# CampusOS — Continuation & Execution Guide

CampusOS is an opportunity intelligence platform for university students built as a modular monolith:
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy + Alembic + PostgreSQL (pgvector)
- **Frontend:** Next.js 15 (App Router) + TypeScript + Tailwind CSS
- **Testing:** Pytest (backend) + Vitest (frontend)

---

## Current Status: Phase 5 (Deterministic Eligibility Engine) Complete

The platform now features a deterministic, rule-based qualification checker (PRD FR-04) that evaluates hard academic constraints before recommendation ranking, producing transparent, human-readable explanations.

### What Was Built in Phase 5:
1. **Eligibility Engine Service** (`backend/app/services/eligibility.py`):
   - Tri-state qualification decision:
     - `eligible`: All known qualification criteria satisfied
     - `ineligible`: One or more hard qualification rules failed (e.g. CGPA cutoff, graduation year, degree, branch)
     - `uncertain`: Missing required student profile data or opportunity criteria
   - Evaluates:
     - Minimum CGPA thresholds with numeric comparison
     - Graduation year batch matching
     - Current year of study matching
     - Degree level matching (e.g., B.Tech, B.S., M.S.)
     - Branch / discipline matching with synonym normalization (e.g. "Computer Science & Engineering" matches "Computer Science")
   - Generates human-readable explanations for every evaluated requirement.
2. **Opportunity API Integration** (`backend/app/schemas/opportunity.py`, `backend/app/services/opportunity.py`, `backend/app/routers/opportunities.py`):
   - Attached `eligibility_evaluation` (status, reasons, missing data) to `OpportunityRead` in list responses and `OpportunityDetail` in detail responses.
   - Automatically resolves authenticated student context from `current_user` to provide real-time eligibility evaluation on all feeds.
3. **Automated Backend Tests** (`backend/tests/test_eligibility.py`):
   - 9 comprehensive unit and integration tests covering fully qualified students, CGPA cutoff rejections, graduation batch mismatches, discipline mismatches and synonym matches, uncertain results on missing profile fields, and full API integration. Total backend tests: **37 passing**.
4. **Frontend Eligibility Badges & Detailed Breakdown** (`frontend/`):
   - `OpportunityCard.tsx`: Displays real-time status pills (`✓ Eligible`, `✕ Ineligible`, `? Needs Info`) with tooltip reasons.
   - `/opportunities/[id]` page: Features dedicated eligibility breakdown card showing passed/failed bullet points and callouts for missing profile information with direct link to `/profile`.
   - 3 Vitest tests verifying badge rendering for all three status states (`frontend/__tests__/eligibility.test.ts`). Total frontend tests: **18 passing**.

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
All **37 tests** will pass:
- 4 Health check tests (`tests/test_health.py`)
- 2 Config loading tests (`tests/test_config.py`)
- 10 Auth & security tests (`tests/test_auth.py`)
- 7 Profile & preferences tests (`tests/test_users.py`)
- 5 Opportunity CRUD & discovery tests (`tests/test_opportunities.py`)
- 9 Deterministic eligibility engine tests (`tests/test_eligibility.py`)

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
All **18 tests** will pass:
- 3 API client & health check tests (`__tests__/api.test.ts`)
- 5 Auth storage & authentication tests (`__tests__/auth.test.ts`)
- 4 Profile management API tests (`__tests__/profile.test.ts`)
- 3 Opportunity search & detail tests (`__tests__/opportunities.test.ts`)
- 3 Eligibility badge rendering tests (`__tests__/eligibility.test.ts`)

---

## Next Step: Phase 6 — Embeddings & Vector Search Foundation

The next milestone introduces semantic similarity matching using vector embeddings (PRD FR-05, TECH_STACK §4):
1. Configure `pgvector` extension in PostgreSQL migration `004_add_vector_embeddings`.
2. Add `embedding` vector column (1536 dimensions) to `opportunities` and `users` (or a dedicated profile embedding model).
3. Create `backend/app/services/embedding.py`:
   - Text representation builder for opportunities (`title + organization + description + skills`).
   - Text representation builder for user profiles (`degree + branch + skills + interests + preferred opportunity types`).
   - Mock/Ollama/OpenAI embedding generator interface with graceful fallback.
4. Implement vector indexing: HNSW index on opportunity embedding column.
5. Create opportunity embedding backfill script (`scripts/generate_embeddings.py`).
6. Write unit tests for embedding text serialization, dimension validation, and vector cosine similarity queries.
