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