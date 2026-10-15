"""Export helpers (CSV/JSON) for solved timetables."""
from __future__ import annotations

import csv
import io

from timetable_solver.models import Assignment


def to_csv(assignments: list[Assignment]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=["batch_id", "subject_id", "teacher_id", "room_id", "timeslot_id"])
    w.writeheader()
    for a in assignments:
        w.writerow(a.to_dict())
    return buf.getvalue()
