# CampusOS --- Technical Stack & Engineering Guidelines

## 1. Stack Summary

  --------------------------------------------------------------------------
  Layer                   Technology              Purpose
  ----------------------- ----------------------- --------------------------
  Frontend                Next.js + TypeScript    Web application

  UI                      Tailwind CSS + reusable Design system
                          components              

  Backend                 Python + FastAPI        REST API

  Database                PostgreSQL              Primary relational store

  Vector search           pgvector                Semantic retrieval

  ORM                     SQLAlchemy              Database access

  Validation              Pydantic                API/data validation

  Migrations              Alembic                 Schema migrations

  Background jobs         Celery + Redis, or      Ingestion/recommendation
                          lightweight worker      jobs
                          initially               

  AI/NLP                  LLM API + embeddings    Extraction and semantic
                                                  matching

  Testing                 Pytest + Playwright     Backend + end-to-end
                                                  testing

  Frontend testing        Vitest/React Testing    Component/unit testing
                          Library                 

  Containerization        Docker                  Reproducible development

  CI                      GitHub Actions          Automated checks

  Deployment              Vercel + managed        Initial production
                          Python/Postgres hosting deployment
  --------------------------------------------------------------------------

------------------------------------------------------------------------

## 2. Architecture Principle

Use a **modular monolith**.

``` text
campusos/
├── frontend/
└── backend/
    ├── auth/
    ├── users/
    ├── opportunities/
    ├── eligibility/
    ├── recommendations/
    ├── applications/
    ├── ingestion/
    ├── database/
    └── shared/
```

Avoid microservices until there is a demonstrated reason.

------------------------------------------------------------------------

## 3. Backend

### Python

Use Python for:

-   ingestion
-   parsing
-   NLP
-   recommendation logic
-   APIs
-   evaluation scripts

Target Python 3.12+ unless a dependency requires otherwise.

### FastAPI

Use:

-   routers for modules
-   dependency injection for authentication/database
-   Pydantic models for request/response validation
-   async endpoints where they provide actual benefit

Do not put business logic directly inside route handlers.

Bad:

``` python
@app.get("/recommendations")
def recommendations():
    # 200 lines of logic
```

Better:

``` text
router
  ↓
service
  ↓
repository
```

------------------------------------------------------------------------

## 4. Database

Use PostgreSQL.

Recommended extensions:

-   pgvector
-   uuid support as needed

Use relational tables for structured data.

Use JSONB only for genuinely flexible structures such as:

-   extracted eligibility details
-   score breakdowns
-   model metadata

Do not put the entire application schema into JSONB.

------------------------------------------------------------------------

## 5. Embeddings

Store embeddings using pgvector.

Use embeddings for:

-   opportunity description
-   skills
-   student profile representation

Do not assume embedding similarity alone equals recommendation quality.

Use it for candidate generation, then combine it with deterministic
features.

------------------------------------------------------------------------

## 6. Recommendation Engine

Initial architecture:

``` text
Candidate retrieval
        ↓
Eligibility filter
        ↓
Feature extraction
        ↓
Weighted scoring
        ↓
Top-K ranking
        ↓
Explanation
```

Example features:

``` python
skill_match
interest_match
eligibility_score
deadline_urgency
type_preference
```

Keep scoring code separate and unit-testable.

------------------------------------------------------------------------

## 7. AI Usage

AI is allowed for:

### Good use cases

-   Extracting structured fields from opportunity text
-   Normalizing skill names
-   Generating concise opportunity summaries
-   Producing explanation text from already-computed evidence

### Bad use cases

-   Deciding eligibility without deterministic checks
-   Inventing deadlines
-   Inventing compensation
-   Generating unsupported requirements
-   Replacing the database
-   Acting as the entire backend

The application should remain useful if the LLM is temporarily
unavailable.

------------------------------------------------------------------------

## 8. Structured Extraction

Prefer a schema-constrained extraction response.

Example:

``` json
{
  "title": "...",
  "organization": "...",
  "deadline": "...",
  "minimum_cgpa": 7.5,
  "eligible_years": [2027, 2028],
  "eligible_branches": ["all engineering"],
  "required_skills": ["python", "sql"],
  "location": "...",
  "work_mode": "...",
  "confidence": 0.94
}
```

Validate every field.

If the model cannot determine a field, use `null` rather than a guess.

------------------------------------------------------------------------

## 9. Ingestion Pipeline

Each source should have an adapter.

``` text
SourceAdapter
   ↓
fetch()
   ↓
extract_content()
   ↓
parse()
   ↓
normalize()
   ↓
validate()
   ↓
deduplicate()
   ↓
persist()
```

