from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class AnalyticsGrouping(str, Enum):
    """Grouping periods for the per-colony analytics chart (#42).

    'Stunde' (hourly) was explicitly dropped — not meaningful for once-daily
    harvest/feeding records.
    """

    year = "year"
    month = "month"
    week = "week"
    day = "day"


class HiveAnalyticsKpi(BaseModel):
    total_harvest_kg: float
    total_feeding_kg_or_l: float
    inspection_count: int
    treatment_count: int
    event_count: int


class HiveAnalyticsChartPoint(BaseModel):
    period_key: str
    period_start: date
    harvest_kg: float
    feeding_kg_or_l: float
    inspection_count: int
    treatment_count: int
    event_count: int


class HiveAnalyticsResponse(BaseModel):
    hive_id: int
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    grouping: AnalyticsGrouping
    kpi: HiveAnalyticsKpi
    chart: list[HiveAnalyticsChartPoint]
