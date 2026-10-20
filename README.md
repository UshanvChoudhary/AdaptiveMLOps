# AdaptiveMLOps - Phase 0

## Architecture
Phase 0 focuses on establishing a clean, modular foundation for the AdaptiveMLOps project.
The backend is built with FastAPI, SQLAlchemy, and Alembic for robust API and database management. The frontend is built using React, TypeScript, and Vite. PostgreSQL is the chosen database.

## Local Setup

### Prerequisites
- Docker and Docker Compose
- Node.js (for frontend local development)
- Python 3.10+ (for backend local development)

### Environment Variables
Copy `.env.example` to `.env` in the project root:
```bash
cp .env.example .env
```
Ensure the values are suitable for your local setup.

### Starting with Docker
To start the entire stack (PostgreSQL, Backend, Frontend) locally:
```bash
docker-compose up --build
```
- Backend API will be available at http://localhost:8000
- Frontend will be available at http://localhost:3000

### Running Backend Tests
Navigate to the `backend` directory and run:
```bash
cd backend
pip install -e .[test]
pytest
```

### Running Frontend
Navigate to the `frontend` directory and run:
```bash
cd frontend
npm install
npm run dev
```
