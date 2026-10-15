from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    name: str = Field(default="untitled", max_length=200)
    time_limit_seconds: int = Field(default=30, ge=1, le=600)
    teacher_ids: list[str] = Field(default_factory=list)
    batch_ids: list[str] = Field(default_factory=list)
    room_ids: list[str] = Field(default_factory=list)
    subject_ids: list[str] = Field(default_factory=list)
    timeslot_ids: list[str] = Field(default_factory=list)


class JobEnqueued(BaseModel):
    job_id: str
    status: str = "queued"


class JobStatus(BaseModel):
    job_id: str
    status: str
    score: float | None = None
    assignments: list[dict] | None = None
    violations: list[str] | None = None
    error: str | None = None
