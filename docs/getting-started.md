# Getting started

## Prerequisites

- Node 20+, pnpm 9
- Python 3.11+
- Docker + Compose (recommended for db/redis)

## Option A — Docker (full stack)

```bash
cp .env.example .env
docker compose up --build
```

- Web: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Option B — Local dev

```bash
# 1. Infra only
docker compose up -d db redis

# 2. API
cd apps/api
python -m venv .venv
# Windows: .venv\Scripts\activate | Mac/Linux: source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 3. Worker (second terminal)
cd apps/api
celery -A app.workers.celery_app.celery_app worker --loglevel=info

# 4. Web (repo root, third terminal)
pnpm install
pnpm --filter @timetable/web dev
# → http://localhost:5173 (VITE_API_URL=http://localhost:8000)
```

## Seed demo data

```bash
cd apps/api
python -m app.seed_demo   # loads 5 teachers, 4 rooms, 2 batches, sample subjects
```

Then open the web app → Generate → Run → watch job go `queued → running → succeeded`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `DATABASE_URL` connection refused | `docker compose up -d db`, check port 5432 free |
| Celery tasks stuck `queued` | worker running? `CELERY_BROKER_URL` matches redis? |
| CORS error in browser | add `http://localhost:5173` to `BACKEND_CORS_ORIGINS` |
| OR-Tools import error | `pip install timetable-solver[ortools]` — greedy fallback still works |
