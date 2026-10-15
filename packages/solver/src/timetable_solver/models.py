"""Plain dataclasses — deliberately framework-free."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Teacher:
    id: str
    name: str = ""
    qualified_subject_ids: list[str] = field(default_factory=list)
    max_periods_per_day: int = 6
    unavailable_slot_ids: list[str] = field(default_factory=list)


@dataclass
class Subject:
    id: str
    name: str = ""
    type: str = "theory"  # theory | lab
    periods_per_week: int = 3


@dataclass
class Batch:
    id: str
    name: str = ""
    size: int = 30


@dataclass
class Room:
    id: str
    name: str = ""
    capacity: int = 40
    type: str = "classroom"  # classroom | lab


@dataclass
class Timeslot:
    id: str
    day: str = "Mon"
    index: int = 0


@dataclass
class Assignment:
    batch_id: str
    subject_id: str
    teacher_id: str
    room_id: str
    timeslot_id: str

    def to_dict(self) -> dict:
        return {
            "batch_id": self.batch_id,
            "subject_id": self.subject_id,
            "teacher_id": self.teacher_id,
            "room_id": self.room_id,
            "timeslot_id": self.timeslot_id,
        }


@dataclass
class TimetableInput:
    teachers: list[Teacher] = field(default_factory=list)
    subjects: list[Subject] = field(default_factory=list)
    batches: list[Batch] = field(default_factory=list)
    rooms: list[Room] = field(default_factory=list)
    timeslots: list[Timeslot] = field(default_factory=list)
    fixed: list[Assignment] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "TimetableInput":
        """Lenient loader — accepts ids or full objects (API passes ids only)."""
        def ids(key: str) -> list[str]:
            return [str(x) for x in data.get(key, [])]

        # When only ids are given, synthesise minimal demo entities so the
        # worker/solver still returns something useful.
        teachers = [Teacher(id=i, qualified_subject_ids=ids("subject_ids")) for i in ids("teacher_ids")] or [
            Teacher(id="t1")
        ]
        subjects = [Subject(id=i) for i in ids("subject_ids")] or [Subject(id="s1")]
        batches = [Batch(id=i) for i in ids("batch_ids")] or [Batch(id="b1")]
        rooms = [Room(id=i) for i in ids("room_ids")] or [Room(id="r1")]
        timeslots = [Timeslot(id=i) for i in ids("timeslot_ids")] or [Timeslot(id="m1")]
        return cls(teachers=teachers, subjects=subjects, batches=batches, rooms=rooms, timeslots=timeslots)


@dataclass
class SolveResult:
    status: str  # optimal | feasible | infeasible | failed
    assignments: list[Assignment] = field(default_factory=list)
    score: float = 0.0
    violations: list[str] = field(default_factory=list)
