"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-10-07
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

TS = sa.DateTime(timezone=True)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_admin", sa.Boolean, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False),
        sa.Column("budget_usd", sa.Float, nullable=False),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "sessions",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("expires_at", TS, nullable=False),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])

    op.create_table(
        "runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("phase", sa.String(32), nullable=False),
        sa.Column("config", sa.JSON, nullable=False),
        sa.Column("budget_usd", sa.Float, nullable=False),
        sa.Column("cost_usd", sa.Float, nullable=False),
        sa.Column("report_md", sa.Text),
        sa.Column("error", sa.Text),
        sa.Column("created_at", TS, nullable=False),
        sa.Column("updated_at", TS, nullable=False),
    )
    op.create_index("ix_runs_user_id", "runs", ["user_id"])

    op.create_table(
        "run_events",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), primary_key=True, autoincrement=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(64), nullable=False),
        sa.Column("agent", sa.String(128)),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_run_events_run_id", "run_events", ["run_id"])

    op.create_table(
        "sources",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("title", sa.Text),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("snippet", sa.Text),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_sources_run_id", "sources", ["run_id"])

    op.create_table(
        "experiments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("hypothesis_id", sa.String(64), nullable=False),
        sa.Column("iteration", sa.Integer, nullable=False),
        sa.Column("metric_name", sa.String(128)),
        sa.Column("metric_value", sa.Float),
        sa.Column("kept", sa.Boolean, nullable=False),
        sa.Column("code", sa.Text),
        sa.Column("stdout", sa.Text),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_experiments_run_id", "experiments", ["run_id"])


def downgrade() -> None:
    for table in ("experiments", "sources", "run_events", "runs", "sessions", "users"):
        op.drop_table(table)
