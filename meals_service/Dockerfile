# syntax=docker/dockerfile:1

FROM python:3.12-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy meals_service's pyproject (lock is optional at this stage)
COPY meals_service/pyproject.toml ./

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
FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Copy application source
COPY meals_service/meals /app/meals

# Change ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

ENV PYTHONPATH=/app:/app/src

EXPOSE 8004

CMD ["python", "-m", "meals.web.server"]
