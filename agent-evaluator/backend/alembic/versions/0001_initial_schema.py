"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-01 00:00:00.000000

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
        "eval_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.String(length=100), nullable=False),
        sa.Column("goal", sa.Text(), nullable=False),
        sa.Column("trace", sa.JSON(), nullable=False),
        sa.Column("final_output", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("submitted_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_eval_runs_id", "eval_runs", ["id"], unique=False)

    op.create_table(
        "eval_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("task_completion_score", sa.Float(), nullable=False),
        sa.Column("step_accuracy_score", sa.Float(), nullable=False),
        sa.Column("hallucination_detected", sa.Boolean(), nullable=True),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("failure_type", sa.String(length=50), nullable=True),
        sa.Column("correction", sa.JSON(), nullable=True),
        sa.Column("evaluated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["run_id"], ["eval_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_eval_results_id", "eval_results", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_eval_results_id", table_name="eval_results")
    op.drop_table("eval_results")
    op.drop_index("ix_eval_runs_id", table_name="eval_runs")
    op.drop_table("eval_runs")
