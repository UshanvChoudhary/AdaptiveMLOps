# Demo Script

## Phase 0

1. `docker-compose up -d --build`
2. Open `http://localhost:8000/api/v1/health` to verify API liveness.
3. Open `http://localhost:8000/api/v1/ready` to verify API readiness (DB connection).
4. Open `http://localhost:3000` to verify frontend application loads.
