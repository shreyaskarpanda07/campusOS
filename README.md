# CampusOS

Personalized opportunity intelligence platform for university students.

## Overview

CampusOS aggregates opportunities (internships, competitions, hackathons, fellowships, scholarships) from multiple sources, normalizes them into structured records, determines eligibility using deterministic rules, ranks them with a weighted scoring system, and lets students track applications.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15 + TypeScript + Tailwind CSS |
| Backend | Python 3.12 + FastAPI |
| Database | PostgreSQL + pgvector |
| ORM | SQLAlchemy + Alembic |
| Testing | Pytest (backend) · Vitest (frontend) |

## Project Structure

```
campusos/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── evaluation/        # Evaluation datasets and scripts
├── docs/              # Project documentation
├── docker-compose.yml # Local development services
└── .env.example       # Environment variable template
```

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 15+ with pgvector extension
- Git

### 1. Clone and configure

```bash
git clone https://github.com/shreyaskarpanda07/campusOS.git
cd campusOS
cp .env.example .env
# Edit .env with your database credentials
```

### 2. Start PostgreSQL

```bash
docker compose up -d postgres
```

Or use an existing PostgreSQL instance and update `DATABASE_URL` in `.env`.

### 3. Backend

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Backend runs at: http://localhost:8000  
API docs at: http://localhost:8000/docs

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:3000

### 5. Verify

- **Health check:** `curl http://localhost:8000/api/health`
- **Frontend:** Open http://localhost:3000 — should show backend connection status

### 6. Run tests

```bash
# Backend tests
cd backend
pytest -v

# Frontend tests
cd frontend
npm test
```

## Documentation

- [PRD](docs/PRD.md) — Product requirements
- [DESIGN](docs/DESIGN.md) — UX and system design
- [TECH_STACK](docs/TECH_STACK.md) — Technical stack and guidelines

## License

Private — All rights reserved.
