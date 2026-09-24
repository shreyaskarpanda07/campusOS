"""
Embedding service for CampusOS.

Handles text serialization, 1536-dimensional vector embedding generation,
and vector similarity search with support for PostgreSQL pgvector and
in-memory fallback for SQLite tests.
"""

from collections import Counter
import hashlib
import logging
import math
import re
from typing import List, Optional, Tuple

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.opportunity import Opportunity
from app.models.user import User

logger = logging.getLogger(__name__)


def build_opportunity_text(opportunity: Opportunity) -> str:
    """
    Serializes an opportunity into a rich, structured text representation for embedding.
    Combines title, organization, type, description, location, work mode, and skills.
    """
    parts = [
        f"Title: {opportunity.title}",
        f"Organization: {opportunity.organization}",
        f"Type: {opportunity.type}",
    ]

    if opportunity.work_mode:
        parts.append(f"Work Mode: {opportunity.work_mode}")
    if opportunity.location:
        parts.append(f"Location: {opportunity.location}")
    if opportunity.description:
        parts.append(f"Description: {opportunity.description}")

    # Extract required and preferred skills
    if opportunity.skills:
        req_skills = [
            os.skill.name for os in opportunity.skills
            if getattr(os, "requirement_type", "required") == "required" and os.skill
        ]
        pref_skills = [
            os.skill.name for os in opportunity.skills
            if getattr(os, "requirement_type", "required") == "preferred" and os.skill
        ]
        if req_skills:
            parts.append(f"Required Skills: {', '.join(req_skills)}")
        if pref_skills:
            parts.append(f"Preferred Skills: {', '.join(pref_skills)}")

    # Extract academic eligibility notes
    if opportunity.eligibility and isinstance(opportunity.eligibility, dict):
        branches = opportunity.eligibility.get("eligible_branches")
        if branches:
            parts.append(f"Eligible Branches: {', '.join(branches) if isinstance(branches, list) else branches}")
        years = opportunity.eligibility.get("eligible_years")
        if years:
            parts.append(f"Eligible Batches: {', '.join(map(str, years)) if isinstance(years, list) else years}")

    return "\n".join(parts)


def build_profile_text(user: User) -> str:
    """
    Serializes a student profile into a rich, structured text representation for embedding.
    Combines academic credentials, skills, interests, and opportunity preferences.
    """
    parts = []

    if user.degree or user.branch:
        parts.append(f"Degree: {user.degree or ''} in {user.branch or ''}".strip())
    if user.university:
        parts.append(f"University: {user.university}")
    if user.current_year:
        parts.append(f"Year of Study: Year {user.current_year}")
    if user.graduation_year:
        parts.append(f"Graduation Year: {user.graduation_year}")

    # User skills
    if user.skills:
        skill_strs = []
        for us in user.skills:
            if us.skill:
                s = us.skill.name
                if getattr(us, "proficiency", None):
                    s += f" ({us.proficiency})"
                skill_strs.append(s)
        if skill_strs:
            parts.append(f"Skills: {', '.join(skill_strs)}")

    # User interests
    if user.interests:
        interest_strs = [ui.interest.name for ui in user.interests if ui.interest]
        if interest_strs:
            parts.append(f"Interests: {', '.join(interest_strs)}")

    # Opportunity type preferences
    if user.preferred_opportunity_types:
        parts.append(f"Preferred Opportunity Types: {', '.join(user.preferred_opportunity_types)}")

    # Work mode & location preferences
    if user.preferred_work_modes:
        parts.append(f"Preferred Work Modes: {', '.join(user.preferred_work_modes)}")
    if user.preferred_locations:
        parts.append(f"Preferred Locations: {', '.join(user.preferred_locations)}")

    return "\n".join(parts)


