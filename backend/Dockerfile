# Stage 1: Build C++ Core
FROM ubuntu:22.04 as builder

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    libopencv-dev \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY cpp_core/ .
RUN mkdir build && cd build && cmake .. && make

# Stage 2: Python Service
FROM python:3.10-slim

WORKDIR /app

# Install Runtime Dependencies (OpenCV libs)
# We need libopencv-core, etc. easier to just install libopencv-dev or similar runtime pkg
# shared libs are needed for the CLI to run
RUN apt-get update && apt-get install -y \
    libopencv-dev \
    libopencv-contrib-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python Deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Built CLI
COPY --from=builder /src/build/vp_cli /usr/local/bin/vp_cli

# Copy App Code
COPY backend/app/ ./app/

# Env
ENV VERIPHYSICS_CLI_PATH=/usr/local/bin/vp_cli

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
