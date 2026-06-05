"""add inspection weather snapshot

Revision ID: 20260605_0006
Revises: 20260605_0005
Create Date: 2026-06-05 16:15:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260605_0006"
down_revision: Union[str, None] = "20260605_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("inspections", sa.Column("weather_temperature", sa.Float(), nullable=True))
    op.add_column("inspections", sa.Column("weather_humidity", sa.Float(), nullable=True))
    op.add_column("inspections", sa.Column("weather_wind_speed", sa.Float(), nullable=True))
    op.add_column("inspections", sa.Column("weather_precipitation", sa.Float(), nullable=True))
    op.add_column("inspections", sa.Column("weather_code", sa.Integer(), nullable=True))
    op.add_column("inspections", sa.Column("weather_source", sa.String(), nullable=True))
    op.add_column("inspections", sa.Column("weather_fetched_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("inspections", "weather_fetched_at")
    op.drop_column("inspections", "weather_source")
    op.drop_column("inspections", "weather_code")
    op.drop_column("inspections", "weather_precipitation")
    op.drop_column("inspections", "weather_wind_speed")
    op.drop_column("inspections", "weather_humidity")
    op.drop_column("inspections", "weather_temperature")
