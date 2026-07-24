"""M7 queen rearing: breeding data, zuchtreihen, breeding steps, criterion weights

Revision ID: 20260724_0025
Revises: 20260723_0024
Create Date: 2026-07-24 09:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260724_0025"
down_revision: Union[str, None] = "20260723_0024"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- #31: breeding data fields on Queen, is_breeding_candidate on Hive ---
    op.add_column("hives", sa.Column("is_breeding_candidate", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.add_column("queens", sa.Column("rasse", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("linie", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("lebensnummer", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("paartyp", sa.String(), nullable=True))

    op.add_column("queens", sa.Column("zuchtbuchnummer_land", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("zuchtbuchnummer_lv", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("zuchtbuchnummer_zuechter", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("zuchtbuchnummer_nr", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("zuchtbuchnummer_jahr", sa.Integer(), nullable=True))

    op.add_column("queens", sa.Column("zuchtbuchnummer_mutter_land", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("zuchtbuchnummer_mutter_lv", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("zuchtbuchnummer_mutter_zuechter", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("zuchtbuchnummer_mutter_nr", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("zuchtbuchnummer_mutter_jahr", sa.Integer(), nullable=True))

    op.add_column("queens", sa.Column("zuchtbuchnummer_drohnen_land", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("zuchtbuchnummer_drohnen_lv", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("zuchtbuchnummer_drohnen_zuechter", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("zuchtbuchnummer_drohnen_nr", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("zuchtbuchnummer_drohnen_jahr", sa.Integer(), nullable=True))

    op.add_column("queens", sa.Column("pedigree_pedigree", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("pedigree_kasten_nr", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("pedigree_zuechter", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("pedigree_jahr", sa.Integer(), nullable=True))

    op.add_column("queens", sa.Column("belegstelle_land", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("belegstelle_verband", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("belegstelle_nummer", sa.String(), nullable=True))
    op.add_column("queens", sa.Column("belegstelle_durchgang", sa.String(), nullable=True))

    # --- #32 / #34: Zuchtreihen with manual counters ---
    op.create_table(
        "zuchtreihen",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("apiary_id", sa.Integer(), nullable=False),
        sa.Column("herkunftsvolk_id", sa.Integer(), nullable=True),
        sa.Column("anzahl_larven", sa.Integer(), nullable=True),
        sa.Column("anzahl_angenommen", sa.Integer(), nullable=True),
        sa.Column("anzahl_geschluepft", sa.Integer(), nullable=True),
        sa.Column("anzahl_begattet", sa.Integer(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["apiary_id"], ["apiaries.id"]),
        sa.ForeignKeyConstraint(["herkunftsvolk_id"], ["hives.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_zuchtreihen_id", "zuchtreihen", ["id"])
    op.create_index("ix_zuchtreihen_owner_id", "zuchtreihen", ["owner_id"])

    # --- #33: BreedingStep ---
    op.create_table(
        "breeding_steps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("zuchtreihe_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("task_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["zuchtreihe_id"], ["zuchtreihen.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_breeding_steps_id", "breeding_steps", ["id"])
    op.create_index("ix_breeding_steps_zuchtreihe_id", "breeding_steps", ["zuchtreihe_id"])

    # --- #35: new TaskSource value ---
    if op.get_context().dialect.name == "postgresql":
        op.execute("ALTER TYPE tasksource ADD VALUE IF NOT EXISTS 'breeding'")

    # --- #36: per-option score value on InspectionCriterion, CriterionWeight ---
    op.add_column("inspection_criteria", sa.Column("option_scores", sa.JSON(), nullable=True))

    op.create_table(
        "criterion_weights",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("criterion_id", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["criterion_id"], ["inspection_criteria.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_criterion_weights_id", "criterion_weights", ["id"])
    op.create_index("ix_criterion_weights_user_id", "criterion_weights", ["user_id"])
    op.create_index("ix_criterion_weights_criterion_id", "criterion_weights", ["criterion_id"])


def downgrade() -> None:
    op.drop_index("ix_criterion_weights_criterion_id", table_name="criterion_weights")
    op.drop_index("ix_criterion_weights_user_id", table_name="criterion_weights")
    op.drop_index("ix_criterion_weights_id", table_name="criterion_weights")
    op.drop_table("criterion_weights")
    op.drop_column("inspection_criteria", "option_scores")

    op.drop_index("ix_breeding_steps_zuchtreihe_id", table_name="breeding_steps")
    op.drop_index("ix_breeding_steps_id", table_name="breeding_steps")
    op.drop_table("breeding_steps")

    op.drop_index("ix_zuchtreihen_owner_id", table_name="zuchtreihen")
    op.drop_index("ix_zuchtreihen_id", table_name="zuchtreihen")
    op.drop_table("zuchtreihen")

    op.drop_column("queens", "belegstelle_durchgang")
    op.drop_column("queens", "belegstelle_nummer")
    op.drop_column("queens", "belegstelle_verband")
    op.drop_column("queens", "belegstelle_land")

    op.drop_column("queens", "pedigree_jahr")
    op.drop_column("queens", "pedigree_zuechter")
    op.drop_column("queens", "pedigree_kasten_nr")
    op.drop_column("queens", "pedigree_pedigree")

    op.drop_column("queens", "zuchtbuchnummer_drohnen_jahr")
    op.drop_column("queens", "zuchtbuchnummer_drohnen_nr")
    op.drop_column("queens", "zuchtbuchnummer_drohnen_zuechter")
    op.drop_column("queens", "zuchtbuchnummer_drohnen_lv")
    op.drop_column("queens", "zuchtbuchnummer_drohnen_land")

    op.drop_column("queens", "zuchtbuchnummer_mutter_jahr")
    op.drop_column("queens", "zuchtbuchnummer_mutter_nr")
    op.drop_column("queens", "zuchtbuchnummer_mutter_zuechter")
    op.drop_column("queens", "zuchtbuchnummer_mutter_lv")
    op.drop_column("queens", "zuchtbuchnummer_mutter_land")

    op.drop_column("queens", "zuchtbuchnummer_jahr")
    op.drop_column("queens", "zuchtbuchnummer_nr")
    op.drop_column("queens", "zuchtbuchnummer_zuechter")
    op.drop_column("queens", "zuchtbuchnummer_lv")
    op.drop_column("queens", "zuchtbuchnummer_land")

    op.drop_column("queens", "paartyp")
    op.drop_column("queens", "lebensnummer")
    op.drop_column("queens", "linie")
    op.drop_column("queens", "rasse")

    op.drop_column("hives", "is_breeding_candidate")
