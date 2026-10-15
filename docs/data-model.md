# Data model

Postgres (SQLAlchemy 2.0, Alembic). Simplified ER:

```
Teacher (id, name, max_periods_per_day)
Subject (id, name, type[theory|lab], periods_per_week, teacher_ids[])
Batch   (id, name, size)
Room    (id, name, capacity, type[classroom|lab])
Timeslot(id, day, start, end)

TimetableJob (id, status[queued|running|succeeded|failed],
              input_json, result_json, error, created_at, updated_at)
```

## Rules

- `Subject.teacher_ids` = qualified teachers (many-to-many simplified as assoc table in prod).
- `Room.type` must be compatible with `Subject.type` (`lab` subject → `lab` room).
- `Room.capacity >= Batch.size`.
- `TimetableJob.input_json` snapshots the solver input so results are reproducible.
- List endpoints paginate with `?skip=0&limit=50`.

Migrations: `apps/api/alembic/versions/*.py`. Never edit landed revisions.
