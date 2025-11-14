# Use a stable Python base image (3.12 is robust for deployment)
FROM python:3.12-slim

# Install system dependencies required for compiling PyAudio:
# 1. build-essential: Provides the GCC compiler needed for PyAudio and others.
# 2. libportaudio2 & portaudio19-dev: Libraries needed to build PyAudio.
RUN apt-get update && \
    apt-get install -y build-essential libportaudio2 portaudio19-dev && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port (Render handles this, but it's good practice)
EXPOSE 8000

# Define the command to run your application using Gunicorn
# Your app is named 'app' (from app.py). SocketIO requires a special Gunicorn worker.
# We are using 'gunicorn' with a worker type compatible with Flask-SocketIO.
CMD gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 app:app