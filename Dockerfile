FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install cURL
RUN apt-get update && apt-get install -y curl

# Install poetry
RUN pip install poetry

# Copy only the files needed for dependency installation
COPY poetry.lock pyproject.toml /app/

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install --no-root --without dev

# Copy the rest of the application code
COPY . /app/

# Expose the ports for the API and Streamlit app
EXPOSE 8000
EXPOSE 8501

# The command to run the application will be in docker-compose.yml
CMD ["poetry", "run", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"] 