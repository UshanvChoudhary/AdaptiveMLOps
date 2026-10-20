FROM python:3.10-slim

# Create a non-root user
RUN useradd -m appuser

WORKDIR /app

# Cache dependencies layer
COPY pyproject.toml /app/
RUN mkdir -p /app/app && touch /app/app/__init__.py &&     pip install --default-timeout=120 --retries=5 -e .

COPY . /app/
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
