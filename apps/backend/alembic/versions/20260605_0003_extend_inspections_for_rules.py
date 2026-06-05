"""extend inspections for rules

Revision ID: 20260605_0003
Revises: 20260605_0002
Create Date: 2026-06-05 02:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260605_0003"
down_revision: Union[str, None] = "20260605_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

swarm_cells = sa.Enum("none", "play_cups", "queen_cells", name="swarmcells")
hive_mood = sa.Enum("calm", "normal", "aggressive", name="hivemood")
hive_strength = sa.Enum("weak", "medium", "strong", name="hivestrength")


def upgrade() -> None:
    op.add_column("inspections", sa.Column("swarm_cells", swarm_cells, nullable=False, server_default="none"))
    op.add_column("inspections", sa.Column("mood", hive_mood, nullable=False, server_default="normal"))
    op.add_column("inspections", sa.Column("strength", hive_strength, nullable=False, server_default="medium"))
    op.add_column("inspections", sa.Column("weather", sa.String(), nullable=True))
    op.add_column("inspections", sa.Column("next_steps", sa.String(), nullable=True))
    if op.get_context().dialect.name != "sqlite":
        op.alter_column("inspections", "swarm_cells", server_default=None)
        op.alter_column("inspections", "mood", server_default=None)
        op.alter_column("inspections", "strength", server_default=None)


def downgrade() -> None:
    op.drop_column("inspections", "next_steps")
    op.drop_column("inspections", "weather")
    op.drop_column("inspections", "strength")
    op.drop_column("inspections", "mood")
    op.drop_column("inspections", "swarm_cells")
    hive_strength.drop(op.get_bind(), checkfirst=True)
    hive_mood.drop(op.get_bind(), checkfirst=True)
    swarm_cells.drop(op.get_bind(), checkfirst=True)
