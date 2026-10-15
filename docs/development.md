# Development

## JS

```bash
pnpm install
pnpm --filter @timetable/web typecheck
pnpm --filter @timetable/web lint
pnpm --filter @timetable/web build
```

Shared code: `packages/ui` (dumb components), `packages/types` (contracts).

## Python

```bash
cd apps/api
pip install -e ".[dev]"
ruff check app tests
black --check app tests
pytest -q
```

Migrations:

```bash
alembic revision --autogenerate -m "add xyz"
alembic upgrade head
```

## Solver

```bash
cd packages/solver
pip install -e ".[dev]"          # light (greedy fallback)
pip install -e ".[dev,ortools]"  # full CP-SAT
pytest -q
```
