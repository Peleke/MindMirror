# syntax=docker/dockerfile:1

FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy habits_service's pyproject (lock is optional at this stage)
COPY habits_service/pyproject.toml ./

# Bring in shared package at path expected by pyproject (../src/shared)
COPY ./src/shared /src/shared

# Install deps (create lock inside the image if missing)
# Use BUILD_WITH_DEV=true at build-time to include dev dependencies
ARG BUILD_WITH_DEV=false
RUN poetry config virtualenvs.create false \
    && poetry lock --no-interaction --no-ansi \
    && if [ "$BUILD_WITH_DEV" = "true" ]; then poetry install --no-root --with dev --no-ansi; else poetry install --no-root --only main --no-ansi; fi

# Build shared wheel
WORKDIR /src/shared
RUN poetry build

WORKDIR /app

# Install shared wheel
RUN pip install /src/shared/dist/*.whl

# --- Final Stage ---
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl make

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Copy application source (migrations run separately, not in container)
COPY habits_service/habits /app/habits

ENV PYTHONPATH=/app:/app/src

EXPOSE 8003

CMD ["uvicorn", "habits.app.main:app", "--host", "0.0.0.0", "--port", "8003"]


