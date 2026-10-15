# API reference

Base URL: `VITE_API_URL` (dev: `http://localhost:8000`). Interactive docs: `/docs`.

## Health

`GET /health` → `{"status":"ok"}` (no `/api/v1` prefix).

## Timetables

### Enqueue generation

`POST /api/v1/timetables/generate` → `202 Accepted`

```json
{
  "name": "CSE Sem 3",
  "time_limit_seconds": 30,
  "teacher_ids": ["t1","t2"],
  "batch_ids": ["b1"],
  "room_ids": ["r1","r2"],
  "subject_ids": ["s1","s2"],
  "timeslot_ids": ["m1","m2","m3"]
}
```

Response: `{ "job_id": "uuid", "status": "queued" }`

### Poll job

`GET /api/v1/timetables/jobs/{job_id}` → `200`

```json
{
  "job_id": "uuid",
  "status": "succeeded",
  "score": 87.5,
  "assignments": [
    {"batch_id":"b1","subject_id":"s1","teacher_id":"t1","room_id":"r1","timeslot_id":"m1"}
  ],
  "violations": [],
  "error": null
}
```

### List timetables

`GET /api/v1/timetables/?skip=0&limit=50`

## CRUD inputs

`GET|POST /api/v1/teachers/`, `/rooms/`, `/batches/`, `/subjects/`, `/timeslots/`
`GET|PATCH|DELETE /api/v1/teachers/{id}` (same pattern for others).

All mutating schemas are Pydantic v2 (`app/schemas/`). TS mirrors in `packages/types`.
