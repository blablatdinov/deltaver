lint:
	poetry run isort deltaver tests
	poetry run ruff check deltaver tests
	poetry run mypy deltaver tests

test:
	poetry run pytest --cov=deltaver --cov-report=term-missing:skip-covered
