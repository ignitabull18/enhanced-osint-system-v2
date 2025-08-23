# Enhanced OSINT System v2.0 - Coolify Deployment
# Optimized for production deployment with health checks and monitoring

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install critical OSINT tools explicitly
RUN pip install --no-cache-dir \
    dnspython>=2.4.0 \
    validators>=0.22.0 \
    python-whois>=0.8.0 \
    requests>=2.31.0 \
    holehe>=1.4.0

# Create symlink for holehe
RUN ln -sf /usr/local/bin/holehe /usr/bin/holehe || true

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x *.py

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Expose port for health checks
EXPOSE 8002

# Default command
CMD ["python3", "main.py"]