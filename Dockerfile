# HiveBox - Phase 2
# Base image - official Python slim for smaller size
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy application code into container
COPY app.py .

# Run the application
CMD ["python", "app.py"]