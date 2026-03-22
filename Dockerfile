# HiveBox - Phase 3
# Using specific version for reproducible builds
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
# Docker caches this layer - only rebuilds if requirements.txt changes
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create non-root user for security
RUN adduser --disabled-password --gecos "" appuser

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]