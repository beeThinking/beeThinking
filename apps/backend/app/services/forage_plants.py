"""Trachtpflanzen (forage plants) reference data (#41).

Design choice: static curated JSON seed file maintained in-repo, not a DB
table and not a third-party API (no vendor available). This is read-only
reference data that rarely changes, so a versioned JSON file keeps it simple
to review/update via normal code review instead of a data migration.
"""

import json
from functools import lru_cache
from pathlib import Path

from app.schemas.map import ForagePlantEntry

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "forage_plants.json"


@lru_cache()
def list_forage_plants() -> list[ForagePlantEntry]:
    with _DATA_PATH.open(encoding="utf-8") as handle:
        raw_entries = json.load(handle)
    return [ForagePlantEntry(**entry) for entry in raw_entries]
