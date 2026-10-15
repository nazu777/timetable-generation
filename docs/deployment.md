# Deployment

## Docker Compose (single host)

```bash
cp .env.example .env   # set SECRET_KEY, passwords
docker compose up --build -d
curl -f http://localhost:8000/health
```

Services: `db`, `redis`, `api`, `worker`, `web`. Scale workers: `docker compose up -d --scale worker=3`.

## Production checklist

- [ ] `SECRET_KEY`, `POSTGRES_PASSWORD` from vault, not `.env.example` values.
- [ ] `BACKEND_CORS_ORIGINS` = real frontend origin(s) only.
- [ ] Postgres volume backed up; `pgdata` on persistent disk.
- [ ] Redis persistence (`appendonly yes`) if job durability matters.
- [ ] `SOLVER_TIME_LIMIT_SECONDS` sized to worker memory/CPU.
- [ ] API behind TLS reverse proxy (Caddy/Nginx); `/docs` disabled or protected.
- [ ] CI green on `main`; images tagged by SHA.

## Env vars (see `.env.example`)

`DATABASE_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `BACKEND_CORS_ORIGINS`, `VITE_API_URL`, `SOLVER_TIME_LIMIT_SECONDS`.
