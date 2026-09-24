"""
Unit and integration tests for Phase 6: Vector Embeddings & Similarity Search.

Tests:
1. Opportunity text representation builder
2. User profile text representation builder
3. 1536-dimensional embedding generation and unit L2 normalization
4. Deterministic reproducibility
5. Semantic separation (related vs unrelated text similarity)
6. Cosine similarity edge cases
7. Opportunity and User model embedding database persistence
8. Vector similarity search ranking & filtering
9. Backfill embeddings logic
"""

import math
import pytest
from sqlalchemy.orm import Session

from app.models import (
    Interest,
    Opportunity,
    OpportunitySkill,
    Skill,
    User,
    UserInterest,
    UserSkill,
)
from app.services.embedding import (
    EmbeddingService,
    embedding_service,
    build_opportunity_text,
    build_profile_text,
)


def test_build_opportunity_text():
    """Verify opportunity text serializer includes all key semantic fields."""
    opp = Opportunity(
        title="AI Research Scientist Intern",
        organization="OpenAI",
        type="internship",
        work_mode="hybrid",
        location="San Francisco, CA",
        description="Researching next-generation transformer architectures and reasoning models.",
        eligibility={
            "eligible_branches": ["Computer Science", "Data Science"],
            "eligible_years": [2026, 2027],
        },
    )
    s1 = Skill(name="PyTorch")
    s2 = Skill(name="Deep Learning")
    opp.skills = [
        OpportunitySkill(skill=s1, requirement_type="required"),
        OpportunitySkill(skill=s2, requirement_type="preferred"),
    ]

    text = build_opportunity_text(opp)

    assert "Title: AI Research Scientist Intern" in text
    assert "Organization: OpenAI" in text
    assert "Type: internship" in text
    assert "Work Mode: hybrid" in text
    assert "Location: San Francisco, CA" in text
    assert "Description: Researching next-generation" in text
    assert "Required Skills: PyTorch" in text
    assert "Preferred Skills: Deep Learning" in text
    assert "Eligible Branches: Computer Science, Data Science" in text
    assert "Eligible Batches: 2026, 2027" in text


def test_build_profile_text():
    """Verify student profile text serializer includes credentials and preferences."""
    user = User(
        email="student@university.edu",
        name="Alex Smith",
        university="MIT",
        degree="B.S.",
        branch="Computer Science",
        current_year=3,
        graduation_year=2027,
        preferred_opportunity_types=["internship", "hackathon"],
        preferred_work_modes=["remote", "hybrid"],
        preferred_locations=["San Francisco, CA", "New York, NY"],
    )
    s1 = Skill(name="Python")
    s2 = Skill(name="FastAPI")
    user.skills = [
        UserSkill(skill=s1, proficiency="advanced"),
        UserSkill(skill=s2, proficiency="intermediate"),
    ]
    i1 = Interest(name="Distributed Systems")
    user.interests = [UserInterest(interest=i1)]

    text = build_profile_text(user)

    assert "Degree: B.S. in Computer Science" in text
    assert "University: MIT" in text
    assert "Year of Study: Year 3" in text
    assert "Graduation Year: 2027" in text
    assert "Skills: Python (advanced), FastAPI (intermediate)" in text
    assert "Interests: Distributed Systems" in text
    assert "Preferred Opportunity Types: internship, hackathon" in text
    assert "Preferred Work Modes: remote, hybrid" in text
    assert "Preferred Locations: San Francisco, CA, New York, NY" in text


def test_embedding_generation_shape_and_norm():
    """Verify generated vector has dimension 1536 and unit L2 norm."""
    text = "Full Stack Engineer building web apps with TypeScript, React, and Python."
    vec = embedding_service.generate_embedding(text)

    assert isinstance(vec, list)
    assert len(vec) == 1536
    assert all(isinstance(x, float) for x in vec)

    # Unit norm: ||v||_2 = 1.0 (within precision tolerance)
    norm = math.sqrt(sum(x * x for x in vec))
    assert abs(norm - 1.0) < 1e-4


def test_embedding_empty_text():
    """Verify empty text returns zero vector of dimension 1536."""
    vec = embedding_service.generate_embedding("")
    assert len(vec) == 1536
    assert all(x == 0.0 for x in vec)


def test_embedding_deterministic_reproducibility():
    """Verify deterministic embedding produces identical vector for identical text."""
    text = "Distributed consensus algorithms, Paxos, Raft, and fault tolerance."
    vec1 = embedding_service.generate_embedding(text)
    vec2 = embedding_service.generate_embedding(text)

    assert vec1 == vec2


def test_embedding_semantic_separation():
    """Verify related texts have higher cosine similarity than unrelated texts."""
    ai_role = "Machine Learning Engineer training deep neural networks and PyTorch LLM models"
    ai_candidate = "Graduate student specializing in PyTorch deep learning and machine learning algorithms"
    culinary_role = "French pastry baker crafting artisanal sourdough breads and chocolate croissants"

    vec_role = embedding_service.generate_embedding(ai_role)
    vec_candidate = embedding_service.generate_embedding(ai_candidate)
    vec_culinary = embedding_service.generate_embedding(culinary_role)

    sim_related = embedding_service.compute_cosine_similarity(vec_role, vec_candidate)
    sim_unrelated = embedding_service.compute_cosine_similarity(vec_role, vec_culinary)
    sim_self = embedding_service.compute_cosine_similarity(vec_role, vec_role)

    assert abs(sim_self - 1.0) < 1e-4
    assert sim_related > 0.25
    assert sim_unrelated < 0.15
    assert sim_related > sim_unrelated


