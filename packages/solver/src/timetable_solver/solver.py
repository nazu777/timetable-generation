"""Solver entrypoint: CP-SAT when ortools present, greedy fallback otherwise."""
from __future__ import annotations

from timetable_solver.models import Assignment, SolveResult, TimetableInput


def solve_timetable(input: TimetableInput, time_limit_seconds: int = 30) -> SolveResult:
    if not input.teachers or not input.subjects or not input.batches:
        raise ValueError("teachers, subjects and batches must be non-empty")
    if not input.rooms or not input.timeslots:
        raise ValueError("rooms and timeslots must be non-empty")

    try:
        import ortools  # noqa: F401
        from timetable_solver import cpsat as _cpsat

        return _cpsat.solve_with_cpsat(input, time_limit_seconds=time_limit_seconds)
    except ImportError:
        return _solve_greedy(input)


def _room_ok(room_type: str, subject_type: str, capacity: int, batch_size: int) -> bool:
    if capacity < batch_size:
        return False
    if subject_type == "lab" and room_type != "lab":
        return False
    return True


def _solve_greedy(input: TimetableInput) -> SolveResult:
    used_teacher: set[tuple[str, str]] = set()
    used_room: set[tuple[str, str]] = set()
    used_batch: set[tuple[str, str]] = set()
    per_teacher_day: dict[tuple[str, str], int] = {}
    assignments: list[Assignment] = []

    # Pin fixed assignments first.
    for f in input.fixed:
        assignments.append(f)
        used_teacher.add((f.teacher_id, f.timeslot_id))
        used_room.add((f.room_id, f.timeslot_id))
        used_batch.add((f.batch_id, f.timeslot_id))

    for batch in input.batches:
        for subject in input.subjects:
            for _ in range(subject.periods_per_week):
                placed = False
                for slot in input.timeslots:
                    if (batch.id, slot.id) in used_batch:
                        continue
                    for teacher in input.teachers:
                        if subject.id not in teacher.qualified_subject_ids and teacher.qualified_subject_ids:
                            continue
                        if (teacher.id, slot.id) in used_teacher:
                            continue
                        if per_teacher_day.get((teacher.id, slot.day), 0) >= teacher.max_periods_per_day:
                            continue
                        for room in input.rooms:
                            if not _room_ok(room.type, subject.type, room.capacity, batch.size):
                                continue
                            if (room.id, slot.id) in used_room:
                                continue
                            assignments.append(
                                Assignment(batch.id, subject.id, teacher.id, room.id, slot.id)
                            )
                            used_teacher.add((teacher.id, slot.id))
                            used_room.add((room.id, slot.id))
                            used_batch.add((batch.id, slot.id))
                            per_teacher_day[(teacher.id, slot.day)] = (
                                per_teacher_day.get((teacher.id, slot.day), 0) + 1
                            )
                            placed = True
                            break
                        if placed:
                            break
                    if placed:
                        break
                if not placed:
                    return SolveResult(
                        status="infeasible",
                        assignments=assignments,
                        score=0.0,
                        violations=[f"could not place {batch.id}/{subject.id}"],
                    )
    return SolveResult(status="feasible", assignments=assignments, score=75.0, violations=[])
