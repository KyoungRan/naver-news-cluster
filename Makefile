# ── 앱 서버 ───────────────────────────────────────────
up:
	docker compose -f docker/app/docker-compose.yml up -d

down:
	docker compose -f docker/app/docker-compose.yml down

build:
	docker compose -f docker/app/docker-compose.yml build --no-cache

logs:
	docker compose -f docker/app/docker-compose.yml logs -f

# ── Langfuse 셀프 호스팅 ──────────────────────────────
langfuse-up:
	docker compose -f docker/langfuse/docker-compose.yml up -d

langfuse-down:
	docker compose -f docker/langfuse/docker-compose.yml down

# ── 로컬 개발 ─────────────────────────────────────────
dev:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	uv run pytest -v --tb=short

lint:
	uv run ruff check .
	uv run mypy app/