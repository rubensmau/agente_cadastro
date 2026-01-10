# Dockerfile for Google Cloud Run deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY data/ ./data/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV SERVER_MODE=compliant

# Expose port (documentation only, Cloud Run uses PORT env var)
EXPOSE 8080

# Cloud Run expects the service to listen on $PORT
# The app instance is created at module level in src.main
CMD exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT} --workers 1
