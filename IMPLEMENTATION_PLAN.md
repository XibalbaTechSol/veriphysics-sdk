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
- [ ] **Verification & Testing**
    - [ ] Create `start.sh` to run both services.
    - [ ] Verify admin access and data display.
