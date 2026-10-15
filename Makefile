# Timetable Generation — dev shortcuts (works on Windows Git Bash / WSL / Linux / macOS)

.PHONY: install dev build lint typecheck api-install api-test api-lint solver-test web-dev docker-up docker-down

install:
	pnpm install

dev:
	pnpm dev

build:
	pnpm build

lint:
	pnpm lint

typecheck:
	pnpm typecheck

api-install:
	cd apps/api && pip install -e ".[dev]"

api-test:
	cd apps/api && pytest -q

api-lint:
	cd apps/api && ruff check app tests && black --check app tests

solver-test:
	cd packages/solver && pip install -e ".[dev]" && pytest -q

web-dev:
	pnpm --filter @timetable/web dev

docker-up:
	docker compose up --build

docker-down:
	docker compose down
