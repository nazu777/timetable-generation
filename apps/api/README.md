# Timetable API

FastAPI + SQLAlchemy + Celery + Postgres + Redis.

## Run

```bash
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```
