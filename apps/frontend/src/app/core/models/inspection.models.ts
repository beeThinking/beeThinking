export interface Inspection {
  id: number;
  hive_id: number;
  date: string;
  queen_seen: boolean;
  brood_strength: number | null;
  varroa_count: number | null;
  food_stores: number | null;
  notes: string | null;
  created_at: string;
}

export interface InspectionCreate {
  date: string;
  queen_seen?: boolean;
  brood_strength?: number;
  varroa_count?: number;
  food_stores?: number;
  notes?: string;
}

export interface InspectionUpdate {
  date?: string;
  queen_seen?: boolean;
  brood_strength?: number;
  varroa_count?: number;
  food_stores?: number;
  notes?: string;
}
