export type AnalyticsGrouping = 'year' | 'month' | 'week' | 'day';

export interface HiveAnalyticsKpi {
  total_harvest_kg: number;
  total_feeding_kg_or_l: number;
  inspection_count: number;
  treatment_count: number;
  event_count: number;
}

export interface HiveAnalyticsChartPoint {
  period_key: string;
  period_start: string;
  harvest_kg: number;
  feeding_kg_or_l: number;
  inspection_count: number;
  treatment_count: number;
  event_count: number;
}

export interface HiveAnalyticsResponse {
  hive_id: number;
  from_date: string | null;
  to_date: string | null;
  grouping: AnalyticsGrouping;
  kpi: HiveAnalyticsKpi;
  chart: HiveAnalyticsChartPoint[];
}
