# VeriPhysics

**The "Stripe for Reality" — Trust, Verified by Physics.**

VeriPhysics is a developer-first SDK and API for **Active Provenance**. We rely on the laws of physics, not just metadata, to authenticate video content. By correlating optical flow with accelerometer/gyroscope data, we prove **Causality**: the motion in the video *must* match the physical motion of the device.

> **Why VeriPhysics?**
> *   **Active Provenance**: Proves reality at the moment of capture.
> *   **Physics-based**: Harder to spoof than metadata; doesn't rely on hardware-backed keystores (like Truepic).
> *   **Developer Friendly**: Simple SDK + JSON API. No Blockchain wallets, no AI black boxes.

 This "Physical Consistency Check" makes it extremely difficult to use pre-recorded footage, deepfakes, or generated media as authentic live captures.

## Architecture

The VeriPhysics ecosystem consists of three main components working in unison:

### 1. Android Client (Proof Generation)
*   **Role**: trusted capture device.
*   **Functionality**:
    *   Records high-definition video.
    *   Simultaneously logs high-frequency sensor data (Gyroscope, Accelerometer).
    *   **Future Integration**: Will implement **ProofMode** to cryptographically sign the bundle (Video + Sensor Data + Device Attestation) at the point of capture, ensuring a secure Chain of Custody.
*   **Location**: `android/`

### 2. Cloud Verification Service (API)
*   **Role**: Validation and integration point.
*   **Tech Stack**: Python, FastAPI.
*   **Functionality**:
    *   Exposes a RESTful API (`/verify`) for clients to submit proof bundles.
    *   Validates API keys and cryptographic signatures (in production).
    *   Orchestrates the verification process by dispatching jobs to the Core Engine.
    *   Returns a JSON `Verification Report` with a confidence score and verdict.
*   **Location**: `backend/`

### 3. Core Verification Engine
*   **Role**: High-performance mathematical analysis.
*   **Tech Stack**: C++, OpenCV.
*   **Functionality**:
    *   Computes optical flow from video frames.
    *   Integrates sensor data to reconstruct camera trajectory.
    *   Performs cross-correlation analysis to determine "Physical Consistency".
*   **Location**: `cpp_core/`

---

## Usage for Paying Clients

VeriPhysics is designed as an API-first service for platforms requiring high-assurance media verification (e.g., Insurance Claims, News Agencies, dating apps, Citizen Journalism).

### Integration Workflow

1.  **Capture**: Your user uses the VeriPhysics SDK (or standalone app) to record a video. The app generates a tamper-proof bundle.
2.  **Submit**: Your backend (or the mobile app directly) uploads this bundle to the VeriPhysics Cloud.
3.  **Verify**: Our engines analyze the physics of the footage.
4.  **Result**: You receive a boolean `verified` status and a `score` reflecting the confidence level.

### API Reference

**Endpoint**: `POST /verify`

**Request**:
`multipart/form-data`
*   `video`: The recorded video file (MP4).
*   `gyro`: The time-synchronized gyroscope data (CSV).

**Example (cURL)**:
```bash
curl -X POST "https://api.veriphysics.com/verify" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "video=@evidence.mp4" \
  -F "gyro=@metadata.csv"
```

**Response**:
```json
{
  "verified": true,
  "score": 0.98,
  "message": "REAL: Motion vectors consistent with sensor data.",
  "details": {
     "signature_valid": true,
     "device_attested": true
  }
}
```

---

## Implementation Status & Roadmap

### Phase 1: Native Core Prototype (Completed) [x]
*   [x] Python prototype of optical flow vs. gyro correlation.
*   [x] Native C++ implementation of the Motion Verifier engine (OpenCV).
*   [x] CLI test harness for the verified engine.

### Phase 2: Cloud Service Integration (In Progress) [/]
*   [x] Basic FastAPI scaffolding (`backend/app/main.py`).
*   [x] Python wrapper for C++ CLI (`backend/app/verifier.py`).
*   [ ] **Dockerization**:
    *   Create multi-stage `Dockerfile` (Build C++ CLI -> Copy to Python runtime).
    *   Minimize image size (Alpine/Slim + shared libs).
*   [ ] **Input Validation**:
    *   Implement strict MIME type checking (e.g., `video/mp4`, `text/csv`).
    *   Enforce file size limits (e.g., 50MB max upload).
*   [ ] **Async Processing**:
    *   Refactor `/verify` to offload work to background workers (prevent request timeout).

### Phase 3: Android ProofMode Integration (Planned) [ ]
*   [ ] **Guardian Project Core**:
    *   Integrate `libproofmode` for secure, tamper-evident sensor logging.
    *   Ensure cryptographic signing of the capture bundle at the hardware level (if supported).
*   [ ] **Data Standardization**:
    *   Standardize metadata format (JSON/CBOR) for interoperability.
*   [ ] **Security**:
    *   Implement Ed25519 key generation and signing for the bundle.
    *   Add "Secure Capture" mode in UI that disables editing features during capture.

### Phase 4: Production Hardening (Planned) [ ]
*   [ ] **Database & Persistence**:
    *   Design SQL schema for `VerificationJobs` (id, status, score, timestamp, client_id).
    *   Integrate Postgres for long-term result storage.
*   [ ] **API Gateway & Security**:
    *   Implement rate limiting (Redis-backed).
    *   Replace mock API Key system with real middleware and distinct client scopes.
    *   Enforce HTTPS/TLS for all transport.
*   [ ] **Scalable Storage**:
    *   Integrate S3 (or compatible object storage) for evidence retention (vs. ephemeral /tmp).

---

## Development Setup

### Prerequisites
*   Android Studio (for Client)
*   Python 3.10+ (for Cloud Service)
*   CMake & C++ Compiler (for Core Engine)
*   OpenCV 4.x

### Build Core Engine
```bash
cd cpp_core
mkdir build && cd build
cmake ..
make
```

### Run Cloud Service
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Set path to built CLI
export VERIPHYSICS_CLI_PATH=../cpp_core/build/vp_cli
uvicorn app.main:app --reload
```
