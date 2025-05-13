FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Configure Poetry to not create a virtual environment inside the container
RUN poetry config virtualenvs.create false

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY app /app/app
COPY fix_training.sh /app

# Create directory for ChromaDB persistence
RUN mkdir -p /app/data/chromadb

# Set Python path to include the app directory
ENV PYTHONPATH=/app

# Configure protobuf to use pure Python implementation
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Expose port for Streamlit
EXPOSE 8501
EXPOSE 8502

# Command to run the application
# Use the refactored app by default, but allow overriding with environment variable
ENV APP_SCRIPT=app/app.py
CMD ["sh", "-c", "streamlit run ${APP_SCRIPT} --server.address=0.0.0.0"]
