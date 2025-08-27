# First stage: Build stage with Poetry
FROM python:3.12-slim AS builder

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=True

# Set work directory
WORKDIR /tmp

# Install Poetry
RUN pip install poetry poetry-plugin-export

# Copy only the necessary files for dependency installation
COPY practices_service/pyproject.toml practices_service/poetry.lock /tmp/

# Also bring in shared package and build its wheel
COPY src/shared /shared
RUN cd /shared && poetry build

# Allow setting a build argument
ARG PROD=0

# Install deps depending on PROD flag
RUN if [ "$PROD" = "1" ]; then \
      poetry export -f requirements.txt --output requirements.txt --without-hashes; \
    else \
      poetry export --with dev -f requirements.txt --output requirements.txt --without-hashes; \
    fi

# Second stage: Production stage
FROM python:3.12-slim

# Set the working directory to /app
ENV APP_HOME=/app
WORKDIR $APP_HOME
ENV PYTHONPATH=/app

# Install curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt from the builder stage
COPY --from=builder /tmp/requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Install shared package wheel built in builder stage (force reinstall to pick up code changes)
COPY --from=builder /shared/dist/*.whl /tmp/
RUN pip install --no-cache-dir --upgrade --force-reinstall /tmp/*.whl

# Copy service source code
COPY practices_service /app

# Copy shared source to ensure it’s importable from /app/shared before site-packages
COPY src/shared /app/shared

# Expose port 8000 for the app
EXPOSE 8000

# Command to run the server
CMD ["uvicorn", "practices.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
