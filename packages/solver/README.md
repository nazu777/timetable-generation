# timetable-solver

Pure-Python timetable engine. No FastAPI/DB imports.

```python
from timetable_solver import TimetableInput, solve_timetable
result = solve_timetable(TimetableInput(...))
```

- Full CP-SAT when `pip install timetable-solver[ortools]`
- Deterministic greedy fallback otherwise (CI-light)
