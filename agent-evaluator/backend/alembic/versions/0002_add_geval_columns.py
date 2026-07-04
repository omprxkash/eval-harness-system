"""add geval columns to eval_results

Revision ID: add_geval_cols
Revises: 0001
Create Date: 2026-07-05

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "add_geval_cols"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("eval_results", sa.Column("geval_scores", sa.JSON(), nullable=True))
    op.add_column("eval_results", sa.Column("geval_weighted", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("eval_results", "geval_weighted")
    op.drop_column("eval_results", "geval_scores")
