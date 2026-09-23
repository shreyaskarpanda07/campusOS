# CampusOS — Continuation & Execution Guide

CampusOS is an opportunity intelligence platform for university students built as a modular monolith:
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy + Alembic + PostgreSQL (pgvector)
- **Frontend:** Next.js 15 (App Router) + TypeScript + Tailwind CSS
- **Testing:** Pytest (backend) + Vitest (frontend)

---

## Current Status: Phase 4 (Opportunity CRUD & Discovery) Complete

The platform now features complete opportunity management, database models, provenance tracking, seeding, full-text search, multi-faceted filtering, and a responsive discovery UI.

### What Was Built in Phase 4:
1. **Opportunity & Source SQLAlchemy Models** (`backend/app/models/`):
   - `Opportunity`: Stores structured records (title, organization, type, description, deadlines, locations, work modes, CGPA, eligibility JSON, compensation, URL, status, confidence).
   - `OpportunitySkill`: Junction table linking required and preferred skills to opportunities.
   - `Source`: Ingestion source registry (name, base URL, source type).
   - `OpportunitySource`: Preserves source provenance and origin URL for every opportunity.
2. **Alembic Migration** (`backend/migrations/versions/003_create_opportunity_tables.py`):
   - Creates `opportunities`, `sources`, `opportunity_skills`, and `opportunity_sources` tables with appropriate indexes on organization, type, deadline, and status.
3. **Pydantic Schemas** (`backend/app/schemas/opportunity.py`):
   - `OpportunityCreateRequest`, `OpportunityRead`, `OpportunityDetail`, `OpportunitySkillItem`, `OpportunitySkillRead`, `OpportunitySourceRead`, `OpportunityListResponse`, `PaginationMeta`.
4. **Opportunity Service Layer** (`backend/app/services/opportunity.py`):
   - `create_opportunity`: Admin opportunity creation with automatic skill canonicalization and source provenance linking. Guarantees unknown fields remain null (FR-03).
   - `get_opportunity_by_id`: Comprehensive detail retrieval with skills and sources.
   - `list_opportunities`: Multi-parameter search across title, organization, description, with type, work mode, location, and CGPA filtering, ordered by urgency (deadline ascending).
5. **Opportunity API Router** (`backend/app/routers/opportunities.py`):
   - `GET /api/opportunities` — search, filter, and paginate.
   - `GET /api/opportunities/{id}` — detailed view.
   - `POST /api/opportunities` — administrator-only creation endpoint.
6. **Realistic Database Seeding Script** (`backend/scripts/seed_opportunities.py`):
   - Seeds Google, Microsoft Research, Stripe, Deloitte, HackMIT, and GSoC opportunities across internships, hackathons, competitions, fellowships, and scholarships.
7. **Backend Opportunity Tests** (`backend/tests/test_opportunities.py`):
   - 5 unit and integration tests covering admin creation protection (403 for students, 401 for anonymous), detail lookup (200 & 404), multi-faceted filtering, and pagination.
8. **Frontend Discovery UI & Components** (`frontend/`):
   - `OpportunityCard.tsx`: Displays category badge, deadline urgency countdown, title, organization, work mode, location, compensation, skills pills, and direct apply link.
   - `/discover` page: Features keyword search, category filter pills (Internships, Hackathons, Competitions, etc.), work mode dropdown, result counters, grid layout, and pagination.
   - `/opportunities/[id]` page: Detailed view showing full overview, required vs. preferred skills breakdown, academic eligibility criteria, and source provenance.
   - Updated `page.tsx` home screen with direct button to Discover Opportunities.
   - 3 Vitest tests covering opportunity search and detail API methods (`frontend/__tests__/opportunities.test.ts`).

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

# Seed sample opportunities
python scripts/seed_opportunities.py

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
All **28 tests** will pass:
- 4 Health check tests (`tests/test_health.py`)
- 2 Config loading tests (`tests/test_config.py`)
- 10 Auth & security tests (`tests/test_auth.py`)
- 7 Profile & preferences tests (`tests/test_users.py`)
- 5 Opportunity CRUD & discovery tests (`tests/test_opportunities.py`)

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
- Discover Opportunities: [http://localhost:3000/discover](http://localhost:3000/discover)
- Student Profile: [http://localhost:3000/profile](http://localhost:3000/profile)

### 5. Run Frontend Tests
In `frontend/`:
```bash
npm test
```
All **15 tests** will pass:
- 3 API client & health check tests (`__tests__/api.test.ts`)
- 5 Auth storage & authentication tests (`__tests__/auth.test.ts`)
- 4 Profile management API tests (`__tests__/profile.test.ts`)
- 3 Opportunity search & detail tests (`__tests__/opportunities.test.ts`)

---

## Next Step: Phase 5 — Deterministic Eligibility Engine

The next milestone is implementing the deterministic eligibility evaluation engine (PRD FR-04):
1. Create `backend/app/services/eligibility.py`:
   - Evaluates hard constraints before recommendation ranking:
     - Graduation year match
     - Current year match
     - Degree / Branch match
     - Minimum CGPA threshold
     - Geographic / location eligibility
   - Returns tri-state result: `eligible`, `ineligible`, or `uncertain`
   - Generates transparent, human-readable reasons (e.g. "Eligible: Meets minimum CGPA (8.5 >= 7.5) and graduation year 2027").
2. Integrate eligibility evaluation into `OpportunityRead` / detail payload for authenticated student requests.
3. Show eligibility status badges (`✓ Eligible`, `✕ Ineligible`, `? Uncertain`) directly on `OpportunityCard` and detail page.
4. Add unit tests for all eligibility boundary cases (missing fields, edge year ranges, branch synonyms, CGPA cutoffs).
