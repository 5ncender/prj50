COMPOSE := docker compose -f docker-compose.dev.yml

.PHONY: setup db-up db-down db-reset db-shell migrate doctor test lint fmt

setup:            ## 의존성 설치 + .env 생성(없을 때만)
	uv sync
	@test -f .env || cp .env.example .env

db-up:            ## 개발용 Postgres 기동 (준비될 때까지 대기)
	$(COMPOSE) up -d --wait

db-down:          ## 개발용 Postgres 중지 (데이터 유지)
	$(COMPOSE) down

db-reset:         ## 개발용 DB 데이터 삭제 후 재생성
	$(COMPOSE) down -v
	$(MAKE) db-up migrate

db-shell:         ## psql 접속
	$(COMPOSE) exec postgres psql -U invest invest

migrate:          ## 스키마를 최신으로
	uv run alembic upgrade head

doctor:           ## 설정·연결 점검
	uv run invest doctor

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

fmt:
	uv run ruff check --fix .
	uv run ruff format .
