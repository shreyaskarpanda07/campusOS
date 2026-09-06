# CampusOS — Phase 1 Continuation Guide

Follow these steps **in order** to get the project running locally.

---

## 1. Backend Setup

Open a terminal in the `backend/` folder:

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Database Setup

Make sure Docker is running, then from the **project root**:

```bash
docker compose up -d postgres
```

This starts PostgreSQL 16 with pgvector on `localhost:5432`.  
Credentials: `campusos` / `campusos` / database `campusos`.

If you already have PostgreSQL installed locally, create the database manually:

```sql
CREATE DATABASE campusos;
CREATE USER campusos WITH PASSWORD 'campusos';
GRANT ALL PRIVILEGES ON DATABASE campusos TO campusos;
```

## 3. Environment Variables

From the project root:

```bash
cp .env.example backend/.env
```

Edit `backend/.env` if your database credentials differ from the defaults.

## 4. Run Alembic Migrations

```bash
cd backend
alembic upgrade head
```

> **Note:** Phase 1 has no models yet, so this will just verify the connection.  
> The first real migration will be created in Phase 2 (Authentication).

## 5. Start the Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Verify: open [http://localhost:8000/api/health](http://localhost:8000/api/health)  
Expected response:

```json
{
  "data": {
    "status": "healthy",
    "database": "connected",
    "version": "0.1.0"
  },
  "error": null
}
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## 6. Run Backend Tests

```bash
cd backend
pytest -v
```

Expected output:

```
tests/test_config.py::test_default_settings PASSED
tests/test_config.py::test_cors_origins_default PASSED
tests/test_health.py::test_health_returns_200 PASSED
tests/test_health.py::test_health_response_shape PASSED
tests/test_health.py::test_health_data_fields PASSED
tests/test_health.py::test_health_database_connected PASSED
```

## 7. Frontend Setup

Open a **new** terminal in the `frontend/` folder:

```bash
cd frontend

# Copy env template
cp .env.local.example .env.local

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).  
You should see the CampusOS landing page with three green status indicators:
- **Backend** — v0.1.0
- **Database** — connected
- **Frontend** — Running

## 8. Run Frontend Tests

```bash
cd frontend
npm test
```

Expected: 3 tests passing (fetchHealth success, error handling, URL construction).

---

## What Was Built (Phase 1)

### Git Commits (all pushed to GitHub)

| # | Commit | Description |
|---|--------|-------------|
| 1 | `chore: initialize repository with root config files and docs` | .gitignore, .env.example, docker-compose.yml, README.md, docs/, evaluation/ |
| 2 | `feat: add backend skeleton with FastAPI, SQLAlchemy, Alembic, and health check` | 25 files — full backend structure |
| 3 | `feat: add frontend skeleton with Next.js, Tailwind CSS, and health status page` | 15 files — full frontend structure |

### Files Created

```
Root (5 files)
├── README.md              — Project overview + setup instructions
├── .gitignore             — Python, Node, env, IDE exclusions
├── .env.example           — Environment variable template
├── docker-compose.yml     — PostgreSQL + pgvector container
└── docs/                  — PRD.md, DESIGN.md, TECH_STACK.md

Backend (25 files)
├── requirements.txt       — Pinned Python dependencies
├── alembic.ini            — Alembic config
├── app/
│   ├── main.py            — FastAPI app factory with CORS
│   ├── core/
│   │   ├── config.py      — Pydantic Settings from env
│   │   ├── security.py    — Placeholder (Phase 2)
│   │   └── dependencies.py — DB session dependency
│   ├── db/
│   │   ├── session.py     — SQLAlchemy engine + SessionLocal
│   │   └── base.py        — Declarative Base + TimestampMixin
│   ├── models/            — Empty (Phase 2)
│   ├── schemas/
│   │   └── common.py      — ApiResponse + ErrorDetail
│   ├── routers/
│   │   └── health.py      — GET /api/health
│   ├── services/          — Empty (Phase 2)
│   └── workers/           — Empty (Phase 9)
├── migrations/
│   ├── env.py             — Alembic env with settings integration
│   ├── script.py.mako     — Migration template
│   └── versions/          — Empty (Phase 2)
└── tests/
    ├── conftest.py        — SQLite test DB + TestClient fixtures
    ├── test_health.py     — 4 health endpoint tests
    └── test_config.py     — 2 config loading tests

Frontend (15 files)
├── package.json           — Next.js 15 + React 19 + Tailwind + Vitest
├── tsconfig.json          — Strict TS with @/ alias
├── next.config.ts         — Minimal Next.js config
├── tailwind.config.ts     — Blue primary palette
├── postcss.config.mjs     — Tailwind + Autoprefixer
├── vitest.config.ts       — jsdom + @/ alias
├── .env.local.example     — NEXT_PUBLIC_API_URL
├── app/
│   ├── globals.css        — Tailwind + light/dark vars
│   ├── layout.tsx         — Root layout with metadata
│   └── page.tsx           — Landing page + health status
├── lib/
│   ├── api.ts             — fetchHealth API client
│   └── types.ts           — Shared TS types
├── components/
│   ├── ui/                — Empty (Phase 3+)
│   └── features/          — Empty (Phase 3+)
└── __tests__/
    └── api.test.ts        — 3 API client tests
```

### Architecture Implemented

```
Browser → Next.js (port 3000)
              │
              │  fetch("/api/health")
              ▼
         FastAPI (port 8000)
              │
              │  SELECT 1
              ▼
         PostgreSQL (port 5432)
```

---

## Known Issues

1. **CRLF warnings** — Git shows LF→CRLF warnings on Windows. Harmless.
2. **No real DB models yet** — Alembic has no migrations; the first migration will come with the User model in Phase 2.
3. **SQLite test DB** — Tests use in-memory SQLite for speed. PostgreSQL-specific features (JSONB, pgvector) will need a separate integration test setup later.
4. **No auth yet** — All endpoints are unauthenticated. Phase 2 adds JWT.

---

## Next Step: Phase 2 — Authentication

The exact next implementation step is:

1. Create the `User` SQLAlchemy model (`backend/app/models/user.py`)
2. Generate the first Alembic migration
3. Implement password hashing with bcrypt (`security.py`)
4. Implement JWT token generation and validation
5. Create `POST /api/auth/register` endpoint
6. Create `POST /api/auth/login` endpoint
7. Create `POST /api/auth/logout` endpoint
8. Add auth dependency for protected routes
9. Write auth tests
10. Create basic login/signup frontend pages

**Tell me to start Phase 2 when you're ready.**
