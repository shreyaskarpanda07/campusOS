"""add vector embeddings to opportunities and users

Revision ID: 004_add_vector_embeddings
Revises: 003_create_opportunity_tables
Create Date: 2026-09-24 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "004_add_vector_embeddings"
down_revision: Union[str, None] = "003_create_opportunity_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    # 1. Enable pgvector extension on PostgreSQL
    if is_postgres:
        op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))

    vector_type = Vector(1536).with_variant(sa.JSON(), "sqlite")

    # 2. Add embedding column to opportunities
    op.add_column(
        "opportunities",
        sa.Column("embedding", vector_type, nullable=True),
    )

    # 3. Add embedding column to users
    op.add_column(
        "users",
        sa.Column("embedding", vector_type, nullable=True),
    )

    # 4. Create HNSW index on opportunities embedding for fast cosine similarity retrieval
    if is_postgres:
        op.execute(
            sa.text(
                "CREATE INDEX IF NOT EXISTS idx_opportunities_embedding "
                "ON opportunities USING hnsw (embedding vector_cosine_ops)"
            )
        )


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        op.execute(sa.text("DROP INDEX IF EXISTS idx_opportunities_embedding"))

    op.drop_column("users", "embedding")
    op.drop_column("opportunities", "embedding")