def test_cosine_similarity_edge_cases():
    """Verify cosine similarity handles edge cases gracefully."""
    # Empty vectors
    assert embedding_service.compute_cosine_similarity([], []) == 0.0
    # Mismatched dimensions
    assert embedding_service.compute_cosine_similarity([1.0], [1.0, 2.0]) == 0.0
    # Zero vectors
    assert embedding_service.compute_cosine_similarity([0.0, 0.0], [0.0, 0.0]) == 0.0
    # Exact opposite vectors
    v1 = [1.0, 0.0]
    v2 = [-1.0, 0.0]
    assert abs(embedding_service.compute_cosine_similarity(v1, v2) - (-1.0)) < 1e-4


def test_opportunity_embedding_database_persistence(db: Session):
    """Verify opportunity embedding column stores and retrieves 1536-dim vectors."""
    sample_vec = embedding_service.generate_embedding("Cloud Security Internship")

    opp = Opportunity(
        title="Cloud Security Internship",
        organization="Cloudflare",
        type="internship",
        status="active",
        embedding=sample_vec,
    )
    db.add(opp)
    db.commit()
    db.refresh(opp)

    assert opp.embedding is not None
    assert len(opp.embedding) == 1536
    assert abs(opp.embedding[0] - sample_vec[0]) < 1e-5


def test_user_embedding_database_persistence(db: Session):
    """Verify user embedding column stores and retrieves 1536-dim vectors."""
    sample_vec = embedding_service.generate_embedding("Undergraduate CS student")

    user = User(
        email="vector_student@test.edu",
        password_hash="hash",
        name="Vector Student",
        embedding=sample_vec,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.embedding is not None
    assert len(user.embedding) == 1536


def test_find_similar_opportunities_ranking(db: Session):
    """Verify vector search ranks semantically matching opportunities at the top."""
    # 1. Opportunity A: Machine Learning
    opp_ml = Opportunity(
        title="Deep Learning Research Fellow",
        organization="Mila",
        type="fellowship",
        description="Researching deep learning computer vision and neural networks with PyTorch.",
        status="active",
    )
    opp_ml.embedding = embedding_service.embed_opportunity(opp_ml)
    db.add(opp_ml)

    # 2. Opportunity B: Web Development
    opp_web = Opportunity(
        title="Frontend Web Developer Intern",
        organization="Vercel",
        type="internship",
        description="Building user interfaces with Next.js, React, Tailwind CSS, and TypeScript.",
        status="active",
    )
    opp_web.embedding = embedding_service.embed_opportunity(opp_web)
    db.add(opp_web)

    # 3. Opportunity C: Investment Banking
    opp_finance = Opportunity(
        title="Summer Financial Analyst",
        organization="Goldman Sachs",
        type="internship",
        description="Financial modeling, valuation analysis, and DCF spreadsheets for M&A.",
        status="active",
    )
    opp_finance.embedding = embedding_service.embed_opportunity(opp_finance)
    db.add(opp_finance)

    db.commit()

    # Query for ML student
    query_text = "Graduate student looking for computer vision deep learning and PyTorch neural network research."
    query_vec = embedding_service.generate_embedding(query_text)

    results = embedding_service.find_similar_opportunities(
        db, query_vec, limit=3, min_similarity=0.0
    )

    assert len(results) >= 3
    top_opp, top_sim = results[0]

    # The ML fellowship must rank first
    assert top_opp.id == opp_ml.id
    assert top_opp.title == "Deep Learning Research Fellow"
    assert top_sim > results[1][1]
    assert top_sim > results[2][1]

    # Test filtering with threshold
    filtered_results = embedding_service.find_similar_opportunities(
        db, query_vec, limit=3, min_similarity=top_sim - 0.01
    )
    assert len(filtered_results) >= 1
    assert filtered_results[0][0].id == opp_ml.id


def test_backfill_embeddings_logic(db: Session):
    """Verify un-embedded opportunities and users receive embeddings upon backfill."""
    # Create opportunity and user without embeddings
    opp = Opportunity(
        title="Rust Systems Engineer",
        organization="Mozilla",
        type="internship",
        status="active",
        embedding=None,
    )
    user = User(
        email="rustacean@test.edu",
        password_hash="hash",
        name="Rust Dev",
        embedding=None,
    )
    db.add(opp)
    db.add(user)
    db.commit()

    assert opp.embedding is None
    assert user.embedding is None

    # Simulate backfill execution
    opp.embedding = embedding_service.embed_opportunity(opp)
    user.embedding = embedding_service.embed_user_profile(user)
    db.commit()
    db.refresh(opp)
    db.refresh(user)

    assert opp.embedding is not None
    assert len(opp.embedding) == 1536
    assert user.embedding is not None
    assert len(user.embedding) == 1536
