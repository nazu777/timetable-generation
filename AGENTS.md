# AGENTS.md — Instructions for AI / Human Agents in this Repo

> Read this file before writing any code. It defines repo conventions, boundaries, and verification steps.

## 1. Repo overview

Monorepo: `timetable-generation`

- `apps/web` — React 18 + TypeScript + Tailwind + Vite. No Next.js. pnpm workspace `@timetable/web`.
- `apps/api` — FastAPI + SQLAlchemy 2.0 + Alembic + Celery + Redis + Postgres. Python 3.11+.
- `packages/solver` — Pure-Python OR-Tools CP-SAT engine (`timetable_solver`). No FastAPI / DB imports here — keep it importable standalone.
- `packages/types` — Shared TypeScript types (must mirror `apps/api/app/schemas/*`).
- `packages/ui` — Shared React presentational components (Tailwind only, no app state).
- `packages/config` — Shared `tsconfig.base.json`, eslint config.
- `docs/` — Human docs. Update docs when you change architecture, API, or solver constraints.

## 2. Default commands (verify every change)

```bash
# JS
pnpm install
pnpm --filter @timetable/web typecheck   # tsc --noEmit
pnpm --filter @timetable/web lint        # eslint
pnpm --filter @timetable/web build

# Python API
cd apps/api
pip install -e ".[dev]"
ruff check app tests
black --check app tests
pytest -q

# Solver
cd packages/solver
pip install -e ".[dev]"
pytest -q
```

Root turbo shortcuts: `pnpm build`, `pnpm lint`, `pnpm typecheck`, `pnpm test`.

Docker sanity: `docker compose up --build -d && curl -f http://localhost:8000/health`.

## 3. Boundaries — DO NOT cross

1. `packages/solver` MUST NOT import from `apps/api`. It receives plain dataclasses (`TimetableInput`) and returns `SolveResult`. No SQLAlchemy, no Celery, no FastAPI.
2. `apps/api` orchestrates: validates (Pydantic) → enqueues Celery task → worker calls `timetable_solver.solve_timetable` → persists JSON result.
3. Frontend MUST NOT hardcode API URLs. Use `VITE_API_URL` (see `apps/web/.env.example`). Poll jobs via `GET /api/v1/timetables/jobs/{id}`, never websockets.
4. DB migrations: every model change needs an Alembic revision (`alembic revision --autogenerate -m "..."`). Never edit applied migrations.
5. Secrets: never commit `.env`. Use `.env.example` as template. Postgres/Redis URLs only via env.

## 4. Code style

- **Python**: Ruff + Black, line-length 100. Type hints everywhere. SQLAlchemy 2.0 style (`Mapped`, `mapped_column`). Pydantic v2 (`BaseModel`, `Field`).
- **TypeScript**: Strict mode. Functional components. `PascalCase` components, `camelCase` hooks/utils. Tailwind for styling — no CSS modules unless necessary.
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`). One logical change per commit.
- **Docs**: If you add an endpoint, constraint, or env var — update `docs/api.md` / `docs/solver.md` / `.env.example` in the same PR.

## 5. Solver rules (packages/solver)

- Hard constraints (must hold or status = `infeasible`):
  - No teacher double-booked in same timeslot.
  - No room double-booked in same timeslot.
  - No batch double-booked in same timeslot.
  - Room capacity >= batch size; room type must allow subject type (e.g. lab).
  - Teacher can only teach qualified subjects; respect `max_periods_per_day`.
  - Fixed assignments (pre-pinned slots) must be honoured.
- Soft preferences (penalties, affect `score` only): teacher time preferences, back-to-back minimisation, room stability.
- `solve_timetable(input, time_limit_seconds=30)` must always return a `SolveResult(status, assignments, score, violations)` — never raise on infeasible; raise only on invalid input (`ValueError`).
- Keep OR-Tools import lazy / optional so unit tests can run with the built-in greedy fallback (see `solver.py`). This keeps CI light; full CP-SAT used when `ortools` installed.

## 6. API rules (apps/api)

- Router prefix: `/api/v1`. Health at `/health` (no prefix).
- Schemas in `app/schemas/`, models in `app/models/`, routes in `app/api/v1/`, Celery tasks in `app/workers/tasks.py`.
- Long-running solve → `202 Accepted { job_id, status: "queued" }`. Never block request on solver.
- Job statuses: `queued → running → succeeded | failed`. Store `result_json` + `error` on completion.
- Pagination: `?skip=0&limit=50` on list endpoints.

## 7. Web rules (apps/web)

- Pages: `Dashboard`, `Inputs` (teachers/rooms/batches), `Generate` (trigger + poll), `TimetableView` (grid). Keep in `src/pages/`.
- API client in `src/lib/api.ts` using `fetch` + `VITE_API_URL`. No axios.
- Shared dumb components go to `packages/ui`; app-specific to `apps/web/src/components`.
- Tailwind config extends theme only — no global CSS hacks.

## 8. Testing expectations

- New solver constraint → add test in `packages/solver/tests/test_solver.py` (feasible + infeasible case).
- New endpoint → add test in `apps/api/tests/` with `httpx` + TestClient.
- New UI flow → ensure `tsc --noEmit` + `vite build` pass. Add Vitest test if logic-heavy.

## 9. PR checklist (agents must self-check)

- [ ] Types pass (`tsc`), lint passes (eslint + ruff), tests pass (pytest + build).
- [ ] `packages/types` and Pydantic schemas still in sync (if API changed).
- [ ] Docs updated (`docs/` + `README.md` if user-facing).
- [ ] No secrets, no `.env`, no `node_modules` / `__pycache__` committed.
- [ ] Docker Compose still boots (`db`, `redis`, `api`, `worker`, `web`).

## 10. Common pitfalls

- Celery broker URL: `redis://redis:6379/0` inside Docker, `redis://localhost:6379/0` locally. Use `CELERY_BROKER_URL` env — don't hardcode.
- SQLAlchemy `DATABASE_URL`: `postgresql+psycopg://...`. Sync engine for API, same URL for Alembic.
- CORS: web dev server `http://localhost:5173` must be in `BACKEND_CORS_ORIGINS`.
- OR-Tools is heavy (~30MB). Keep it optional in `packages/solver` extras (`pip install timetable-solver[ortools]`).
