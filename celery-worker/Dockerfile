FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Set working directory
WORKDIR /app

# Copy Poetry files
COPY celery-worker/pyproject.toml celery-worker/poetry.lock* ./

# Install dependencies (excluding dev dependencies)
RUN poetry install --without dev

# Copy and build the shared package
COPY src/shared /app/shared
WORKDIR /app/shared
RUN poetry build

# Go back to app directory and install the shared wheel
WORKDIR /app
RUN pip install ./shared/dist/*.whl

# Copy application code
RUN find /app -name '*.pyc' -delete || true
COPY celery-worker .

# Make startup script executable
RUN chmod +x start.sh

# Expose port
EXPOSE 8000

# Start the service
CMD ["./start.sh"] 