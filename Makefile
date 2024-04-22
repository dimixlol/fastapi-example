LDE_VOLUME ?= "./:/app"
ADDITIONAL_UVICORN_CMD ?= "--reload"

install:
	@pip install pipenv==2023.6.12
	@pipenv install --dev

lint:
	@black src --check --diff
	@isort src -c
	@pylint src

format:
	@black src
	@isort src

migrate:
	@alembic upgrade head

dev:
	@LDE_VOLUME=$(LDE_VOLUME) ADDITIONAL_UVICORN_CMD=$(ADDITIONAL_UVICORN_CMD) docker compose up -d

run:
	@docker compose up -d

stop:
	@LDE_VOLUME=$(LDE_VOLUME) ADDITIONAL_UVICORN_CMD=$(ADDITIONAL_UVICORN_CMD) docker compose down
