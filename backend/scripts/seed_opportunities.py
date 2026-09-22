"""
Seed script to populate CampusOS with realistic university student opportunities.

Covers:
- Software Engineering & Data Internships
- Global & National Hackathons
- Business & Tech Case Competitions
- Fellowships & Open Source Programs
- Academic Scholarships
"""

import sys
from datetime import date, timedelta
from pathlib import Path

# Ensure backend root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityCreateRequest, OpportunitySkillItem
from app.services.opportunity import opportunity_service


SAMPLE_OPPORTUNITIES = [
    {
        "title": "Software Engineering Intern — Summer 2027",
        "organization": "Google",
        "type": "internship",
        "description": "Join Google's Core Systems engineering team to build scalable cloud infrastructure and developer tooling. You will collaborate with senior engineers on production distributed systems handling billions of requests daily.",
        "days_to_deadline": 5,
        "location": "Mountain View, CA",
        "work_mode": "hybrid",
        "minimum_cgpa": 7.5,
        "eligibility": {
            "eligible_years": [2027, 2028],
            "eligible_branches": ["Computer Science", "Information Technology", "Electrical Engineering"],
            "degree_levels": ["B.Tech", "B.S.", "M.S."],
        },
        "compensation": "$58/hour + housing stipend",
        "application_url": "https://careers.google.com/jobs/results/swe-intern-summer-2027",
        "source_name": "Google Careers",
        "source_url": "https://careers.google.com",
        "skills": [
            OpportunitySkillItem(name="Python", requirement_type="required"),
            OpportunitySkillItem(name="C++", requirement_type="preferred"),
            OpportunitySkillItem(name="Distributed Systems", requirement_type="preferred"),
            OpportunitySkillItem(name="Data Structures", requirement_type="required"),
        ],
    },
    {
        "title": "Deloitte Strategy & Analytics Case Challenge",
        "organization": "Deloitte Consulting",
        "type": "competition",
        "description": "National case competition tackling digital transformation and operational AI adoption in healthcare systems. Teams solve a 48-hour live business challenge presented to Deloitte consulting partners.",
        "days_to_deadline": 3,
        "location": "Remote",
        "work_mode": "remote",
        "minimum_cgpa": 7.0,
        "eligibility": {
            "eligible_years": [2025, 2026, 2027, 2028],
            "eligible_branches": ["All Branches"],
            "degree_levels": ["All Degrees"],
        },
        "compensation": "$10,000 prize pool + interview fast-track",
        "application_url": "https://deloitte.com/challenge/strategy-2026",
        "source_name": "Unstop",
        "source_url": "https://unstop.com/competitions/deloitte-strategy-challenge",
        "skills": [
            OpportunitySkillItem(name="Business Analysis", requirement_type="required"),
            OpportunitySkillItem(name="Problem Solving", requirement_type="required"),
            OpportunitySkillItem(name="Financial Modeling", requirement_type="preferred"),
            OpportunitySkillItem(name="Data Analytics", requirement_type="preferred"),
        ],
    },
    {
        "title": "HackMIT 2026 — AI & Society Track",
        "organization": "MIT Tech Club",
        "type": "hackathon",
        "description": "36-hour premier collegiate hackathon gathering 1,000+ top student hackers globally. Build innovative solutions across GenAI, Web3, HealthTech, and Sustainability with sponsor API mentorship.",
        "days_to_deadline": 12,
        "location": "Cambridge, MA",
        "work_mode": "hybrid",
        "minimum_cgpa": None,
        "eligibility": {
            "eligible_years": [2025, 2026, 2027, 2028, 2029],
            "eligible_branches": ["All Branches"],
            "degree_levels": ["Undergraduate", "Graduate"],
        },
        "compensation": "$50,000 in prizes + travel grants",
        "application_url": "https://hackmit.org/apply",
        "source_name": "Devpost",
        "source_url": "https://devpost.com/hackathons/hackmit-2026",
        "skills": [
            OpportunitySkillItem(name="Full Stack Development", requirement_type="required"),
            OpportunitySkillItem(name="React", requirement_type="preferred"),
            OpportunitySkillItem(name="Machine Learning", requirement_type="preferred"),
            OpportunitySkillItem(name="FastAPI", requirement_type="preferred"),
        ],
    },
    {
        "title": "Machine Learning Research Intern",
        "organization": "Microsoft Research",
        "type": "internship",
        "description": "Contribute to cutting-edge research in multimodal foundation models and reasoning architectures. Publish research papers and benchmark novel model representations.",
        "days_to_deadline": 18,
        "location": "Redmond, WA",
        "work_mode": "onsite",
        "minimum_cgpa": 8.5,
        "eligibility": {
            "eligible_years": [2026, 2027],
            "eligible_branches": ["Computer Science", "Mathematics", "Data Science"],
            "degree_levels": ["B.S.", "M.S.", "Ph.D."],
        },
        "compensation": "$65/hour + relocation assistance",
        "application_url": "https://careers.microsoft.com/research/internships/ml-2027",
        "source_name": "Microsoft Careers",
        "source_url": "https://careers.microsoft.com",
        "skills": [
            OpportunitySkillItem(name="PyTorch", requirement_type="required"),
            OpportunitySkillItem(name="Python", requirement_type="required"),
            OpportunitySkillItem(name="Deep Learning", requirement_type="required"),
            OpportunitySkillItem(name="NLP", requirement_type="preferred"),
        ],
    },
    {
        "title": "Google Summer of Code (GSoC) 2026 Contributor",
        "organization": "Python Software Foundation",
        "type": "fellowship",
        "description": "Open source mentorship program where students write code for global open source organizations under expert maintainers. Work on Python core tooling, CPython, or scientific libraries.",
        "days_to_deadline": 25,
        "location": "Remote",
        "work_mode": "remote",
        "minimum_cgpa": None,
        "eligibility": {
            "eligible_years": [2025, 2026, 2027, 2028],
            "eligible_branches": ["All Branches"],
            "degree_levels": ["All Degrees"],
        },
        "compensation": "$3,000 – $6,600 stipend",
        "application_url": "https://summerofcode.withgoogle.com",
        "source_name": "Google Summer of Code",
        "source_url": "https://summerofcode.withgoogle.com",
        "skills": [
            OpportunitySkillItem(name="Python", requirement_type="required"),
            OpportunitySkillItem(name="Git", requirement_type="required"),
            OpportunitySkillItem(name="Open Source", requirement_type="required"),
        ],
    },
    {
        "title": "Generation Google Scholarship (APAC)",
        "organization": "Google Student Veterans & Diversity",
        "type": "scholarship",
        "description": "Scholarship awarded to aspiring computer science students with strong academic merit, passion for technology, and demonstrated leadership in underrepresented communities.",
        "days_to_deadline": 8,
        "location": "Remote",
        "work_mode": "remote",
        "minimum_cgpa": 8.0,
        "eligibility": {
            "eligible_years": [2026, 2027, 2028],
            "eligible_branches": ["Computer Science", "Computer Engineering"],
            "degree_levels": ["B.Tech", "B.S."],
        },
        "compensation": "$2,500 academic award",
        "application_url": "https://buildyourfuture.withgoogle.com/scholarships/generation-google-scholarship-apac",
        "source_name": "Google Student Opportunities",
        "source_url": "https://buildyourfuture.withgoogle.com",
        "skills": [
            OpportunitySkillItem(name="Computer Science Fundamentals", requirement_type="required"),
            OpportunitySkillItem(name="Community Leadership", requirement_type="required"),
        ],
    },
    {
        "title": "Backend Engineering Intern — Infrastructure",
        "organization": "Stripe",
        "type": "internship",
        "description": "Build high-reliability financial systems handling hundreds of billions of dollars per year. Focus on latency, database concurrency, and idempotent transaction pipelines.",
        "days_to_deadline": 14,
        "location": "San Francisco, CA",
        "work_mode": "hybrid",
        "minimum_cgpa": 7.5,
        "eligibility": {
            "eligible_years": [2026, 2027],
            "eligible_branches": ["Computer Science", "Software Engineering"],
            "degree_levels": ["Undergraduate"],
        },
        "compensation": "$60/hour + housing benefits",
        "application_url": "https://stripe.com/jobs/infra-intern-2027",
        "source_name": "Stripe Careers",
        "source_url": "https://stripe.com/jobs",
        "skills": [
            OpportunitySkillItem(name="Go", requirement_type="preferred"),
            OpportunitySkillItem(name="Ruby", requirement_type="preferred"),
            OpportunitySkillItem(name="SQL", requirement_type="required"),
            OpportunitySkillItem(name="Distributed Systems", requirement_type="required"),
        ],
    },
]


