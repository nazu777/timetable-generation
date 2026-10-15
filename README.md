# Timetable Generation

> Automated, constraint-based timetable scheduling platform — React + FastAPI monorepo.

Generate conflict-free class timetables for schools / colleges / universities with rooms, faculty, batches, and time-slot constraints. A CP-SAT (OR-Tools) solver runs async via Celery + Redis, persists to Postgres, and serves results through FastAPI to a React UI.

## ✨ Features

- **Constraint solver** (`packages/solver`) — OR-Tools CP-SAT skeleton: no teacher/room/batch clashes, workload limits, room capacity/type matching, fixed slots, preferences (soft).
- **Async jobs** — FastAPI enqueues generation jobs → Celery worker + Redis broker → Postgres stores job + result.
- **Modern UI** (`apps/web`) — React 18 + TypeScript + TailwindCSS + Vite: dashboard, inputs, timetable grid, job status polling.
- **Typed contracts** (`packages/types`) — shared TS types mirroring Pydantic schemas.
- **DevOps ready** — Docker Compose (api, worker, web, db, redis), GitHub Actions CI, Alembic migrations.

## 🧱 Monorepo layout

```
timetable-generation/
├── apps/
│   ├── web/              # React + TS + Tailwind (Vite)
│   └── api/              # FastAPI + SQLAlchemy + Celery
├── packages/
│   ├── solver/           # OR-Tools timetable engine (Python)
│   ├── types/            # Shared TypeScript types
│   ├── ui/               # Shared React components
│   └── config/           # Shared tsconfig / eslint
├── docs/                 # Architecture, API, solver, deployment
├── .github/workflows/    # CI
├── docker-compose.yml
├── turbo.json
├── pnpm-workspace.yaml
└── AGENTS.md             # Agent / contributor instructions
```

## 🚀 Quickstart

### 1. Prerequisites

- Node 20+ + pnpm 9 (`npm i -g pnpm`)
- Python 3.11+ + uv (or pip)
- Docker + Docker Compose (for Postgres + Redis)

### 2. Clone + env

```bash
git clone https://github.com/<you>/timetable-generation.git
cd timetable-generation
cp .env.example .env
```

### 3. Full stack via Docker (easiest)

```bash
docker compose up --build
# web → http://localhost:5173
# api → http://localhost:8000/docs
```

### 4. Local dev (without Docker for app code)

```bash
# Postgres + Redis only
docker compose up -d db redis

# API
cd apps/api
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]          # or: pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Celery worker (new terminal)
celery -A app.workers.celery_app.celery_app worker --loglevel=info

# Web (new terminal, repo root)
pnpm install
pnpm --filter @timetable/web dev
```

See [`docs/getting-started.md`](docs/getting-started.md) for details.

## 🔌 API sketch

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/health` | Liveness |
| `POST` | `/api/v1/timetables/generate` | Enqueue generation job → `{ job_id }` |
| `GET` | `/api/v1/timetables/jobs/{job_id}` | Poll job status + result |
| `GET` | `/api/v1/timetables/` | List generated timetables |
| `CRUD` | `/api/v1/{teachers,rooms,batches,subjects,timeslots}` | Manage inputs |

Full spec: [`docs/api.md`](docs/api.md) + live Swagger at `/docs`.

## 🧠 Solver sketch

Input: teachers, subjects, batches, rooms, timeslots + constraints.
Output: assignments `(batch, subject, teacher, room, timeslot)` with zero hard-conflicts.

```python
from timetable_solver import TimetableInput, solve_timetable
result = solve_timetable(TimetableInput(...))
print(result.status, result.assignments)
```

Details: [`docs/solver.md`](docs/solver.md) · Code: [`packages/solver/`](packages/solver/).

## 🛠️ Common commands

```bash
pnpm install          # install JS workspaces
pnpm dev              # turbo: run all dev tasks
pnpm build            # turbo: build all
make api-test         # pytest apps/api + solver
make lint             # eslint + ruff
docker compose up --build
```

## 📚 Docs

- [`docs/architecture.md`](docs/architecture.md) — system design + diagrams
- [`docs/data-model.md`](docs/data-model.md) — ER model
- [`docs/solver.md`](docs/solver.md) — constraint model
- [`docs/deployment.md`](docs/deployment.md) — Docker / prod notes
- [`AGENTS.md`](AGENTS.md) — how agents should work in this repo

## 🤝 Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Conventional Commits, PRs must pass CI.

## 📄 License

MIT — see [`LICENSE`](LICENSE).
