# Use a Python base image (python:3.12-slim is using Debian Trixie/13)
FROM python:3.12-slim

# Install system dependencies needed for PyAudio
# Note the changed package name: 'portaudio19-dev'
RUN apt-get update && \
    apt-get install -y libportaudio2 portaudio19-dev && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Define the command to run your application (REPLACE 'your_script.py' with your main file)
CMD ["python", "your_script.py"]