from datetime import date, timedelta

import pytest

from app.models.hive import Hive, HiveStatus
from app.models.inspection import HiveStrength, Inspection, SwarmCells
from app.services.beekeeping_rules import (
    calculate_hive_status,
    calculate_swarm_risk,
    get_inspection_warnings,
    suggest_tasks_after_inspection,
)


@pytest.mark.unit
class TestBeekeepingRules:
    def test_hive_without_inspection_needs_inspection(self):
        hive = Hive(id=1, name="Alpha", status=HiveStatus.active, owner_id=1, apiary_id=1)

        assert calculate_hive_status(hive, None) == "needs_inspection"

    def test_low_food_creates_warning_and_task(self):
        hive = Hive(id=1, name="Alpha", status=HiveStatus.active, owner_id=1, apiary_id=1)
        inspection = Inspection(
            hive_id=1,
            date=date.today(),
            queen_seen=True,
            food_stores=2,
            swarm_cells=SwarmCells.none,
            strength=HiveStrength.medium,
        )

        assert calculate_hive_status(hive, inspection) == "needs_attention"
        assert "Food stores are low" in get_inspection_warnings(inspection)
        assert suggest_tasks_after_inspection(hive, inspection)[0].title == "Check food stores"

    def test_queen_cells_raise_swarm_risk(self):
        hive = Hive(id=1, name="Alpha", status=HiveStatus.active, owner_id=1, apiary_id=1)
        inspection = Inspection(
            hive_id=1,
            date=date.today(),
            queen_seen=True,
            swarm_cells=SwarmCells.queen_cells,
            strength=HiveStrength.strong,
        )

        assert calculate_swarm_risk(hive, inspection, date.today()) == "high"
        assert "Swarm risk is high" in get_inspection_warnings(inspection)

    def test_old_inspection_has_unknown_swarm_risk(self):
        hive = Hive(id=1, name="Alpha", status=HiveStatus.active, owner_id=1, apiary_id=1)
        inspection = Inspection(
            hive_id=1,
            date=date.today() - timedelta(days=20),
            queen_seen=True,
            swarm_cells=SwarmCells.none,
            strength=HiveStrength.medium,
        )

        assert calculate_swarm_risk(hive, inspection, date.today()) == "unknown"
