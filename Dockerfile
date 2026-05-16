# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=True

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
# We copy this first to leverage Docker cache for dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all local files to the container image
COPY . .

# Expose port 8080 for the Flask app
EXPOSE 8080

# Run the web service on container startup using gunicorn
CMD exec gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 --timeout 0 main:app
