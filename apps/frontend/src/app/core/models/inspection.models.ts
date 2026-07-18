export interface Inspection {
  id: number;
  hive_id: number;
  date: string;
  queen_seen: boolean;
  brood_strength: number | null;
  varroa_count: number | null;
  food_stores: number | null;
  swarm_cells: 'none' | 'play_cups' | 'queen_cells';
  mood: 'calm' | 'normal' | 'aggressive';
  strength: 'weak' | 'medium' | 'strong';
  weather: string | null;
  weather_temperature: number | null;
  weather_humidity: number | null;
  weather_wind_speed: number | null;
  weather_precipitation: number | null;
  weather_code: number | null;
  weather_source: string | null;
  weather_fetched_at: string | null;
  hive_weight_kg: number | null;
  criteria_values: Record<string, unknown> | null;
  next_steps: string | null;
  notes: string | null;
  created_at: string;
}

export interface InspectionCreate {
  date: string;
  queen_seen?: boolean;
  brood_strength?: number;
  varroa_count?: number;
  food_stores?: number;
  swarm_cells?: 'none' | 'play_cups' | 'queen_cells';
  mood?: 'calm' | 'normal' | 'aggressive';
  strength?: 'weak' | 'medium' | 'strong';
  weather?: string;
  weather_temperature?: number;
  weather_humidity?: number;
  weather_wind_speed?: number;
  weather_precipitation?: number;
  weather_code?: number;
  weather_source?: string;
  weather_fetched_at?: string;
  hive_weight_kg?: number | null;
  criteria_values?: Record<string, unknown> | null;
  next_steps?: string;
  notes?: string;
}

export interface InspectionUpdate {
  date?: string;
  queen_seen?: boolean;
  brood_strength?: number;
  varroa_count?: number;
  food_stores?: number;
  swarm_cells?: 'none' | 'play_cups' | 'queen_cells';
  mood?: 'calm' | 'normal' | 'aggressive';
  strength?: 'weak' | 'medium' | 'strong';
  weather?: string;
  weather_temperature?: number;
  weather_humidity?: number;
  weather_wind_speed?: number;
  weather_precipitation?: number;
  weather_code?: number;
  weather_source?: string;
  weather_fetched_at?: string;
  next_steps?: string;
  notes?: string;
}

export type CriterionSection = 'allg_befund' | 'verhalten' | 'klima' | 'verschiedenes';
export type CriterionValueType = 'stars' | 'bool' | 'number' | 'text' | 'select';

export interface InspectionCriterion {
  id: number;
  owner_id: number;
  name: string;
  section: CriterionSection;
  value_type: CriterionValueType;
  options: string[] | null;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface InspectionCriterionCreate {
  name: string;
  section?: CriterionSection;
  value_type?: CriterionValueType;
  options?: string[] | null;
  sort_order?: number;
  is_active?: boolean;
}

export interface InspectionCriterionUpdate {
  name?: string;
  section?: CriterionSection;
  value_type?: CriterionValueType;
  options?: string[] | null;
  sort_order?: number;
  is_active?: boolean;
}
