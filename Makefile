PYTHON ?= python3.13
VENV ?= .venv313

.PHONY: setup run test lint docker-up docker-down

setup:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && pip install -r requirements.txt

run:
	. $(VENV)/bin/activate && uvicorn app.main:app --reload

test:
	. $(VENV)/bin/activate && pytest -q

lint:
	. $(VENV)/bin/activate && python -m compileall app

docker-up:
	docker compose up --build

docker-down:
	docker compose down
