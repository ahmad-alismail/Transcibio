# Use an official Python runtime as a parent image
# Choose a version compatible with your dependencies (e.g., 3.10 or 3.11)
FROM python:3.10-slim

# Set environment variables to prevent interactive prompts during package installations
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    # Streamlit specific env vars (optional, but good practice)
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_ENABLE_CORS=false

# Install system dependencies required by torch, torchaudio, whisper, pyannote
# ffmpeg: often needed by whisper/torchaudio for audio processing
# libsndfile1: often needed by torchaudio/soundfile for audio I/O
# git: required if any dependency installs directly from git (pyannote sometimes does)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt ./

# Install Python dependencies
# --no-cache-dir: Reduces image size slightly
# Upgrade pip first
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the working directory
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Define the command to run the application
# Uses the environment variables set above for port
# --server.address=0.0.0.0 makes Streamlit accessible from outside the container
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
