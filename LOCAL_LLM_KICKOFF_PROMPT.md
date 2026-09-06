# Local LLM Kickoff Prompt --- CampusOS

You are the lead software engineer responsible for starting the CampusOS
project.

I have provided three project specification files:

1.  `PRD.md` --- product requirements and scope
2.  `DESIGN.md` --- UX, architecture, data flow, API and ERD
3.  `TECH_STACK.md` --- technical stack and engineering rules

Your first task is NOT to blindly generate the entire application.

Your task is to analyze these three documents, identify dependencies and
ambiguities, and then create a practical implementation plan that can be
executed incrementally.

## Instructions

### Step 1 --- Analyze the specifications

Read all three files completely.

Produce:

-   Product summary
-   Core user journey
-   MVP feature list
-   Architecture summary
-   Database entities
-   API surface
-   External dependencies
-   AI/NLP components
-   Testing requirements
-   Deployment requirements

Identify conflicts between the files.

If something is ambiguous, state the ambiguity and make a reasonable
engineering assumption. Do not silently invent major requirements.

### Step 2 --- Establish the MVP boundary

Separate requirements into:

``` text
MUST HAVE — MVP
SHOULD HAVE — post-MVP
COULD HAVE — future
DO NOT BUILD YET
```

Do not expand the scope unless a requirement is necessary for the MVP to
work.

### Step 3 --- Design the repository

Propose the exact initial repository structure based on `TECH_STACK.md`.

Include:

-   frontend directories
-   backend directories
-   database/migrations
-   tests
-   evaluation
-   documentation

### Step 4 --- Design the database

Translate the ERD into PostgreSQL/SQLAlchemy models.

For every table specify:

-   columns
-   data types
-   primary keys
-   foreign keys
-   indexes
-   unique constraints
-   nullable/non-nullable fields

Pay special attention to:

-   user/opportunity relationships
-   application history
-   source provenance
-   recommendation score breakdown
-   vector embeddings

### Step 5 --- Design the API

Create an API contract for the MVP.

For each endpoint specify:

-   method
-   path
-   authentication requirement
-   request body
-   response body
-   validation
-   likely errors

Do not create endpoints that are not justified by the PRD.

### Step 6 --- Implementation sequence

Create a dependency-aware sequence such as:

``` text
Phase 1
Project setup
    ↓
Database
    ↓
Authentication
    ↓
User profile
    ↓
Opportunity CRUD
    ↓
Search/filter
    ↓
Eligibility
    ↓
Recommendation
    ↓
Application tracker
    ↓
Ingestion
    ↓
Evaluation
    ↓
Deployment
```

Break each phase into small tasks that can be implemented and tested
independently.

### Step 7 --- Start coding

After producing the plan, begin with Phase 1 only.

Do not generate the entire project in one response.

For the first implementation:

1.  Create the repository structure.
2.  Create the backend skeleton.
3.  Create the frontend skeleton.
4.  Configure environment variables.
5.  Configure PostgreSQL.
6.  Configure migrations.
7.  Add a health-check endpoint.
8.  Add a minimal frontend page that confirms the frontend/backend
    connection.
9.  Add initial tests.
10. Explain how to run everything locally.

### Engineering constraints

Follow these rules strictly:

-   Use Next.js + TypeScript for frontend.
-   Use Python + FastAPI for backend.
-   Use PostgreSQL + pgvector.
-   Use SQLAlchemy + Alembic.
-   Keep the backend modular.
-   Use a modular monolith.
-   Do not introduce microservices.
-   Do not add Kubernetes.
-   Do not build a mobile app.
-   Do not make the LLM the core of the application.
-   Never allow model output to bypass validation.
-   Never fabricate opportunity information.
-   Preserve source provenance.
-   Keep secrets in environment variables.
-   Write tests for important business logic.
-   Prefer deterministic logic before AI logic.

### Important AI rule

The LLM may help extract structured opportunity information and generate
explanations.

It must NOT be the authoritative source for eligibility.

Eligibility should be determined from structured requirements and
deterministic rules whenever possible.

### Code quality

Write code that a strong software engineering student could explain in
an interview.

Avoid:

-   unnecessary abstractions
-   huge files
-   magic constants
-   duplicated business logic
-   unexplained dependencies
-   premature optimization

Use clear names and type hints.

### When you finish Phase 1

Stop.

Report:

-   files created
-   architecture implemented
-   commands to run
-   tests added
-   known issues
-   exact next step

Then wait for the next instruction.

## Output format

Use this structure:

``` text
# Specification Analysis

# MVP Boundary

# Architecture

# Database Plan

# API Plan

# Implementation Roadmap

# Phase 1 Implementation

# How to Run

# Tests

# Known Issues

# Next Step
```

The goal is to build CampusOS as a real, testable product---not as a
large generated code dump.
