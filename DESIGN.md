# CampusOS --- Product & System Design

## 1. Design Objective

Build CampusOS as a clean, technically credible web product with a
modular architecture.

The design should communicate:

-   trustworthy opportunity data,
-   strong information hierarchy,
-   useful recommendations,
-   explainability,
-   low cognitive load.

Avoid making it look like an AI demo.

------------------------------------------------------------------------

## 2. UX Architecture

``` text
Landing
 ├── Sign in / Sign up
 └── Product explanation

Authenticated app
 ├── Dashboard
 ├── Discover
 ├── Recommended
 ├── Saved
 ├── Applications
 ├── Opportunity detail
 └── Profile / Preferences
```

------------------------------------------------------------------------

## 3. Dashboard Design

The dashboard should answer three questions immediately:

1.  What should I apply to?
2.  What deadline is approaching?
3.  What is the state of my applications?

Suggested layout:

``` text
----------------------------------------------------
CampusOS                         Profile
----------------------------------------------------

Good matches for you

[ Opportunity card ] [ Opportunity card ]
[ Opportunity card ] [ Opportunity card ]

----------------------------------------------------

Deadlines
Today       2
This week   5
Later       14

----------------------------------------------------

Application pipeline

Saved → Applied → Assessment → Interview → Offer
```

Do not overcrowd the dashboard with charts that do not support
decisions.

------------------------------------------------------------------------

## 4. Opportunity Card

Each card should contain:

-   Opportunity title
-   Organization
-   Type
-   Deadline
-   Match percentage
-   Eligibility state
-   1--2 recommendation reasons
-   Save action
-   Apply action

Example:

``` text
Deloitte Strategy Challenge
Case Competition · Remote

94% match
✓ Eligible
Deadline: 3 days

Why recommended?
• Consulting is a selected interest
• Matches case competition preference
• 4/5 relevant skills

[Save] [View Opportunity]
```

Avoid displaying a match percentage if the underlying score is not
meaningful.

------------------------------------------------------------------------

## 5. Opportunity Detail Page

Sections:

1.  Title and organization
2.  Deadline
3.  Eligibility
4.  Description
5.  Required skills
6.  Preferred skills
7.  Location/work mode
8.  Why this matches you
9.  Application source
10. Save / Track application

Always display the source/application URL.

------------------------------------------------------------------------

## 6. Application Tracker

Use a Kanban-style interface on desktop:

``` text
SAVED       APPLIED       ASSESSMENT       INTERVIEW       OFFER
-----       ------        ----------       ---------       -----
Card        Card          Card             Card            Card
Card        Card
```

On smaller screens, use a status-filtered list instead of forcing a wide
Kanban board.

------------------------------------------------------------------------

## 7. Profile Design

Organize profile into:

### Academic

-   University
-   Degree
-   Branch
-   Graduation year
-   Current year
-   CGPA

### Skills

Tag-based input.

### Interests

Tag-based input.

### Preferences

-   Opportunity type
-   Location
-   Work mode

Avoid making the profile feel like a resume editor.

------------------------------------------------------------------------

## 8. Design System

### Visual direction

-   Modern SaaS
-   Clean
-   Information-dense but not cramped
-   Neutral base palette
-   One primary accent
-   Strong typography hierarchy
-   Consistent status indicators

### Components

Create reusable components:

``` text
Button
Input
Select
Tag
Badge
OpportunityCard
DeadlineBadge
MatchScore
StatusPill
Modal
Drawer
Toast
EmptyState
Skeleton
Pagination
```

### Accessibility

-   Keyboard navigation
-   Visible focus states
-   Semantic HTML
-   Adequate contrast
-   Labels for form inputs
-   Do not communicate state only through color

------------------------------------------------------------------------

## 9. Frontend Information Architecture

Recommended routes:

``` text
/
 /login
 /signup

/app
 /app/dashboard
 /app/discover
 /app/recommended
 /app/saved
 /app/applications
 /app/opportunities/[id]
 /app/profile
```

Keep routing predictable.

------------------------------------------------------------------------

## 10. Backend Architecture

Use a modular monolith initially.

``` text
Frontend
   │
   ▼
FastAPI
   │
   ├── Auth module
   ├── Users module
   ├── Opportunities module
   ├── Eligibility module
   ├── Recommendation module
   ├── Applications module
   └── Ingestion module
          │
          ├── Source adapters
          ├── Parser
          ├── Extractor
          └── Deduplicator
   │
   ▼
PostgreSQL + pgvector
```

Do not split these modules into separate services in V1.

------------------------------------------------------------------------

## 11. Data Flow

### Ingestion

``` text
Source URL
   ↓
Fetcher
   ↓
Raw document
   ↓
Content extraction
   ↓
Structured extraction
   ↓
Validation
   ↓
Deduplication
   ↓
Opportunity DB
```

### Recommendation