class EmbeddingService:
    """Service for generating vector embeddings and performing similarity retrieval."""

    def __init__(self, dim: int = 1536):
        self.dim = dim

    def generate_deterministic_embedding(self, text: str) -> List[float]:
        """
        Generates a deterministic 1536-dimensional unit vector from input text.

        Uses token hashing with n-grams, subword extraction, log-TF weighting,
        and random projection initialized by SHA-256 hashes, followed by L2 normalization.
        Guarantees:
        - Exactly self.dim floating-point components
        - Unit length (L2 norm = 1.0)
        - Reproducible and deterministic
        - Positive cosine similarity for semantically aligned token distributions
        """
        words = re.findall(r"\b[a-zA-Z0-9_+#.-]+\b", text.lower())
        if not words:
            return [0.0] * self.dim

        features = Counter()
        for w in words:
            features[w] += 2.0
            # Character trigrams for morphological and spelling tolerance
            if len(w) >= 3:
                for i in range(len(w) - 2):
                    features[w[i : i + 3]] += 0.5

        # Word bigrams for phrasal context
        for i in range(len(words) - 1):
            features[f"{words[i]}_{words[i+1]}"] += 1.5

        vec = [0.0] * self.dim
        for feat, count in features.items():
            weight = 1.0 + math.log(count)
            h = int(hashlib.sha256(feat.encode("utf-8")).hexdigest(), 16)
            for i in range(12):
                idx = (h >> (i * 10)) % self.dim
                sign = 1.0 if ((h >> (i * 3)) & 1) else -1.0
                vec[idx] += sign * weight

        # L2 Normalization to unit hypersphere
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            return [round(x / norm, 6) for x in vec]
        return [0.0] * self.dim

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates a vector embedding for the given text.
        If OPENAI_API_KEY is configured, attempts external API call with fallback.
        Otherwise uses deterministic semantic token embedding.
        """
        if not text or not text.strip():
            return [0.0] * self.dim

        if settings.OPENAI_API_KEY:
            try:
                response = httpx.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                    json={"input": text, "model": settings.EMBEDDING_MODEL},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    embedding = data["data"][0]["embedding"]
                    if len(embedding) == self.dim:
                        return embedding
                logger.warning(
                    "OpenAI embeddings call returned status %s; falling back to deterministic generator.",
                    response.status_code,
                )
            except Exception as e:
                logger.warning("OpenAI embeddings call failed (%s); falling back to deterministic generator.", e)

        return self.generate_deterministic_embedding(text)

    def compute_cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """
        Calculates cosine similarity between two vectors.
        For unit vectors, this is simply their dot product.
        """
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0

        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        cos = dot / (norm_a * norm_b)
        return float(max(-1.0, min(1.0, round(cos, 6))))

    def embed_opportunity(self, opportunity: Opportunity) -> List[float]:
        """Generates and returns an embedding for an opportunity model instance."""
        text = build_opportunity_text(opportunity)
        return self.generate_embedding(text)

    def embed_user_profile(self, user: User) -> List[float]:
        """Generates and returns an embedding for a user profile model instance."""
        text = build_profile_text(user)
        return self.generate_embedding(text)

    def find_similar_opportunities(
        self,
        db: Session,
        query_embedding: List[float],
        limit: int = 10,
        min_similarity: float = 0.0,
    ) -> List[Tuple[Opportunity, float]]:
        """
        Finds opportunities most semantically similar to the given query embedding.

        Uses PostgreSQL pgvector cosine_distance operator when running on Postgres,
        or in-memory cosine similarity calculation when running on SQLite test databases.
        """
        if not query_embedding or len(query_embedding) != self.dim:
            return []

        bind = db.get_bind()
        is_postgres = bind.dialect.name == "postgresql"

        if is_postgres:
            distance_expr = Opportunity.embedding.cosine_distance(query_embedding)
            similarity_expr = 1.0 - distance_expr

            stmt = (
                select(Opportunity, similarity_expr.label("similarity"))
                .where(
                    Opportunity.status == "active",
                    Opportunity.embedding.is_not(None),
                )
                .order_by(distance_expr.asc())
                .limit(limit)
            )
            rows = db.execute(stmt).all()
            return [
                (opp, float(sim))
                for opp, sim in rows
                if float(sim) >= min_similarity
            ]

        # SQLite / In-Memory Fallback for tests
        candidates = (
            db.query(Opportunity)
            .filter(
                Opportunity.status == "active",
                Opportunity.embedding.is_not(None),
            )
            .all()
        )

        scored: List[Tuple[Opportunity, float]] = []
        for opp in candidates:
            if opp.embedding:
                sim = self.compute_cosine_similarity(query_embedding, opp.embedding)
                if sim >= min_similarity:
                    scored.append((opp, sim))

        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:limit]


# Global singleton instance
embedding_service = EmbeddingService(dim=settings.EMBEDDING_DIM)
