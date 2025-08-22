# First stage: Build stage with Poetry
FROM python:3.12-slim AS builder

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=True

# Set work directory
WORKDIR /tmp

# Install Poetry
# Consider pinning the Poetry version for more reproducible builds
RUN pip install poetry poetry-plugin-export

# Copy only the necessary files for dependency installation
# This ensures that changing application code doesn't bust the dependency cache layer
COPY ./pyproject.toml ./poetry.lock* /tmp/

# Allow setting a build argument for PROD/DEV builds
ARG PROD=0

# Install dependencies based on the PROD flag
# For PROD, export without dev dependencies. For DEV, include them.
RUN if [ "$PROD" = "1" ]; then \
      poetry export -f requirements.txt --output requirements.txt --without-hashes; \
    else \
      poetry export --with dev -f requirements.txt --output requirements.txt --without-hashes; \
    fi

# Second stage: Production/Runtime stage
FROM python:3.12-slim

# Set the working directory to /app
ENV APP_HOME=/app
WORKDIR $APP_HOME
ENV PYTHONPATH=/app

# Create a non-root user and group for security
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Install curl (useful for healthchecks, etc.) and other essential packages
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt from the builder stage
COPY --from=builder /tmp/requirements.txt .

# Install runtime dependencies from requirements.txt
# Using --no-cache-dir can reduce image size slightly
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code from the current directory (context) to /app
# This should be one of the last layers to optimize caching
COPY . .

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appuser $APP_HOME

# Switch to the non-root user
USER appuser

# Expose the port the app runs on (defined by Uvicorn in server.py or CMD)
# This should match the MEALS_HTTP_PORT or default in server.py, typically 8000 for internal
EXPOSE 8004

# Command to run the server
# Uses python -m to run the server module, which is good practice
CMD ["python", "-m", "meals.web.server"] 