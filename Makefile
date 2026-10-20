.PHONY: help setup test run-local build-docker

help:
	@echo "AdaptiveMLOps Makefile"
	@echo "Available targets:"
	@echo "  setup       - Install backend and frontend dependencies locally"
	@echo "  test        - Run backend tests"
	@echo "  run-local   - Run backend and frontend locally (without Docker)"
	@echo "  build-docker- Build Docker images"
	@echo "  up          - Run Docker Compose up"
	@echo "  down        - Run Docker Compose down"

setup:
	cd backend && pip install -e .[test]
	cd frontend && npm install

test:
	cd backend && pytest

run-backend:
	cd backend && uvicorn app.main:app --reload

run-frontend:
	cd frontend && npm run dev

build-docker:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down
