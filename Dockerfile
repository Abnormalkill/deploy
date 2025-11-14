# Use a Python base image (using 3.12 for stability, as discussed earlier)
FROM python:3.12-slim

# Install system dependencies needed for PyAudio
# This step requires root privileges, which are available in a Docker build.
RUN apt-get update && \
    apt-get install -y libportaudio2 libportaudio-dev && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Define the command to run your application (Replace 'your_script.py' with your main file)
CMD ["python", "your_script.py"]