Do not write one giant scraper.

Each source can implement a common interface.

------------------------------------------------------------------------

## 10. Deduplication

Start with deterministic matching:

1.  Canonicalized application URL
2.  Source URL
3.  Organization + title
4.  Deadline + normalized title

Later add fuzzy/embedding matching.

Always keep source provenance.

------------------------------------------------------------------------

## 11. Security

### Secrets

Use environment variables:

``` text
DATABASE_URL
SECRET_KEY
LLM_API_KEY
REDIS_URL
```

Never commit `.env`.

Commit `.env.example`.

### Authentication

Use secure password hashing.

Use short-lived access tokens or secure session cookies.

Validate authorization on every private resource.

------------------------------------------------------------------------

## 12. API Conventions

Use consistent JSON.

Example:

``` json
{
  "data": {},
  "error": null
}
```

For errors:

``` json
{
  "data": null,
  "error": {
    "code": "OPPORTUNITY_NOT_FOUND",
    "message": "Opportunity not found"
  }
}
```

Use appropriate HTTP status codes.

------------------------------------------------------------------------

## 13. Testing Strategy

### Unit tests

Test:

-   eligibility rules
-   scoring
-   deadline urgency
-   normalization
-   deduplication
-   validation

### Integration tests

Test:

-   database operations
-   recommendation API
-   application workflow
-   ingestion pipeline

### End-to-end

At minimum:

``` text
register
→ profile
→ recommendation
→ save
→ apply
→ update status
```

------------------------------------------------------------------------

## 14. Evaluation

Create a manually labeled evaluation dataset.

Example:

``` text
20 student profiles
100 opportunities
```

Label:

-   eligible/ineligible
-   relevant/not relevant

Measure:

### Eligibility

``` text
accuracy
precision
recall
F1
```

### Recommendation

``` text
Precision@5
Precision@10
Recall@10
NDCG@10
```

### Extraction

Measure field-level accuracy.

Do not claim ML performance without an evaluation set.

------------------------------------------------------------------------

## 15. Observability

Log:

-   request latency
-   ingestion failures
-   extraction failures
-   recommendation generation time
-   model errors
-   database errors

Each ingestion job should have a status:

``` text
PENDING
RUNNING
SUCCESS
PARTIAL
FAILED
```

------------------------------------------------------------------------

## 16. Git Workflow

Recommended branches:

``` text
main
develop
feature/*
fix/*
```

Commit examples:

``` text
feat: add opportunity ingestion pipeline
feat: implement eligibility engine
fix: handle missing deadlines
test: add recommendation scoring tests
```

Keep commits focused.

------------------------------------------------------------------------

## 17. Environment Setup

Use Docker Compose for local infrastructure where practical.

Expected local services:

``` text
frontend
backend
postgres
redis
```

If Redis is not needed initially, do not add it merely for architectural
aesthetics.

------------------------------------------------------------------------

## 18. CI Pipeline

Every pull request should run:

``` text
lint
type check
unit tests
backend tests
frontend tests
build
```

Do not allow broken tests to merge into `main`.

------------------------------------------------------------------------

## 19. Recommended Repository Structure

``` text
campusos/
├── README.md
├── .env.example
├── docker-compose.yml
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── tests/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   └── workers/
│   └── tests/
│
├── evaluation/
│   ├── datasets/
│   ├── scripts/
│   └── reports/
│
└── docs/
```

------------------------------------------------------------------------

## 20. Engineering Rules

1.  Do not over-engineer V1.
2.  Do not introduce microservices.
3.  Do not hard-code user-specific recommendation logic.
4.  Do not mix database code with UI code.
5.  Do not let LLM output bypass validation.
6.  Never fabricate opportunity information.
7.  Preserve source URLs.
8.  Write tests for recommendation and eligibility logic.
9.  Measure system quality before optimizing it.
10. Prefer simple working code over architectural complexity.

------------------------------------------------------------------------

## 21. Definition of Done

A feature is done only when:

-   implementation exists,
-   API/UI behavior works,
-   validation exists,
-   tests exist for important logic,
-   error states are handled,
-   documentation is updated,
-   no secrets are committed.

------------------------------------------------------------------------

## 22. Resume/Portfolio Standard

The final project should demonstrate:

-   full-stack development,
-   database design,
-   data ingestion,
-   NLP/LLM integration,
-   recommendation systems,
-   API design,
-   testing,
-   evaluation,
-   deployment.

The portfolio should show actual metrics and architecture diagrams
rather than generic claims such as "AI-powered platform."
