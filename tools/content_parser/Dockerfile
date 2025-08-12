# syntax=docker/dockerfile:1

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for poetry
RUN apt-get update && apt-get install -y --no-install-recommends curl git && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry

# Ensure package imports from /app without installation
ENV PYTHONPATH=/app

# Build arg: if set to false, we will bootstrap pyproject and deps inside the container
ARG USE_LOCAL_PYPROJECT=true

# Copy project files (if present). We copy everything under tools/content_parser
COPY . /app

# Install deps via poetry
RUN if [ "$USE_LOCAL_PYPROJECT" = "true" ] && [ -f "/app/pyproject.toml" ]; then \
      poetry config virtualenvs.create false && \
      poetry install --no-interaction --no-ansi --no-root; \
    else \
      poetry config virtualenvs.create false && \
      poetry init --name content-parser --description "Decoupled content parser for habits lessons" --author "MindMirror" --license MIT --python "^3.11" --no-interaction && \
      poetry add pyyaml && \
      poetry add --group dev pytest && \
      poetry install --no-interaction --no-ansi --no-root; \
    fi

# Default command runs tests
CMD ["/bin/sh", "-lc", "PYTHONPATH=/app poetry run pytest -q"]


