# VeriPhysics Admin Dashboard Implementation Plan

- [x] **Backend: Database Schema Update**
    - [x] Add `is_admin` column to `User` model.
    - [x] Recreate database and seed admin user (`debug@test.com`).
- [x] **Backend: API Implementation**
    - [x] Add `/users/me` endpoint for session info.
    - [x] Add `/admin/stats` endpoint for system metrics.
    - [x] Add `/admin/jobs` endpoint for global job history.
    - [x] Implement `get_current_admin` dependency for security.
- [x] **Frontend: Admin UI**
    - [x] Create `/admin` page with dashboard stats and job table.
    - [x] Update User Dashboard with conditional "Admin Panel" link.
- [ ] Verification & Testing
    - [x] Create `start.sh` to run both services.
    - [ ] Verify admin access and data display.

# Phase 2: C2PA Integration
- [x] **Research & Tooling**
    - [x] Install `c2pa-python`.
    - [x] Generate self-signed X.509 certificates (`backend/certs`).
- [x] **Backend Implementation**
    - [x] Create `C2PASignerService` (`backend/app/c2pa_signer.py`).
    - [x] Update `VerificationJob` model with `signed_url`.
    - [x] Integrate signing into `process_verification` workflow.
    - [x] Serve signed files via `/files` static mount.
- [x] **Frontend Updates**
    - [x] Update `Job` interface.
    - [x] Display "Manifest" link in Dashboard for verified jobs.
- [ ] **Verification**
    - [ ] Test end-to-end flow with a real video.

# Future Roadmap
- [ ] **Performance Optimization**: GPU acceleration for Optical Flow.
- [ ] **Security**: Implement "Screen Attack" detection (2D planar motion check).
- [ ] **Mobile SDK**: Complete Android implementation and add iOS support.
- [ ] **Production Readiness**: Dockerize for cloud deployment (AWS/GCP).
