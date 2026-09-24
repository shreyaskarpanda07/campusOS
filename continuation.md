# CampusOS — Continuation & Execution Guide

CampusOS is an opportunity intelligence platform for university students built as a modular monolith:
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy + Alembic + PostgreSQL (pgvector)
- **Frontend:** Next.js 15 (App Router) + TypeScript + Tailwind CSS
- **Testing:** Pytest (backend) + Vitest (frontend)

---

## Current Status: Phase 6 (Embeddings & Vector Search Foundation) Complete

The platform now features full semantic retrieval support using 1536-dimensional vector embeddings and pgvector (PRD FR-05, TECH_STACK §4-§5), with cross-database fallback for testing.

### What Was Built in Phase 6:
1. **Model & Database Vector Support** (`backend/app/models/opportunity.py`, `backend/app/models/user.py`, `backend/migrations/versions/004_add_vector_embeddings.py`):
   - Added `embedding` column of type `Vector(1536)` with `.with_variant(JSON(), "sqlite")` to `opportunities` and `users` tables.
   - Alembic migration enabling PostgreSQL `vector` extension and creating an HNSW cosine index (`idx_opportunities_embedding USING hnsw (embedding vector_cosine_ops)`).
2. **Embedding Service** (`backend/app/services/embedding.py`):
   - Text serializers:
     - `build_opportunity_text`: Formats title, organization, type, description, work mode, location, required/preferred skills, and academic eligibility requirements.
     - `build_profile_text`: Formats degree, branch, university, academic year, skills with proficiency levels, interests, and preferences.
   - Embedding generator (`generate_embedding`):
     - Unit-normalized 1536-dimensional float vector generator.
     - Deterministic token-hashing generator using n-grams, subwords, log-TF weighting, and SHA-256 projections to guarantee offline reproducibility without external API keys.
     - Optional OpenAI API integration fallback if `OPENAI_API_KEY` is present.
   - Vector search:
     - `compute_cosine_similarity`: Unit-vector dot product calculation.
     - `find_similar_opportunities`: High-performance cosine distance query using pgvector `<=>` on PostgreSQL, with in-memory SQLite fallback for test execution.
   - Integrated automatic opportunity embedding generation into `OpportunityService.create_opportunity`.
3. **Embeddings Backfill Utility** (`backend/scripts/generate_embeddings.py`):
   - CLI utility with `--force` and `--batch-size` options to populate embeddings for existing opportunities and user profiles.
4. **Backend Automated Tests** (`backend/tests/test_embeddings.py`):
   - 11 new unit and integration tests covering text representation formatting, 1536 dimension validation, unit L2 normalization, deterministic reproducibility, semantic separation, vector persistence, similar opportunity ranking, and backfill logic.
   - **Total Backend Tests: 48 passing**.
   - **Total Frontend Tests: 18 passing**.

---

## Local Development Instructions

### 1. Database Setup
Start PostgreSQL with pgvector via Docker from the project root:
```bash
docker compose up -d postgres
```
Database credentials: `campusos` / `campusos` on port `5432`.

### 2. Backend Setup
```bash
cd backend

# Create virtual environment (if not already created)
uv venv --python 3.13

# Install dependencies
uv pip install -r requirements.txt

# Run migrations to latest version
alembic upgrade head

# Seed sample opportunities
python scripts/seed_opportunities.py

# Backfill vector embeddings (if needed)
python scripts/generate_embeddings.py

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 3. Run Backend Tests
In `backend/`:
```bash
.\.venv\Scripts\pytest.exe -v
```
All **48 tests** will pass:
- 4 Health check tests (`tests/test_health.py`)
- 2 Config loading tests (`tests/test_config.py`)
- 10 Auth & security tests (`tests/test_auth.py`)
- 7 Profile & preferences tests (`tests/test_users.py`)
- 5 Opportunity CRUD & discovery tests (`tests/test_opportunities.py`)
- 9 Deterministic eligibility engine tests (`tests/test_eligibility.py`)
- 11 Vector embeddings & similarity search tests (`tests/test_embeddings.py`)

### 4. Frontend Setup
In a new terminal:
```bash
cd frontend

# Install dependencies
npm.cmd install

# Run frontend dev server
npm.cmd run dev
```
- Web Application: [http://localhost:3000](http://localhost:3000)
- Discover Opportunities: [http://localhost:3000/discover](http://localhost:3000/discover)
- Student Profile: [http://localhost:3000/profile](http://localhost:3000/profile)

### 5. Run Frontend Tests
In `frontend/`:
```bash
npm.cmd test
```
All **18 tests** will pass:
- 3 API client & health check tests (`__tests__/api.test.ts`)
- 5 Auth storage & authentication tests (`__tests__/auth.test.ts`)
- 4 Profile management API tests (`__tests__/profile.test.ts`)
- 3 Opportunity search & detail tests (`__tests__/opportunities.test.ts`)
- 3 Eligibility badge rendering tests (`__tests__/eligibility.test.tsx`)

---

## Next Step: Phase 7 — Recommendation Engine & Scoring Pipeline

The next milestone is implementing the multi-factor personalized recommendation scoring pipeline (PRD FR-05, FR-06, TECH_STACK §6):
1. **Recommendation Scoring Service** (`backend/app/services/recommendation.py`):
   - Multi-factor weighted formula:
     ```
     Final Score = 0.30 × Skill Match + 0.25 × Interest Match + 0.20 × Eligibility Fit + 0.15 × Deadline Urgency + 0.10 × Opportunity-Type Preference
     ```
   - Configurable weights stored in application settings.
   - Filter pipeline: Candidates -> Deterministic Eligibility Filter -> Feature Extraction -> Scoring -> Top-K Ranking.
2. **Transparent Explanation Generator** (PRD FR-06):
   - Generates human-readable explanations from computed subscores (e.g. "92% match. You match 4 of 5 required skills (Python, PyTorch), meet the academic criteria (CGPA 8.5 >= 7.5), and have internships as a preferred category. Deadline in 5 days.").
3. **Recommendation API Router** (`backend/app/routers/recommendations.py`):
   - `GET /api/recommendations` — paginated personalized feed for authenticated student.
   - `GET /api/recommendations/top` — quick dashboard widget.
4. **Backend Recommendation Tests** (`backend/tests/test_recommendations.py`):
   - Unit tests for each scoring feature, weighted combination, explanation generation, and router endpoints.
5. **Frontend Personalized Recommendations UI**:
   - `/recommendations` or home feed showing ranked cards with match percentages, score breakdowns, and "Why this?" modals/tooltips.
