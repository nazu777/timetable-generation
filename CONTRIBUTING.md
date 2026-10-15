# Contributing

Thanks for contributing! Quick rules:

1. **Setup** — see `docs/getting-started.md`. Use `cp .env.example .env`, never commit `.env`.
2. **Branches** — `feat/<short-name>`, `fix/<short-name>`, `docs/<short-name>`.
3. **Commits** — Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`.
4. **Before pushing**:
   - `pnpm typecheck && pnpm lint && pnpm build` (JS)
   - `cd apps/api && pytest -q && ruff check app tests` (API)
   - `cd packages/solver && pytest -q` (solver)
5. **Docs** — endpoint/constraint/env change → update `docs/` in the same PR.
6. **Migrations** — model change → `alembic revision --autogenerate`, never edit landed migrations.
7. **Types** — keep `packages/types` in sync with Pydantic schemas.

Questions? Open a discussion / issue first for large changes.
