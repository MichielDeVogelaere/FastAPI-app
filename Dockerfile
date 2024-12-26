# Base image supports Nvidia CUDA but does not require it and can also run demucs on the CPU
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

USER root
ENV TORCH_HOME=/data/models
ENV OMP_NUM_THREADS=1

# Install required tools
# Notes:
#  - build-essential and python3-dev are included for platforms that may need to build some Python packages (e.g., arm64)
#  - torchaudio >= 0.12 now requires ffmpeg on Linux, see https://github.com/facebookresearch/demucs/blob/main/docs/linux.md
RUN apt update && apt install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    git \
    python3 \
    python3-dev \
    python3-pip \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Clone Demucs (now maintained in the original author's github space)
RUN git clone --single-branch --branch main https://github.com/adefossez/demucs /lib/demucs
WORKDIR /lib/demucs

# Checkout known stable commit on main
RUN git checkout b9ab48cad45976ba42b2ff17b229c071f0df9390

# Install dependencies with overrides for known working versions on this base image
RUN python3 -m pip install -e . "torch<2" "torchaudio<2" "numpy<2" --no-cache-dir

# Install FastAPI and related dependencies
RUN python3 -m pip install fastapi "uvicorn[standard]" python-multipart aiofiles --no-cache-dir

# Run once to ensure demucs works and trigger the default model download
RUN python3 -m demucs -d cpu test.mp3

# Cleanup output - we just used this to download the model
RUN rm -r separated

# Copy application files
COPY ./app /app

# Set up volumes for data persistence
VOLUME /data/input
VOLUME /data/output
VOLUME /data/models

# Set working directory to the app folder
WORKDIR /app

# Create a startup script
RUN echo '#!/bin/bash\n\
if [ "$1" = "serve" ]; then\n\
    exec uvicorn main:app --host 0.0.0.0 --port 8000\n\
else\n\
    exec "$@"\n\
fi' > /start.sh && chmod +x /start.sh

# Use the startup script as entrypoint
ENTRYPOINT ["/start.sh"]
CMD ["serve"]