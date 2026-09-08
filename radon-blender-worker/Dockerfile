# RADON Blender Worker — Dockerfile
# Contains a REAL Blender runtime for headless 3D asset generation.
#
# Build:  docker build -t radon-blender-worker .
# Run:    docker run -p 8001:8001 radon-blender-worker

FROM python:3.12-slim AS base

# Install system dependencies required by Blender and the Python web server
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    xz-utils \
    libxrender1 \
    libxi6 \
    libxxf86vm1 \
    libxfixes3 \
    libxkbcommon0 \
    libsm6 \
    libgl1 \
    libegl1 \
    libopengl0 \
    libglib2.0-0 \
    libfontconfig1 \
    libfreetype6 \
    libxext6 \
    libx11-6 \
    libxau6 \
    libxdmcp6 \
    libxss1 \
    libxtst6 \
    libxcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xinput0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

# Install Blender 4.2 LTS from the official download
# This is a REAL Blender runtime — not a stub.
ENV BLENDER_VERSION=4.2
ENV BLENDER_SUBVERSION=4.2.4
ENV BLENDER_URL="https://download.blender.org/release/Blender4.2/blender-4.2.4-linux-x64.tar.xz"

RUN wget -q --no-check-certificate "${BLENDER_URL}" -O /tmp/blender.tar.xz && \
    mkdir -p /opt/blender && \
    tar -xf /tmp/blender.tar.xz -C /opt/blender --strip-components=1 && \
    rm /tmp/blender.tar.xz && \
    ln -s /opt/blender/blender /usr/bin/blender && \
    chmod +x /usr/bin/blender

# Verify Blender is actually installed and executable
RUN blender --background --version

# Set up the application
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create output directory
RUN mkdir -p /tmp/radon-output

# Environment configuration
ENV BLENDER_PATH=/usr/bin/blender
ENV OUTPUT_DIR=/tmp/radon-output
ENV HOST=0.0.0.0
ENV PORT=8001
ENV JOB_TIMEOUT=120
ENV MAX_OUTPUT_SIZE_MB=100

EXPOSE 8001

# Health check — verify both the API and Blender executable
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request, json; r=urllib.request.urlopen('http://localhost:8001/health'); d=json.loads(r.read()); exit(0 if d.get('blender')=='available' else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
