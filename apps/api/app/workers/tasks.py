import json

from app.workers.celery_app import celery_app


@celery_app.task(name="solve_timetable_task", bind=True)
def solve_timetable_task(self, job_id: str, payload: dict) -> dict:
    """Run the solver and persist the result.

    Imports are lazy so the worker image stays lean and unit tests
    don't need a DB/Redis connection.
    """
    from app.core.database import SessionLocal
    from app.models.job import TimetableJob

    db = SessionLocal()
    try:
        job = db.get(TimetableJob, job_id)
        if job is None:
            return {"ok": False, "error": "job not found"}
        job.status = "running"
        db.commit()

        try:
            from timetable_solver import TimetableInput, solve_timetable

            # Minimal demo mapping: real code would hydrate entities from payload ids.
            result = solve_timetable(
                TimetableInput.from_dict(payload),
                time_limit_seconds=int(payload.get("time_limit_seconds", 30)),
            )
            job.status = "succeeded" if result.status != "failed" else "failed"
            job.result_json = json.dumps(
                {
                    "status": result.status,
                    "score": result.score,
                    "assignments": [a.to_dict() for a in result.assignments],
                    "violations": result.violations,
                }
            )
        except Exception as exc:  # keep job row informative
            job.status = "failed"
            job.error = str(exc)
        db.commit()
        return {"ok": True, "job_id": job_id}
    finally:
        db.close()
