# syntax=docker/dockerfile:1

# Use an official Python runtime as a parent image
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy journal_service's poetry project
COPY src/journal_service/pyproject.toml src/journal_service/poetry.lock ./

# Install journal_service deps
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only=main

# Now, bring in the shared package
COPY src/shared /app/shared

# Build the shared wheel automatically
WORKDIR /app/shared
RUN poetry build

# Go back to service directory
WORKDIR /app

# Install the freshly built wheel
RUN pip install ./shared/dist/*.whl

# --- Final Stage ---
FROM python:3.11-slim

WORKDIR /app

# For health check
RUN apt-get update && apt-get install -y curl

# Copy the installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Copy the application source code
COPY src/journal_service /app/journal_service

# Download the CA during build
ADD https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem /etc/ssl/certs/supabase-rds-ca.pem
ENV SUPABASE_CA_CERT_PATH=/etc/ssl/certs/supabase-rds-ca.pem

# Set Python path to include src directory
ENV PYTHONPATH=/app/src

# Expose the port the app runs on
EXPOSE 8000

# Set the entrypoint
CMD ["uvicorn", "journal_service.journal_service.main:app", "--host", "0.0.0.0", "--port", "8000"] 