``` text
User profile
   ↓
Eligibility rules
   ↓
Candidate opportunities
   ↓
Embedding similarity
   ↓
Feature calculation
   ↓
Ranking
   ↓
Recommendation explanation
   ↓
Dashboard
```

------------------------------------------------------------------------

## 12. ERD

``` mermaid
erDiagram
    USER ||--o{ USER_SKILL : has
    SKILL ||--o{ USER_SKILL : assigned
    USER ||--o{ USER_INTEREST : has
    INTEREST ||--o{ USER_INTEREST : assigned
    USER ||--o{ APPLICATION : creates
    OPPORTUNITY ||--o{ APPLICATION : receives
    OPPORTUNITY ||--o{ OPPORTUNITY_SKILL : requires
    SKILL ||--o{ OPPORTUNITY_SKILL : listed
    OPPORTUNITY ||--o{ OPPORTUNITY_SOURCE : has
    SOURCE ||--o{ OPPORTUNITY_SOURCE : provides
    OPPORTUNITY ||--o{ RECOMMENDATION : generates
    USER ||--o{ RECOMMENDATION : receives
    APPLICATION ||--o{ APPLICATION_EVENT : records

    USER {
        uuid id PK
        string email
        string name
        string university
        string degree
        string branch
        int graduation_year
        int current_year
        decimal cgpa
        timestamp created_at
        timestamp updated_at
    }

    SKILL {
        uuid id PK
        string name
    }

    USER_SKILL {
        uuid user_id FK
        uuid skill_id FK
        string proficiency
    }

    INTEREST {
        uuid id PK
        string name
    }

    USER_INTEREST {
        uuid user_id FK
        uuid interest_id FK
    }

    OPPORTUNITY {
        uuid id PK
        string title
        string organization
        string type
        text description
        date deadline
        date start_date
        string location
        string work_mode
        decimal minimum_cgpa
        jsonb eligibility
        string application_url
        vector embedding
        string status
        timestamp created_at
        timestamp updated_at
    }

    OPPORTUNITY_SKILL {
        uuid opportunity_id FK
        uuid skill_id FK
        string requirement_type
    }

    SOURCE {
        uuid id PK
        string name
        string base_url
        string source_type
    }

    OPPORTUNITY_SOURCE {
        uuid opportunity_id FK
        uuid source_id FK
        string source_url
        timestamp fetched_at
    }

    APPLICATION {
        uuid id PK
        uuid user_id FK
        uuid opportunity_id FK
        string status
        text notes
        timestamp applied_at
        timestamp updated_at
    }

    APPLICATION_EVENT {
        uuid id PK
        uuid application_id FK
        string old_status
        string new_status
        timestamp created_at
    }

    RECOMMENDATION {
        uuid id PK
        uuid user_id FK
        uuid opportunity_id FK
        decimal score
        jsonb score_breakdown
        jsonb reasons
        timestamp generated_at
    }
```

------------------------------------------------------------------------

## 13. API Design

### Auth

``` text
POST /auth/register
POST /auth/login
POST /auth/logout
```

### Profile

``` text
GET  /users/me
PATCH /users/me
PUT  /users/me/skills
PUT  /users/me/interests
```

### Opportunities

``` text
GET  /opportunities
GET  /opportunities/{id}
POST /opportunities
```

Admin-only write operations should be protected.

### Recommendations

``` text
GET /recommendations
GET /recommendations/{id}
```

### Applications

``` text
GET   /applications
POST  /applications
PATCH /applications/{id}
DELETE /applications/{id}
```

### Ingestion

``` text
POST /ingestion/run
GET  /ingestion/jobs/{id}
```

The ingestion endpoint should eventually be restricted to an
admin/worker rather than exposed publicly.

------------------------------------------------------------------------

## 14. Recommendation Architecture

Start with deterministic and interpretable features.

``` text
Skill similarity
Interest similarity
Eligibility
Deadline urgency
Opportunity preference
```

Candidate generation can use vector similarity.

Final ranking should be computed server-side.

Store the score breakdown so recommendations can be debugged.

------------------------------------------------------------------------

## 15. Failure States

Design explicitly for:

-   No recommendations
-   No eligible opportunities
-   Expired opportunity
-   Missing deadline
-   Source unavailable
-   Extraction failed
-   Duplicate detected
-   Recommendation service unavailable
-   Empty application tracker

Never show a blank screen when a useful empty state can be provided.

------------------------------------------------------------------------

## 16. Development Order

``` text
1. Database schema
2. Backend foundation
3. Authentication
4. Profile
5. Opportunity CRUD
6. Frontend shell
7. Search/filter
8. Eligibility engine
9. Embeddings
10. Recommendation ranking
11. Application tracker
12. Ingestion
13. Evaluation
14. Deployment
15. Observability
```

This order intentionally gets a usable deterministic product working
before adding AI complexity.
