FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app /app/app
COPY fix_training.sh /app

# Create directory for ChromaDB persistence
RUN mkdir -p /app/data/chromadb

# Set Python path to include the app directory
ENV PYTHONPATH=/app

# Expose port for Streamlit
EXPOSE 8501
EXPOSE 8502

# Command to run the application
CMD ["streamlit", "run", "app/app.py", "--server.address=0.0.0.0"]
