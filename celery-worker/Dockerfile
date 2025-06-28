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
COPY pyproject.toml poetry.lock* ./

# Install dependencies (excluding dev dependencies)
RUN poetry install --without dev

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Expose port
EXPOSE 8000

# Use the startup script
CMD ["./start.sh"] 