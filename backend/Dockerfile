FROM python:3.10-slim

# Create a non-root user
RUN useradd -m appuser

WORKDIR /app

COPY pyproject.toml /app/
RUN pip install -e .

COPY . /app/

# Switch to non-root user
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
