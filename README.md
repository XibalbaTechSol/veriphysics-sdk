# VeriPhysics SDK

VeriPhysics is a "Physics-based Verification" system that authenticates video content by cross-referencing optical flow (visual motion) with gyroscope data (physical motion) logged by the camera device.

## Core Features
*   **Active Provenance**: Proves video was captured on a real device at a specific time.
*   **Physics Verification**: Matches 3D camera rotation with pixel motion to detect deepfakes or simulator attacks.
*   **C2PA Signing Authority**: Acts as a trusted signer, injecting "Physics Verified" assertions into standard C2PA manifests.
*   **Developer-First**: Simple REST API and Dashboard.

## Architecture
*   **CPP Core**: High-performance C++ engine using OpenCV and FastDTW for signal analysis.
*   **Backend**: Python (FastAPI) service handling auth, job queues, verification logic, and C2PA signing.
*   **Frontend**: Next.js (React) dashboard for managing API keys and viewing results.
*   **Android SDK**: (Concept) Kotlin library for capturing secure sensor logs alongside video.

## Getting Started

### Prerequisites
*   Python 3.12+
*   Node.js 18+
*   CMake & C++ Compiler
*   OpenSSL (for generating signing keys)

### Installation

1.  **Install Dependencies**
    ```bash
    ./install_deps.sh
    ```

2.  **Generate Signing Keys (for C2PA)**
    ```bash
    chmod +x backend/certs/generate_certs.sh
    ./backend/certs/generate_certs.sh
    ```

3.  **Start Services**
    ```bash
    ./start.sh
    ```
    *   Backend: http://localhost:8000
    *   Frontend: http://localhost:3000

## Usage
1.  Register an account on the Frontend.
2.  Generate an API Key.
3.  Upload a video + gyro CSV bundle to the `/verify` endpoint.
4.  If verified, download the C2PA-signed video with the "Physics Verified" assertion.

## C2PA Integration
VeriPhysics uses the `c2pa-python` library to sign verified assets.
*   **Assertion**: `stds.veriphysics.assertion`
*   **Data**: Includes verification score, timestamp, and verification details.
*   **Verification**: Signed files can be verified using [Content Credentials Verify](https://contentcredentials.org/verify).

## License
Proprietary. Copyright 2024 Xibalba Solutions.

