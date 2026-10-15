# Timetable Generator: Phase-Wise Implementation Plan

## 0. What the PDF contains

The PDF has **no explicit soft constraints**. It describes the problem data: rooms, semesters, time slots, and weekly LTP loads. These are treated as input data and hard constraints, and the **soft constraints in section 0.3 are proposed** here. Replace them if your guide or department has its own list.

### 0.1 Data extracted from the PDF

| Item | Value |
|---|---|
| Rooms | 30: 22 theory (100s: 102, 103, 104, 106 · 200s: 12 rooms · 400s: 401-408) and 8 labs (LAB-1, LAB-2, 501-504, BSN.LL, Seminar Hall) |
| Sections | 35: Sem 3 has 22, Sem 5 has 7, Sem 7 has 6 |
| Sem 3 | Starts 8:00, lunch 1-2pm, 9 theory periods, 3 lab blocks (8-9:50, 10:20-12:10, 2-3:50), max 1 lab/day |
| Sem 5 | Starts 10:20, lunch 2-3pm, 6 theory periods, 2 lab blocks, max 1 lab/day, Professional Elective (PE) synchronized across all sections |
| Sem 7 | Starts 8:55, lunch 2-3pm, 9 periods, classes only Thu/Fri/Sat, PE and Open Elective (OE) synchronized across all sections |
| Weekly load | Sem 3: 16 theory + 4 labs + tutorials (USP-1, SDM-1) · Sem 5: 14 theory + 5 labs (incl. mini-project) + tutorial (DEV-1) · Sem 7: 12 theory + tutorial (NP-1) |

### 0.2 Things to confirm (inconsistencies found)

