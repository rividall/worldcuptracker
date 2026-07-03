"""initial tables: teams, matches, group_standings, sync_runs

Revision ID: 0001
Revises:
Create Date: 2026-07-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("tla", sa.String(length=3), nullable=True),
        sa.Column("crest_url", sa.String(length=255), nullable=True),
        sa.Column("group_name", sa.String(length=2), nullable=True),
    )
    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("stage", sa.String(length=20), nullable=False, index=True),
        sa.Column("group_name", sa.String(length=2), nullable=True),
        sa.Column("utc_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, index=True),
        sa.Column("home_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=True),
        sa.Column("away_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=True),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("duration", sa.String(length=20), nullable=False, server_default="REGULAR"),
        sa.Column("penalties_home", sa.Integer(), nullable=True),
        sa.Column("penalties_away", sa.Integer(), nullable=True),
        sa.Column("winner_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=True),
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "group_standings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("group_name", sa.String(length=2), nullable=False, index=True),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("played", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("won", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("drawn", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lost", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("goals_for", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("goals_against", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("goal_difference", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("group_name", "team_id"),
    )
    op.create_table(
        "sync_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="running"),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("matches_updated", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("sync_runs")
    op.drop_table("group_standings")
    op.drop_table("matches")
    op.drop_table("teams")
