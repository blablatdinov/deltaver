lint:
	poetry run isort deltaver tests
	poetry run ruff check deltaver tests --fix
	poetry run mypy deltaver tests

test:
	TZ=UTC poetry run pytest --cov=deltaver --cov-report=term-missing:skip-covered
