# CampusOS — Continuation & Execution Guide

CampusOS is an opportunity intelligence platform for university students built as a modular monolith:
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy + Alembic + PostgreSQL (pgvector)
- **Frontend:** Next.js 15 (App Router) + TypeScript + Tailwind CSS
- **Testing:** Pytest (backend) + Vitest (frontend)

---

## Current Status: Phase 3 (User Profile & Preferences) Complete

The platform now provides comprehensive student profile and preference management (FR-01) with database persistence, canonical skill and interest mapping, and responsive UI.

### What Was Built in Phase 3:
1. **SQLAlchemy Models** (`backend/app/models/`):
   - `Skill` (`skills` table) with unique name index.
   - `UserSkill` (`user_skills` junction table) with proficiency rating.
   - `Interest` (`interests` table) with unique name index.
   - `UserInterest` (`user_interests` junction table).
   - `User` model extended with `preferred_locations` and relationships to skills and interests.
2. **Alembic Migration** (`backend/migrations/versions/002_create_profile_tables.py`):
   - Creates `skills`, `user_skills`, `interests`, `user_interests` tables and adds `preferred_locations` JSON column to `users`.
3. **Pydantic Schemas** (`backend/app/schemas/user.py`):
   - `UserProfileResponse`, `UserProfileUpdateRequest`, `SkillItem`, `SkillRead`, `UserSkillsUpdateRequest`, `InterestItem`, `InterestRead`, `UserInterestsUpdateRequest`.
4. **User Service Layer** (`backend/app/services/user.py`):
   - `get_profile`: Aggregates user academic data, skills with proficiency, and interests into a clean schema.
   - `update_profile`: Updates academic background (university, degree, branch, year, CGPA) and multi-select preferences (types, work modes, locations).
   - `sync_skills`: Canonicalizes skill names, prevents duplicates, and links to user.
   - `sync_interests`: Canonicalizes interest names, prevents duplicates, and links to user.
5. **Profile Router** (`backend/app/routers/users.py`):
   - `GET /api/users/me` — Read current authenticated profile.
   - `PATCH /api/users/me` — Update academic details and preferences.
   - `PUT /api/users/me/skills` — Synchronize skills and proficiency levels.
   - `PUT /api/users/me/interests` — Synchronize career interests.
6. **Backend Tests** (`backend/tests/test_users.py`):
   - 7 unit and integration tests covering GET/PATCH/PUT, boundary validation (CGPA <= 10.0), and strict user data isolation.
7. **Frontend Profile & Tag Input** (`frontend/`):
   - `TagInput.tsx` reusable component supporting tag pills, removal, and optional skill proficiency selector.
   - `/profile` page supporting full academic background editing, opportunity type toggles, work mode toggles, location tags, skill tags, and interest tags.
   - Updated `page.tsx` with direct link to profile management when signed in.
   - 4 Vitest tests covering profile API client methods (`frontend/__tests__/profile.test.ts`).

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

# Create virtual environment (if not already created)
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations to latest version
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
All **23 tests** will pass:
- 4 Health check tests (`tests/test_health.py`)
- 2 Config loading tests (`tests/test_config.py`)
- 10 Auth & security tests (`tests/test_auth.py`)
- 7 Profile & preferences tests (`tests/test_users.py`)

### 4. Frontend Setup
In a new terminal:
```bash
cd frontend

# Install dependencies
npm install

# Run frontend dev server
npm run dev
```
- Web Application: [http://localhost:3000](http://localhost:3000)
- Sign In: [http://localhost:3000/login](http://localhost:3000/login)
- Sign Up: [http://localhost:3000/signup](http://localhost:3000/signup)
- Student Profile: [http://localhost:3000/profile](http://localhost:3000/profile)

### 5. Run Frontend Tests
In `frontend/`:
```bash
npm test
```
All **12 tests** will pass:
- 3 API client & health check tests (`__tests__/api.test.ts`)
- 5 Auth storage & authentication tests (`__tests__/auth.test.ts`)
- 4 Profile management API tests (`__tests__/profile.test.ts`)

---

## Next Step: Phase 4 — Opportunity CRUD & Discovery

The next milestone is implementing opportunity data models and discovery APIs (FR-02, FR-03, FR-07):
1. Create `Opportunity`, `OpportunitySkill`, `Source`, `OpportunitySource` SQLAlchemy models.
2. Generate Alembic migration `003_create_opportunity_tables`.
3. Create Pydantic schemas for Opportunity create, detail, list query filters, and pagination.
4. Implement `OpportunityService`:
   - Admin opportunity creation with skill requirements and source provenance.
   - Filterable opportunity discovery (`type`, `work_mode`, `location`, `organization`, `search`, `min_cgpa`).
   - Opportunity detail retrieval by ID.
5. Create Opportunity Router (`backend/app/routers/opportunities.py`):
   - `GET /api/opportunities` — search, filter, paginate
   - `GET /api/opportunities/{id}` — single opportunity detail
   - `POST /api/opportunities` — admin-only opportunity creation
6. Create database seeding script (`backend/scripts/seed_opportunities.py`) with realistic sample opportunities (internships, hackathons, case competitions, fellowships).
7. Create Discover page (`/discover`) with search bar, filter sidebar, and opportunity cards.
8. Add unit and integration tests for opportunity CRUD, search, and filtering.
