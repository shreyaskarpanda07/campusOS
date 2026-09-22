"""create opportunity and source tables

Revision ID: 003_create_opportunity_tables
Revises: 002_create_profile_tables
Create Date: 2026-09-22 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003_create_opportunity_tables"
down_revision: Union[str, None] = "002_create_profile_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    json_type = (
        postgresql.JSONB(astext_type=sa.Text())
        .with_variant(sa.JSON(), "sqlite")
    )

    # 1. Create opportunities table
    op.create_table(
        "opportunities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("organization", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("work_mode", sa.String(length=20), nullable=True),
        sa.Column("minimum_cgpa", sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column("eligibility", json_type, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("compensation", sa.String(length=255), nullable=True),
        sa.Column("application_url", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("extraction_confidence", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_opportunities_organization"), "opportunities", ["organization"], unique=False)
    op.create_index(op.f("ix_opportunities_type"), "opportunities", ["type"], unique=False)
    op.create_index(op.f("ix_opportunities_deadline"), "opportunities", ["deadline"], unique=False)
    op.create_index(op.f("ix_opportunities_status"), "opportunities", ["status"], unique=False)

    # 2. Create sources table
    op.create_table(
        "sources",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("base_url", sa.Text(), nullable=True),
        sa.Column("source_type", sa.String(length=50), nullable=False, server_default=sa.text("'manual'")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 3. Create opportunity_skills table
    op.create_table(
        "opportunity_skills",
        sa.Column("opportunity_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("requirement_type", sa.String(length=20), nullable=False, server_default=sa.text("'required'")),
        sa.ForeignKeyConstraint(
            ["opportunity_id"],
            ["opportunities.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"],
            ["skills.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("opportunity_id", "skill_id"),
    )

    # 4. Create opportunity_sources table
    op.create_table(
        "opportunity_sources",
        sa.Column("opportunity_id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column(
            "fetched_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["opportunity_id"],
            ["opportunities.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("opportunity_id", "source_id"),
    )


def downgrade() -> None:
    op.drop_table("opportunity_sources")
    op.drop_table("opportunity_skills")
    op.drop_table("sources")
    op.drop_index(op.f("ix_opportunities_status"), table_name="opportunities")
    op.drop_index(op.f("ix_opportunities_deadline"), table_name="opportunities")
    op.drop_index(op.f("ix_opportunities_type"), table_name="opportunities")
    op.drop_index(op.f("ix_opportunities_organization"), table_name="opportunities")
    op.drop_table("opportunities")
