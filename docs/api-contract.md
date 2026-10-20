# API Contract

## Core Endpoints
- `GET /api/v1/health`: Liveness probe. Returns `{"status": "ok"}`
- `GET /api/v1/ready`: Readiness probe. Checks DB connection. Returns `{"status": "ready", "database": "connected"}` or `not_ready` respectively.
