# CampusOS — Continuation & Execution Guide

CampusOS is an opportunity intelligence platform for university students built as a modular monolith:
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy + Alembic + PostgreSQL (pgvector)
- **Frontend:** Next.js 15 (App Router) + TypeScript + Tailwind CSS
- **Testing:** Pytest (backend) + Vitest (frontend)

---

## Current Status: Phase 2 (Authentication) Complete

The project now has complete, tested, and secure authentication across backend and frontend.

### What Was Built in Phase 2:
1. **User SQLAlchemy Model** (`backend/app/models/user.py`):
   - Supports UUID primary keys, email index, bcrypt password hash, academic details, and opportunity preferences.
2. **Alembic Initial Migration** (`backend/migrations/versions/001_create_users_table.py`):
   - Creates the `users` table with unique indexes and cross-database JSON support (Postgres JSONB with SQLite fallback).
3. **Security Utilities** (`backend/app/core/security.py`):
   - Passlib Bcrypt password hashing & verification.
   - Python-Jose JWT access token encoding & decoding with configurable expiration.
4. **Auth Schemas** (`backend/app/schemas/user.py`):
   - Request models with Pydantic validation (email format, password min length 8).
   - Response models guaranteeing passwords are never leaked.
5. **Auth Service Layer** (`backend/app/services/auth.py`):
   - Separates business logic from HTTP handlers (`register_user`, `authenticate_user`).
   - Standard error handling returning `EMAIL_TAKEN` (409) and `INVALID_CREDENTIALS` (401).
6. **Auth Router** (`backend/app/routers/auth.py`):
   - `POST /api/auth/register` (201 Created)
   - `POST /api/auth/login` (200 OK)
   - `POST /api/auth/logout` (200 OK, requires Bearer token)
7. **Auth Dependency Injection** (`backend/app/core/dependencies.py`):
   - `get_current_user`
   - `get_current_active_user`
   - `get_current_admin_user`
8. **Automated Backend Tests** (`backend/tests/test_auth.py`):
   - 10 unit and integration tests covering hashing, JWT validity, duplicate rejection, validation errors, and protected routes.
9. **Frontend Auth & UI** (`frontend/`):
   - Reusable accessible UI components: `Button.tsx`, `Input.tsx`.
   - Client storage helpers (`lib/auth.ts`) for JWT tokens and cached user profiles.
   - API client methods (`lib/api.ts`): `registerUser`, `loginUser`, `logoutUser`, `authFetch`.
   - `/signup` page with real-time validation and error alert.
   - `/login` page with session redirection.
   - Landing page with dynamic sign-in / sign-out controls.
   - 5 Vitest tests covering auth storage and API behavior (`frontend/__tests__/auth.test.ts`).

---

## Local Development Instructions

### 1. Database Setup
Start PostgreSQL via Docker from the project root:
```bash
docker compose up -d postgres
```
Database credentials: `campusos` / `campusos` on port `5432`.

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 3. Run Backend Tests
In `backend/`:
```bash
pytest -v
```
All 16 tests should pass:
- 4 Health check tests (`tests/test_health.py`)
- 2 Config loading tests (`tests/test_config.py`)
- 10 Auth & security tests (`tests/test_auth.py`)

### 4. Frontend Setup
In a new terminal:
```bash
cd frontend

# Copy environment template
cp .env.local.example .env.local

# Install dependencies
npm install

# Run frontend dev server
npm run dev
```
- Web Application: [http://localhost:3000](http://localhost:3000)
- Sign Up: [http://localhost:3000/signup](http://localhost:3000/signup)
- Sign In: [http://localhost:3000/login](http://localhost:3000/login)

### 5. Run Frontend Tests
In `frontend/`:
```bash
npm test
```
All 8 tests should pass (3 API client tests, 5 Auth storage and network tests).

---

## Architecture Flow

```text
Browser / Next.js Client
       │
       ├── POST /api/auth/register ──────┐
       ├── POST /api/auth/login ─────────┼──→ FastAPI (Modular Monolith)
       ├── POST /api/auth/logout ────────┤         │
       └── GET  /api/health ─────────────┘         ▼
                                             AuthService / Security
                                                   │
                                                   ▼
                                            SQLAlchemy ORM
                                                   │
                                                   ▼
                                         PostgreSQL (users table)
```

---

## Next Step: Phase 3 — User Profile

The next milestone is implementing the academic profile and preferences engine (FR-01):
1. Create `Skill`, `UserSkill`, `Interest`, `UserInterest` SQLAlchemy models.
2. Generate Alembic migration `002_create_profile_tables`.
3. Create Pydantic schemas for Profile update, Skills catalog, and Interests.
4. Implement UserService:
   - `GET /api/users/me` — returns complete user profile with skills and interests
   - `PATCH /api/users/me` — updates academic details (university, degree, branch, graduation_year, current_year, cgpa, opportunity preferences)
   - `PUT /api/users/me/skills` — synchronizes user skills and proficiency
   - `PUT /api/users/me/interests` — synchronizes user interest tags
5. Create Profile frontend page (`/app/profile`):
   - Academic section (university, degree, branch, year, CGPA)
   - Tag-based input for Skills and Interests
   - Preference selectors (opportunity types, work modes)
6. Add unit and integration tests for profile management.
