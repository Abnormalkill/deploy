# Use a stable Python base image (3.12 is robust for deployment)
FROM python:3.12-slim

# Install system dependencies required for compiling PyAudio:
# 1. build-essential: Provides the GCC compiler needed to build PyAudio from source.
# 2. libportaudio2: The runtime library for PortAudio.
# 3. portaudio19-dev: The development headers needed to build PyAudio.
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

# Define the command to run your application
# IMPORTANT: REPLACE 'your_main_script.py' with the actual name of your main Python file!
CMD ["python", "app.py"]