# src/api/Dockerfile (improved from your base)
FROM python:3.12-slim

WORKDIR /app

# Add PostgreSQL dev headers + compiler
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy & install Python deps (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY models/ ./models/

# Expose port
EXPOSE 8000

# Healthcheck (uses your /health endpoint)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Fix: Correct module path
CMD ["uvicorn", "src.api.main:api", "--host", "0.0.0.0", "--port", "8000"]
