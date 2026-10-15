# Architecture

```
                ┌─────────────┐   poll /jobs/{id}   ┌──────────────┐
                │  React Web  ├────────────────────►│   FastAPI    │
                │ (Vite+Tail) │  POST /generate     │  + Postgres  │
                └─────────────┘                     └──────┬───────┘
                                                         │ enqueue
                                                  ┌──────▼───────┐
                                                  │ Celery+Redis │
                                                  └──────┬───────┘
                                                         │ calls
                                                  ┌──────▼───────┐
                                                  │    Solver    │
                                                  │ OR-Tools SAT │
                                                  └──────────────┘
```

## Services (`docker-compose.yml`)

| Service | Image / build | Port | Role |
|---------|---------------|------|------|
| `db` | postgres:16 | 5432 | System of record (inputs, jobs, results) |
| `redis` | redis:7 | 6379 | Celery broker (db 0) + result backend (db 1) |
| `api` | ./apps/api | 8000 | Validation, CRUD, job enqueue, polling |
| `worker` | ./apps/api | — | Runs `solve_timetable`, writes result |
| `web` | ./apps/web | 5173 | Dashboard + grid UI |

## Job lifecycle

1. `POST /api/v1/timetables/generate` validates payload (Pydantic), creates `Job(status=queued)`, enqueues Celery task → `202 { job_id }`.
2. Worker marks `running`, calls `timetable_solver.solve_timetable(input)`.
3. On success: `status=succeeded`, `result_json={assignments, score}`. On error: `status=failed`, `error=...`.
4. Web polls `GET /api/v1/timetables/jobs/{id}` every 2s until terminal state, then renders grid.

No websockets — polling keeps web + API stateless-friendly.

## Key decisions

- **Solver is pure Python** (`packages/solver`) — no DB/network imports, unit-testable standalone.
- **Sync SQLAlchemy engine** in API for simplicity; async optional later.
- **Shared types** in `packages/types` mirror Pydantic schemas manually (codegen optional future).
