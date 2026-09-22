"""create profile tables and user preferences

Revision ID: 002_create_profile_tables
Revises: 001_create_users
Create Date: 2026-09-22 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002_create_profile_tables"
down_revision: Union[str, None] = "001_create_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    json_type = (
        postgresql.JSONB(astext_type=sa.Text())
        .with_variant(sa.JSON(), "sqlite")
    )

    # 1. Add preferred_locations to users
    op.add_column(
        "users",
        sa.Column(
            "preferred_locations",
            json_type,
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )

    # 2. Create skills table
    op.create_table(
        "skills",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_skills_name"), "skills", ["name"], unique=True)

    # 3. Create user_skills junction table
    op.create_table(
        "user_skills",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("proficiency", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(
            ["skill_id"],
            ["skills.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "skill_id"),
    )

    # 4. Create interests table
    op.create_table(
        "interests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_interests_name"), "interests", ["name"], unique=True)

    # 5. Create user_interests junction table
    op.create_table(
        "user_interests",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("interest_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["interest_id"],
            ["interests.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "interest_id"),
    )


def downgrade() -> None:
    op.drop_table("user_interests")
    op.drop_index(op.f("ix_interests_name"), table_name="interests")
    op.drop_table("interests")

    op.drop_table("user_skills")
    op.drop_index(op.f("ix_skills_name"), table_name="skills")
    op.drop_table("skills")

    op.drop_column("users", "preferred_locations")