1. **Sem 5 lab slot 2:00-3:50** overlaps lunch (2-3pm) and doesn't align with Sem 5's theory periods (2:00-2:55 isn't a Sem 5 period). It may be 2:55-4:45.
2. **Sem 7 theory slot 2:00-2:55** also falls inside its 2-3pm lunch.
3. **"TUTORIAL (2 SLOTS)"**: does this mean the section has 2 tutorial sessions per week in total, or that each tutorial lasts 2 consecutive periods? Assumed the former; the schema supports both.
4. **Working days**: assumed Mon-Sat, since Saturday is clearly a class day for Sem 7.
5. **Lab batches**: are sections split into batches for labs? This matters for feasibility (see 0.4).
6. **Not in the PDF but required**: faculty list, subject-to-faculty-to-section mapping, section strengths, room capacities, lab-to-subject compatibility, and full names of the subject codes.

### 0.3 Constraints

**Hard constraints (a timetable is invalid if any is violated)**

| ID | Constraint |
|---|---|
| H1 | Every required session (per the LTP table) is scheduled exactly the required number of times. |
| H2 | A section has at most one session at a time. |
| H3 | A faculty member has at most one session at a time. |
| H4 | A room has at most one session at a time. |
| H5 | Room type matches the session: theory and tutorial go in theory rooms, labs go in lab rooms. |
| H6 | Sessions use only the slots allowed for that semester: no classes before its start time and none during lunch. |
| H7 | A lab is one contiguous 2-period block taken from the semester's lab slots, with at most one lab per section per day. |
| H8 | Sem 7 is scheduled only on Thu/Fri/Sat. |
| H9 | PE and OE sessions are synchronized: all sections of the semester have them in the same slots. Each elective course needs its own room and faculty at that time. |
| H10 | Room capacity is at least the section strength. |
| H11 | A section has at most one session of the same subject per day. |
| H12 | Faculty unavailability (leave, other duties) and pre-fixed or locked sessions are respected. |
| H13 | A lab session uses a lab room compatible with its subject. |
| H14 | A faculty member's daily teaching hours stay under a hard cap (for example 6). |

**Soft constraints (proposed, each with a weight)**

| ID | Constraint |
|---|---|
| S1 | Minimize idle gaps in a section's day. |
| S2 | Spread each subject's sessions evenly across the week, avoiding consecutive days where possible. |
| S3 | Balance daily load per section (target 4-6 periods, avoid days with 1-2 periods). |
| S4 | Minimize faculty gaps and more than 3 consecutive teaching periods. |
| S5 | Respect faculty preferred days and slots. |
| S6 | Keep a section in a "home room" for theory, and minimize room changes. |
| S7 | Keep consecutive classes in the same block (100s/200s/400s) to reduce walking. |
| S8 | Avoid placing heavy theory subjects in the first or last period. |
| S9 | Keep Saturday lighter. |
| S10 | Avoid a lab and the same subject's theory on the same day. |
| S11 | Prefer labs after theory-heavy mornings, or follow whatever lab-timing rule your department has. |

### 0.4 Feasibility numbers (to verify in Phase 1)

- **Theory rooms:** about 520 weekly theory-room-periods are needed against roughly 1,200+ available. Total utilization is about 40%, but midday is the pinch point. From 10:20 to 1:05 all of Sem 3 and Sem 5 are in session, which is 29 sections for 22 rooms on Mon-Wed. On Thu-Sat all 35 sections compete for 22 rooms. Rooms therefore **cannot** be permanently assigned one per section.
- **Lab rooms:** Sem 3 needs 22 x 4 = 88 lab sessions and Sem 5 needs 7 x 5 = 35, so 123 in total. Capacity is 8 rooms x 3 blocks x 6 days = 144. That is about **85% utilization, and it becomes infeasible if labs run in batches.**

### 0.5 Algorithm strategy

Your PDF lists CSP, GA, and Hybrid GA-CSP. Plan to implement all three and compare them:

- **CSP** builds a hard-feasible schedule with MRV/degree heuristics, forward checking, and backtracking.
- **GA** evolves schedules against the soft-constraint cost function.
- **Hybrid GA-CSP** is what you'll likely end up using. CSP generates the initial population and repairs offspring, and the GA optimizes soft constraints.
- **Benchmark (optional):** OR-Tools CP-SAT gives a reference solution to compare against.

### 0.6 System architecture

```
┌────────────┐   REST    ┌──────────────────────────┐
│ React UI   │◄────────►│ FastAPI backend          │
│ (admin +   │           │  ├ routers (CRUD, solve) │
│ timetable  │           │  ├ services              │
│ views)     │           │  └ job queue (RQ/Celery) │
└────────────┘           └────────┬─────────────────┘
                                  │
        ┌─────────────────────────┼───────────────────────┐
        ▼                         ▼                       ▼
 ┌─────────────┐        ┌──────────────────┐     ┌──────────────┐
 │ PostgreSQL  │        │ Solver engine    │     │ Exporter     │
 │ (SQLite dev)│        │ model/constraints│     │ PDF/XLSX/CSV │
 └─────────────┘        │ csp / ga / hybrid│     └──────────────┘
                        └──────────────────┘
```

**Stack:** Python 3.11, FastAPI, SQLAlchemy and Alembic, NumPy, DEAP or a custom GA, OR-Tools (benchmark), Redis for jobs, React for the UI, and pytest.

**Repo layout:**

```
timetable/
├── app/api/          # routers
├── app/db/           # models.py, session.py, migrations/
├── app/engine/
│   ├── model.py          # Session, Slot, Assignment dataclasses
│   ├── constraints/      # hard.py, soft.py, registry.py
│   ├── csp.py  ga.py  hybrid.py  cpsat_ref.py
│   ├── fitness.py  repair.py  explain.py
├── app/ingest/       # loaders, validators, feasibility.py
├── app/export/
├── tests/
└── data/seed/        # rooms.csv, sections.csv, ltp.csv, slots.csv
```

### 0.7 Database schema (PostgreSQL)

```sql
-- Static master data
CREATE TABLE semester (
  id SERIAL PRIMARY KEY, number INT UNIQUE,            -- 3,5,7
  day_start TIME, lunch_start TIME, lunch_end TIME,
  max_labs_per_day INT DEFAULT 1
);
CREATE TABLE semester_day (                              -- 7th sem: Thu-Sat only
  semester_id INT REFERENCES semester, weekday SMALLINT, PRIMARY KEY(semester_id, weekday)
);
CREATE TABLE section (
  id SERIAL PRIMARY KEY, semester_id INT REFERENCES semester,
  name TEXT, strength INT, home_room_id INT NULL, UNIQUE(semester_id, name)
);
CREATE TABLE room (
  id SERIAL PRIMARY KEY, code TEXT UNIQUE, block TEXT,   -- '100s','200s','400s','LAB'
  type TEXT CHECK (type IN ('THEORY','LAB')), capacity INT
);
CREATE TABLE subject (
  id SERIAL PRIMARY KEY, code TEXT UNIQUE, name TEXT,
  kind TEXT CHECK (kind IN ('CORE','PE','OE','PROJECT','MC'))
);
CREATE TABLE faculty (
  id SERIAL PRIMARY KEY, name TEXT, max_hours_per_day INT DEFAULT 6,
  max_hours_per_week INT
);

-- Time model
CREATE TABLE period (                                    -- atomic teaching period
  id SERIAL PRIMARY KEY, semester_id INT REFERENCES semester,
  idx INT, start_time TIME, end_time TIME, UNIQUE(semester_id, idx)
);
CREATE TABLE slot (                                      -- schedulable unit (day x period or lab block)
  id SERIAL PRIMARY KEY, semester_id INT REFERENCES semester,
  weekday SMALLINT, kind TEXT CHECK (kind IN ('THEORY','LAB')),
  start_period_id INT REFERENCES period, span INT DEFAULT 1  -- lab span = 2
);

-- Curriculum (LTP)
CREATE TABLE course_offering (                           -- subject taught in a semester
  id SERIAL PRIMARY KEY, subject_id INT REFERENCES subject,
  semester_id INT REFERENCES semester,
  theory_slots INT DEFAULT 0, tutorial_slots INT DEFAULT 0, lab_slots INT DEFAULT 0,
  tutorial_span INT DEFAULT 1, sync_group TEXT NULL      -- 'S5_PE','S7_PE','S7_OE'
);
CREATE TABLE teaching_assignment (                       -- who teaches what to whom
  id SERIAL PRIMARY KEY, offering_id INT REFERENCES course_offering,
  section_id INT REFERENCES section, faculty_id INT REFERENCES faculty,
  component TEXT CHECK (component IN ('THEORY','TUTORIAL','LAB'))
);
CREATE TABLE lab_room_compat (subject_id INT, room_id INT, PRIMARY KEY(subject_id, room_id));

-- Constraints data
CREATE TABLE faculty_unavailability (faculty_id INT, slot_id INT, reason TEXT);
CREATE TABLE faculty_preference (faculty_id INT, slot_id INT, weight INT);  -- +ve prefer, -ve avoid
CREATE TABLE locked_session (teaching_assignment_id INT, slot_id INT, room_id INT);
CREATE TABLE constraint_config (code TEXT PRIMARY KEY, kind TEXT, enabled BOOL, weight INT);

-- Output
CREATE TABLE timetable_run (
  id SERIAL PRIMARY KEY, algorithm TEXT, params JSONB, seed INT,
  status TEXT, hard_violations INT, soft_cost NUMERIC, runtime_s NUMERIC,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE schedule_entry (
  run_id INT REFERENCES timetable_run, teaching_assignment_id INT,
  slot_id INT, room_id INT,
  PRIMARY KEY (run_id, teaching_assignment_id, slot_id)
);
CREATE INDEX ON schedule_entry (run_id, slot_id, room_id);
```

`course_offering.sync_group` handles PE and OE synchronization. Because `timetable_run` stores the seed and params, every run is reproducible.

### 0.8 Core in-memory representation (used by all algorithms)

- **Event** is one required session: `(event_id, section_id, subject_id, faculty_id, component, span, sync_group)`. It is built from `teaching_assignment x slot counts`.
- **Variable** is `(slot_id, room_id)` per event. The domain is pre-filtered by H5, H6, H8, H10, H12, and H13.
- **Chromosome** (GA) is an array of `(slot_idx, room_idx)` of length N events.
- **Sync groups** are collapsed into one variable, so H9 is satisfied by construction.
- **Occupancy tensors** (booleans for section, faculty, and room by slot) give O(1) clash checks.

---

## Phase 1: Data layer and ingestion

**Goal:** all PDF data is in the DB and validated.

- Alembic migrations for the schema above.
- Seed loaders from CSV/Excel.
- `generate_periods_and_slots(semester)`: builds periods, theory slots, and lab blocks from the PDF.
- `validate_data()`: checks that periods and lab blocks don't overlap lunch, every teaching assignment has a faculty, and every section has all its LTP components. This is where the Sem 5 and Sem 7 slot inconsistencies from 0.2 should surface.
- `feasibility_report()`: computes theory-room and lab-room utilization (overall and per peak period), per-faculty weekly load, and per-section slot-demand versus capacity. It should fail early if the lab arithmetic is infeasible.

**Exit criteria:** `feasibility_report` runs clean on the real data.

## Phase 2: Domain model and constraint engine

**Goal:** a trusted referee that scores any timetable.

```python
build_events(db) -> list[Event]
build_domains(events, slots, rooms) -> dict[event_id, list[(slot_id, room_id)]]
class Timetable:  assign(e, slot, room); unassign(e); clone(); to_entries()
hard_violations(tt) -> dict[str, list[Violation]]   # one fn per H1-H14
soft_cost(tt, weights) -> (total, per_constraint_breakdown)
delta_cost(tt, move)  # incremental evaluation for speed
explain(tt) -> human-readable violation report
```

- Register constraints in `registry.py`, so each has a code, a function, a weight, and an on/off flag from `constraint_config`.
- Write unit tests with hand-built tiny timetables that violate each constraint exactly once.

**Exit criteria:** 100% test coverage on constraints.

## Phase 3: CSP solver (baseline)

**Goal:** a hard-feasible timetable.

```python
solve_csp(events, domains, heuristics) -> Timetable | None
select_variable(...)      # MRV, then degree; labs and sync groups first
order_values(...)         # least-constraining value, plus soft-cost tiebreak
forward_check(assign, e, v) -> bool
backtrack(...)            # with limited discrepancy search and restarts
```

- Place in this order: sync groups (PE/OE), then labs, then theory and tutorials, because labs and electives are the tightest.
- Use AC-3 pre-pruning on domains.
- Add restarts with randomized tie-breaking and a time limit.

**Exit criteria:** zero hard violations for all 35 sections, in under a few minutes.

## Phase 4: Genetic algorithm

**Goal:** optimize soft constraints.

```python
init_population(n, mode="random"|"csp_seeded")
fitness(ind) = -(1e4*hard_violations + soft_cost)
select(pop)               # tournament
crossover_section(a, b)   # swap whole-section schedules (keeps intra-section integrity)
crossover_day(a, b)
mutate_swap_slots(ind)    # swap two events' slots
mutate_move_room(ind)
mutate_shift_day(ind)
repair(ind)               # fix clashes greedily
run_ga(params) -> Timetable
```

- Use elitism and adaptive mutation. Log per-generation fitness, plus hard violations and soft cost separately.
- Tune population size, mutation rate, and constraint weights using stored `timetable_run` rows.

## Phase 5: Hybrid GA-CSP

**Goal:** the best of both.

```python
seed_population_with_csp(n)       # diverse CSP solutions via randomized value ordering
csp_repair(ind)                   # unassign violating events, re-solve locally with CSP
ga_with_csp_repair(params)
local_search(tt)                  # hill-climb / simulated annealing on soft cost
```

- Offspring that break hard constraints are repaired by CSP instead of being discarded.
- Add a final LNS (Large Neighbourhood Search) step: free one day or section and re-optimize.

## Phase 6: Tuning and benchmarking

- `compare_algorithms(seeds)` runs CSP, GA, Hybrid, and optionally CP-SAT, and reports hard violations, soft cost (with per-constraint breakdown), runtime, and success rate over N seeds.
- A weight-tuning study, with sensitivity analysis.
- Charts: convergence curves and soft-cost bar charts. These make good project-report material.

## Phase 7: API, UI, export

**Endpoints:**

```
POST /runs {algorithm, params}   GET /runs/{id}   GET /runs/{id}/violations
GET /timetable/section/{id}      GET /timetable/faculty/{id}      GET /timetable/room/{id}
PUT /constraints/{code}          POST /locks    POST /runs/{id}/repair
```

- **Web UI:** admin forms for master data, a constraint weight editor, a run launcher with live progress, grid views by section, faculty, and room, drag-and-drop manual edits with live violation highlighting, and manual locks followed by a partial re-solve.
- **Export:** PDF and Excel per section, faculty, and room, plus a master sheet.

## Phase 8: Testing, hardening, documentation

- Property tests: any output must pass `hard_violations == 0`.
- Stress tests: faculty unavailability, locked sessions, and an extra section.
- Reproducibility test: same seed gives the same output.
- Dockerize, write a README, and document the algorithm design and results for your report.

---

## Suggested order and effort

| Phase | Rough effort |
|---|---|
| 0-1 | 1 week |
| 2 | 1 week |
| 3 | 1-2 weeks |
| 4 | 1-2 weeks |
| 5 | 1-2 weeks |
| 6-8 | 2-3 weeks |

## Next steps

Answer the Phase 0.2 questions, especially lab batches, the meaning of "tutorial (2 slots)", and the faculty and subject-mapping data. With the faculty and subject-code details, the seed CSV templates and the Phase 1 and Phase 2 code skeleton can be generated.