"""Hard-constraint helpers (used by cpsat.py and documented in docs/solver.md)."""
from timetable_solver.models import Room


def room_fits_subject(room: Room, subject_type: str, batch_size: int) -> bool:
    if room.capacity < batch_size:
        return False
    if subject_type == "lab" and room.type != "lab":
        return False
    return True
