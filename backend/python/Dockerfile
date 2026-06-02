# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application source
COPY src/ ./src/
COPY pyproject.toml .

# Stage 2: Production
FROM python:3.11-slim as production

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application source
COPY --from=builder /app/src/ ./src/
COPY --from=builder /app/pyproject.toml .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/home/appuser/.local/bin:$PATH \
    USER=appuser

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
