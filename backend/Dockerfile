# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Set environment variables to ensure the output is sent directly to the terminal with no buffering.
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Ensure the service account key is copied
COPY service_account_key.json /app/service_account_key.json

# Set environment variables for Flask and Cloud
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/service_account_key.json

# Command to run the application using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
