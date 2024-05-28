lint:
	poetry run isort deltaver tests
	poetry run ruff check deltaver tests --fix
	poetry run mypy deltaver tests

test:
	TZ=UTC poetry run pytest --cov=deltaver --cov-report=term-missing:skip-covered

clean:
	rm -rf .deltaver_cache .mypy_cache .pytest_cache .ruff_cache .coverage dist
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
