"""initial schema

Revision ID: 0001
Revises:
Create Date: 2025-06-21 09:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("external_id", sa.String(length=128), nullable=True),
        sa.Column("author", sa.String(length=256), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=512), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=16), nullable=True),
        sa.Column("received_at", sa.DateTime(), nullable=True),
        sa.Column("imported_at", sa.DateTime(), nullable=True),
        sa.Column("sentiment", sa.String(length=16), nullable=True),
        sa.Column("sentiment_score", sa.Float(), nullable=True),
        sa.Column("topics", sa.JSON(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("draft_response", sa.Text(), nullable=True),
        sa.Column(
            "analysis_status",
            sa.Enum("pending", "processing", "complete", "failed", name="analysisstatus"),
            nullable=True,
        ),
        sa.Column("routed_to", sa.String(length=64), nullable=True),
        sa.Column("routed_at", sa.DateTime(), nullable=True),
        sa.Column("is_escalated", sa.Boolean(), nullable=True),
        sa.Column("response_sent", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reviews_id", "reviews", ["id"], unique=False)
    op.create_index("ix_reviews_external_id", "reviews", ["external_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_reviews_external_id", table_name="reviews")
    op.drop_index("ix_reviews_id", table_name="reviews")
    op.drop_table("reviews")
    op.execute("DROP TYPE IF EXISTS analysisstatus")
