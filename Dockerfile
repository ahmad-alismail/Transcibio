
# Use multi-arch base image
FROM --platform=$TARGETPLATFORM python:3.10-slim

# Set build arguments and environment variables
ARG TARGETPLATFORM
ARG BUILDPLATFORM
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_ENABLE_CORS=false

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements first (excluding PyTorch)
COPY requirements.txt ./

# Install PyTorch and other dependencies based on architecture
RUN pip install --no-cache-dir --upgrade pip && \
    if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
        # ARM64-specific PyTorch installation (no CUDA)
        pip install --no-cache-dir torch torchvision torchaudio && \
        # Install other requirements excluding torch and CUDA packages
        grep -v "torch" requirements.txt | grep -v "nvidia" > requirements_filtered.txt && \
        pip install --no-cache-dir -r requirements_filtered.txt; \
    else \
        # AMD64 with CUDA support
        pip install --no-cache-dir torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118 && \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# Copy the rest of the application
COPY . .

# Expose the Streamlit port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
