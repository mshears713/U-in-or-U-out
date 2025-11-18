# Data Alchemist - Dockerfile for Windows/WSL
# Multi-stage build for optimized image size

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Set metadata labels
LABEL maintainer="data-alchemist"
LABEL description="A modular universal data conversion framework with automatic file type detection"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash alchemist && \
    mkdir -p /app /data && \
    chown -R alchemist:alchemist /app /data

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=alchemist:alchemist . .

# Install the package in development mode
RUN pip install --no-cache-dir -e .

# Switch to non-root user
USER alchemist

# Create volume mount points for data
VOLUME ["/data"]

# Set the default command to show help
ENTRYPOINT ["data-alchemist"]
CMD ["--help"]

# Health check (optional - validates Python environment)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import data_alchemist; print('OK')" || exit 1
