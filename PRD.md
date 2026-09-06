# CampusOS --- Product Requirements Document (PRD)

## 1. Product Overview

**Product name:** CampusOS\
**Product type:** Personalized opportunity intelligence platform\
**Primary users:** University students seeking internships,
competitions, hackathons, fellowships, scholarships, and similar
opportunities.

### Problem

Student opportunities are fragmented across company websites,
competition portals, college pages, newsletters, LinkedIn, and other
channels. Students spend significant time searching, checking
eligibility, comparing deadlines, and manually tracking applications.

CampusOS turns this fragmented information into a structured,
personalized opportunity feed.

### Product thesis

The core question CampusOS should answer is:

> **"Given all the opportunities available, what should this student
> apply to right now, and why?"**

The product is not primarily an AI chatbot. AI/NLP is used where it
creates measurable value inside a broader data and recommendation
system.

------------------------------------------------------------------------

## 2. Goals

### V1 goals

1.  Aggregate opportunities from a small number of reliable sources.
2.  Convert unstructured opportunity descriptions into structured
    records.
3.  Determine basic eligibility from student profiles.
4.  Rank eligible opportunities by relevance and urgency.
5.  Explain recommendations.
6.  Let students save and track applications.
7.  Provide a measurable evaluation framework.

### Non-goals for V1

-   Native mobile application.
-   Full browser extension.
-   Automated application submission.
-   Resume generation.
-   General-purpose conversational assistant.
-   Complex social network.
-   Microservice architecture.
-   Custom foundation model training.

------------------------------------------------------------------------

## 3. Target User

### Primary persona --- Ambitious undergraduate

Typical profile:

-   1st--4th year undergraduate.
-   Interested in one or more non-core/career paths.
-   Applies to internships, competitions, hackathons, fellowships, etc.
-   Uses multiple information channels.
-   Has limited time and misses opportunities because of information
    overload.

### Core pain points

-   "I don't know where to look."
-   "I found this too late."
-   "Am I eligible?"
-   "Is this worth applying to?"
-   "I've lost track of what I already applied to."

------------------------------------------------------------------------

## 4. Core User Journey

``` text
Sign up
  ↓
Create profile
  ↓
Add skills/interests/preferences
  ↓
System discovers opportunities
  ↓
Normalize + extract requirements
  ↓
Eligibility filtering
  ↓
Recommendation ranking
  ↓
Student reviews "Why this?"
  ↓
Save / Apply
  ↓
Track application
  ↓
Outcome feeds future recommendations
```

------------------------------------------------------------------------

## 5. Functional Requirements

### FR-01 --- User profile

The user must be able to maintain:

-   Name
-   University
-   Degree
-   Branch/discipline
-   Graduation year
-   Current year
-   CGPA
-   Skills
-   Interests
-   Preferred opportunity types
-   Preferred locations/work modes

The system should allow profile edits without requiring re-registration.

### FR-02 --- Opportunity ingestion

The system must support importing opportunities from:

-   Seeded/manual records
-   Public webpages
-   Structured feeds where legally and technically appropriate

Each imported opportunity should retain its source URL and source
metadata.

### FR-03 --- Opportunity normalization

Convert source content into:

-   Title
-   Organization
-   Opportunity type
-   Description
-   Deadline
-   Start date if available
-   Location/work mode
-   Eligibility
-   Minimum CGPA
-   Eligible years
-   Eligible branches
-   Required skills
-   Preferred skills
-   Compensation if publicly stated
-   Application URL
-   Source URL

Unknown fields must remain null/unknown rather than being guessed.

### FR-04 --- Eligibility engine

The eligibility engine must evaluate deterministic requirements before
semantic ranking.

Initial rules:

-   Graduation year
-   Current year
-   Degree/branch
-   Minimum CGPA
-   Geographic constraints where explicitly stated

Each result should have:

-   `eligible`
-   `ineligible`
-   `uncertain`

The system should preserve the reason for the decision.

### FR-05 --- Recommendation engine

V1 ranking should combine:

``` text
Final Score =
0.30 × Skill Match
+ 0.25 × Interest Match
+ 0.20 × Eligibility/Requirement Fit
+ 0.15 × Deadline Urgency
+ 0.10 × Opportunity-Type Preference
```

