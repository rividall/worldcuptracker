"""scorers table (tournament top scorers / assisters)

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scorers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("player_id", sa.Integer(), nullable=False, index=True),
        sa.Column("player_name", sa.String(length=120), nullable=False),
        sa.Column("nationality", sa.String(length=60), nullable=True),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False, index=True),
        sa.Column("goals", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("assists", sa.Integer(), nullable=True),
        sa.Column("penalties", sa.Integer(), nullable=True),
        sa.Column("played_matches", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("scorers")
