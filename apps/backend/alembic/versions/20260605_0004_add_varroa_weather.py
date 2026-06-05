"""add varroa weather windows

Revision ID: 20260605_0004
Revises: 20260605_0003
Create Date: 2026-06-05 12:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260605_0004"
down_revision: Union[str, None] = "20260605_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

treatment_type = sa.Enum(
    "formic_acid_short",
    "formic_acid_long",
    "thymol",
    "oxalic_acid_dribble",
    "oxalic_acid_sublimation",
    "lactic_acid",
    "biotechnical",
    "other",
    name="varroatreatmenttype",
)
weather_rating = sa.Enum("suitable", "caution", "unsuitable", "unknown", name="varroaweatherrating")


def upgrade() -> None:
    if op.get_context().dialect.name != "sqlite":
        treatment_type.create(op.get_bind(), checkfirst=True)
        weather_rating.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "varroa_weather_windows",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("apiary_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("provider_version", sa.String(), nullable=False),
        sa.Column("treatment_type", treatment_type, nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("rating", weather_rating, nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("min_temperature", sa.Float(), nullable=True),
        sa.Column("max_temperature", sa.Float(), nullable=True),
        sa.Column("avg_humidity", sa.Float(), nullable=True),
        sa.Column("precipitation_probability", sa.Float(), nullable=True),
        sa.Column("wind_speed", sa.Float(), nullable=True),
        sa.Column("raw_payload_json", sa.JSON(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["apiary_id"], ["apiaries.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_varroa_weather_windows_id"), "varroa_weather_windows", ["id"], unique=False)
    op.create_index(
        "ix_varroa_weather_lookup",
        "varroa_weather_windows",
        ["owner_id", "apiary_id", "treatment_type", "date"],
        unique=False,
    )

    op.add_column("treatments", sa.Column("weather_window_id", sa.Integer(), nullable=True))
    op.add_column("treatments", sa.Column("weather_rating", sa.String(), nullable=True))
    op.add_column("treatments", sa.Column("weather_source", sa.String(), nullable=True))
    op.add_column("treatments", sa.Column("weather_fetched_at", sa.DateTime(timezone=True), nullable=True))
    if op.get_context().dialect.name != "sqlite":
        op.create_foreign_key(
            "fk_treatments_weather_window_id",
            "treatments",
            "varroa_weather_windows",
            ["weather_window_id"],
            ["id"],
        )


def downgrade() -> None:
    if op.get_context().dialect.name != "sqlite":
        op.drop_constraint("fk_treatments_weather_window_id", "treatments", type_="foreignkey")
    op.drop_column("treatments", "weather_fetched_at")
    op.drop_column("treatments", "weather_source")
    op.drop_column("treatments", "weather_rating")
    op.drop_column("treatments", "weather_window_id")
    op.drop_index("ix_varroa_weather_lookup", table_name="varroa_weather_windows")
    op.drop_index(op.f("ix_varroa_weather_windows_id"), table_name="varroa_weather_windows")
    op.drop_table("varroa_weather_windows")
    if op.get_context().dialect.name != "sqlite":
        weather_rating.drop(op.get_bind(), checkfirst=True)
        treatment_type.drop(op.get_bind(), checkfirst=True)