These weights are initial configuration, not scientific truth. Store
them centrally so they can be tuned.

Recommendation pipeline:

``` text
All opportunities
    ↓
Basic validation
    ↓
Eligibility filter
    ↓
Candidate generation
    ↓
Semantic similarity
    ↓
Ranking
    ↓
Explanation generation
```

### FR-06 --- Explainability

Every recommendation should expose human-readable reasons.

Example:

> 91% match. You match 4 of 5 listed skills, meet the academic
> requirements, and have selected consulting competitions as a preferred
> category. Deadline is in 4 days.

Do not expose unsupported claims.

### FR-07 --- Opportunity search

Users should be able to filter by:

-   Type
-   Deadline
-   Eligibility
-   Location
-   Remote/on-site
-   Organization
-   Skills
-   Match score

### FR-08 --- Application tracker

Statuses:

``` text
DISCOVERED
SAVED
APPLIED
ASSESSMENT
INTERVIEW
OFFER
REJECTED
WITHDRAWN
```

Users can add notes and update status.

### FR-09 --- Dashboard

Minimum dashboard:

-   Recommended opportunities
-   Deadlines soon
-   Saved opportunities
-   Active applications
-   Interview count
-   Offers
-   Recently added opportunities

### FR-10 --- Data quality

The system should identify:

-   Duplicate opportunities
-   Missing deadlines
-   Expired opportunities
-   Stale source records
-   Extraction uncertainty

------------------------------------------------------------------------

## 6. Non-Functional Requirements

### Performance

Target V1:

-   Typical API response: \<500 ms excluding external model calls.
-   Recommendation generation should be cached where appropriate.
-   Pages should remain usable on normal student internet connections.

### Reliability

-   Failed ingestion of one source must not stop the entire pipeline.
-   External model/API failures must degrade gracefully.
-   Every opportunity should have provenance.

### Security

-   Passwords must never be stored in plaintext.
-   Authentication tokens must be handled securely.
-   Users should only access their own private profile/application data.
-   API keys must remain server-side.
-   Secrets must never be committed to Git.

### Privacy

Collect only data needed for the product.

Do not expose student profiles publicly by default.

------------------------------------------------------------------------

## 7. MVP Acceptance Criteria

The MVP is complete when a new user can:

1.  Create a profile.
2.  See opportunities in the database.
3.  Have obviously ineligible opportunities filtered.
4.  Receive ranked recommendations.
5.  Understand why an opportunity was recommended.
6.  Save an opportunity.
7.  Mark it as applied.
8.  Track application status.
9.  Search/filter opportunities.
10. View deadlines from a dashboard.

The system must also:

-   retain source URLs,
-   handle duplicates,
-   record extraction confidence,
-   and expose enough data to evaluate recommendation quality.

------------------------------------------------------------------------

## 8. Product Metrics

### Primary

-   Opportunity-to-application conversion rate
-   Recommendation Precision@K
-   Eligible recommendation rate
-   Application completion rate

### Secondary

-   Save rate
-   Click-through rate
-   Time from discovery to application
-   Deadline-miss rate
-   7-day/30-day retention

### System metrics

-   Extraction accuracy
-   Eligibility classification accuracy
-   Duplicate detection precision
-   API latency
-   Ingestion success rate

Never place fabricated metrics on a resume or portfolio.

------------------------------------------------------------------------

## 9. Roadmap

### Phase 1 --- Foundation

Profile, database, authentication, opportunity CRUD.

### Phase 2 --- Intelligence

Extraction, eligibility, embeddings, ranking, explanations.

### Phase 3 --- Workflow

Application tracker, deadlines, dashboard, notifications.

### Phase 4 --- Learning

Use saves, clicks, applications, and outcomes to improve ranking.

### Phase 5 --- Scale

More sources, better evaluation, caching, observability, deployment
hardening.

------------------------------------------------------------------------

## 10. Product Principles

1.  **Correctness before intelligence.**
2.  **Eligibility before recommendation.**
3.  **Evidence before AI-generated claims.**
4.  **Every opportunity has provenance.**
5.  **Unknown is better than hallucinated.**
6.  **Measure before claiming improvement.**
7.  **Build a modular monolith before microservices.**
8.  **Ship a narrow useful product before adding features.**
