# Solver — constraint model

Engine: `packages/solver` (`timetable_solver.solve_timetable`).

## Inputs

`TimetableInput`: teachers (+`qualified_subject_ids`, `max_periods_per_day`, `unavailable_slot_ids`),
subjects (`periods_per_week`, `type`), batches (`size`), rooms (`capacity`, `type`),
timeslots (`day`, `index`), fixed assignments, `time_limit_seconds`.

## Hard constraints (infeasible if violated)

1. Each timeslot: teacher ≤ 1 class, room ≤ 1 class, batch ≤ 1 class.
2. `room.capacity >= batch.size`.
3. `room.type` compatible: `lab` subject needs `lab` room; `theory` fits any.
4. Teacher qualified: `subject.id ∈ teacher.qualified_subject_ids`.
5. `max_periods_per_day` per teacher.
6. Fixed assignments pinned exactly.

## Soft objectives (affect `score`, not feasibility)

- Teacher time preferences (avoid `unavailable` / penalise undesired).
- Minimise back-to-back overload (spread `periods_per_week` across days).
- Room stability (same batch+subject → same room).

## Implementation

- **CP-SAT** when `ortools` installed (binary `x[(batch,subject,teacher,room,slot)]`, all-different style constraints, linearised soft penalties).
- **Greedy fallback** otherwise (deterministic, respects all hard constraints, used in CI-light envs).
- `solve_timetable` never raises on infeasible — returns `SolveResult(status="infeasible", violations=[...])`. Raises `ValueError` only on invalid input.

## Tuning

- Increase `time_limit_seconds` (default 30) for large instances (> 200 sessions/week).
- If `infeasible`, inspect `violations` — typically room capacity or teacher overload. Add rooms/slots or relax fixed pins.
