# syntax=docker/dockerfile:1

# --- Builder stage: use Poetry to export requirements ---
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /tmp

# Install Poetry and export plugin
RUN pip install --no-cache-dir poetry poetry-plugin-export

# Copy only dependency metadata (no source code yet)
COPY pyproject.toml /tmp/

# Allow setting a build arg to include dev deps in the export (default: false)
ARG BUILD_WITH_DEV=false

# Generate lock file if missing and export requirements
RUN if [ ! -f poetry.lock ]; then poetry lock; fi && \
    if [ "$BUILD_WITH_DEV" = "true" ]; then \
      poetry export --with dev -f requirements.txt --output requirements.txt --without-hashes; \
    else \
      poetry export -f requirements.txt --output requirements.txt --without-hashes; \
    fi

# --- Runtime stage ---
FROM python:3.12-slim

ENV APP_HOME=/app \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR ${APP_HOME}

# Install system deps required by common Python packages
RUN apt-get update && apt-get install -y \
    curl \
    cmake \
    g++ \
    build-essential \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from builder and install
COPY --from=builder /tmp/requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application source
COPY . .

EXPOSE 8005

# Use the module entrypoint which reads PORT from env (default 8005)
CMD ["python", "-m", "movements.web.server"] 