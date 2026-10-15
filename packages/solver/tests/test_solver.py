from timetable_solver import Batch, Room, Subject, Teacher, Timeslot, TimetableInput, solve_timetable


def _basic_input() -> TimetableInput:
    return TimetableInput(
        teachers=[Teacher(id="t1", qualified_subject_ids=["s1", "s2"])],
        subjects=[Subject(id="s1", periods_per_week=2), Subject(id="s2", periods_per_week=1)],
        batches=[Batch(id="b1", size=30)],
        rooms=[Room(id="r1", capacity=40)],
        timeslots=[Timeslot(id="m1", day="Mon"), Timeslot(id="m2", day="Mon"), Timeslot(id="m3", day="Tue")],
    )


def test_feasible():
    result = solve_timetable(_basic_input())
    assert result.status in ("feasible", "optimal")
    assert len(result.assignments) == 3


def test_infeasible_room_capacity():
    inp = _basic_input()
    inp.rooms = [Room(id="tiny", capacity=5)]
    result = solve_timetable(inp)
    assert result.status == "infeasible"
    assert result.violations


def test_invalid_input_raises():
    import pytest

    with pytest.raises(ValueError):
        solve_timetable(TimetableInput())
