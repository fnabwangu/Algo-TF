test:
	pytest -q

lint:
	ruff check .

mypy:
	mypy algo_tf
