# syntax=docker/dockerfile:1

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends curl git && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry

# Allow importing local pkgs
ENV PYTHONPATH=/app:/app/src:/app/movements_service

# Copy CLI project and local editable packages
COPY cli /app/cli
COPY src/alembic-config /app/src/alembic-config
COPY src/shared /app/src/shared
COPY habits_service /app/habits_service
COPY tools/content_parser /app/tools/content_parser
COPY movements_service /app/movements_service

WORKDIR /app/cli

# Install deps with editable local packages
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi

# Default command shows help
CMD ["/bin/sh", "-lc", "mindmirror --help | cat"]


