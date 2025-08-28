# First stage: Build stage with Poetry
FROM python:3.12-slim AS builder

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=True
ENV PYTHONDONTWRITEBYTECODE=1

# Set work directory
WORKDIR /tmp

# Install Poetry and poetry-plugin-export
# poetry-plugin-export is needed for `poetry export`
RUN pip install poetry poetry-plugin-export

# Copy only the necessary files for dependency installation
COPY ./pyproject.toml ./poetry.lock* /tmp/

# Allow setting a build argument (though not strictly used in this simplified version yet)
ARG PROD=0 

# Install deps and export to requirements.txt
# For simplicity, we'll export all dependencies. 
# The PROD flag like in practices Dockerfile can be used to differentiate dev/prod deps.
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Second stage: Production stage
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app
WORKDIR $APP_HOME
ENV PYTHONPATH=/app

# Install curl (useful for healthchecks, etc.)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt from the builder stage
COPY --from=builder /tmp/requirements.txt .

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code from the current directory to $APP_HOME in the image
COPY . .

# Expose port 8000 for the app (or whatever HTTP_PORT is set to in docker-compose)
EXPOSE 8000 

# Command to run the Uvicorn server
# Assumes users.web.server uses Uvicorn and respects HOST/PORT from env or defaults
# The CMD from practices: CMD ["uvicorn", "practices.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
# We used: CMD ["poetry", "run", "python", "-m", "users.web.server"]
# If users.web.server directly calls uvicorn.run with appropriate host/port, that's fine.
# Otherwise, a more direct uvicorn command is often preferred for clarity.
# Let's assume users.web.server starts uvicorn correctly on 0.0.0.0 and port from HTTP_PORT env var.
# For consistency with the practices example and direct Uvicorn usage: 
CMD ["uvicorn", "users.web.app:app", "--host", "0.0.0.0", "--port", "8000"] 