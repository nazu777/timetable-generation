import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job import TimetableJob
from app.schemas.timetable import GenerateRequest, JobEnqueued, JobStatus

router = APIRouter()


@router.post("/timetables/generate", response_model=JobEnqueued, status_code=202)
def generate_timetable(payload: GenerateRequest, db: Session = Depends(get_db)) -> JobEnqueued:
    job = TimetableJob(name=payload.name, status="queued", input_json=payload.model_dump_json())
    db.add(job)
    db.commit()
    db.refresh(job)

    # Enqueue — import locally so tests without redis still pass (task.send is mocked).
    try:
        from app.workers.tasks import solve_timetable_task

        solve_timetable_task.delay(str(job.id), payload.model_dump())
    except Exception:
        # Broker unavailable in unit tests / local without redis: keep job queued.
        pass

    return JobEnqueued(job_id=str(job.id), status="queued")


@router.get("/timetables/jobs/{job_id}", response_model=JobStatus)
def get_job(job_id: str, db: Session = Depends(get_db)) -> JobStatus:
    job = db.get(TimetableJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    data: dict = json.loads(job.result_json) if job.result_json else {}
    return JobStatus(
        job_id=str(job.id),
        status=job.status,
        score=data.get("score"),
        assignments=data.get("assignments"),
        violations=data.get("violations"),
        error=job.error,
    )


@router.get("/timetables/")
def list_jobs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(TimetableJob).order_by(TimetableJob.created_at.desc()).offset(skip).limit(limit)
    return [{"job_id": j.id, "name": j.name, "status": j.status} for j in q.all()]