def seed():
    """Populate database with sample opportunities idempotently."""
    db = SessionLocal()
    today = date.today()
    created_count = 0

    try:
        for item in SAMPLE_OPPORTUNITIES:
            # Check if opportunity already exists by title and organization
            stmt = select(Opportunity).where(
                Opportunity.title == item["title"],
                Opportunity.organization == item["organization"],
            )
            existing = db.scalars(stmt).first()
            if existing:
                continue

            deadline = today + timedelta(days=item["days_to_deadline"])
            start_date = today + timedelta(days=item["days_to_deadline"] + 60)

            req = OpportunityCreateRequest(
                title=item["title"],
                organization=item["organization"],
                type=item["type"],
                description=item["description"],
                deadline=deadline,
                start_date=start_date,
                location=item["location"],
                work_mode=item["work_mode"],
                minimum_cgpa=item["minimum_cgpa"],
                eligibility=item["eligibility"],
                compensation=item["compensation"],
                application_url=item["application_url"],
                source_name=item["source_name"],
                source_url=item["source_url"],
                skills=item["skills"],
                status="active",
                extraction_confidence=0.95,
            )
            opportunity_service.create_opportunity(db, req)
            created_count += 1

        print(f"Successfully seeded {created_count} opportunities into CampusOS database.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
