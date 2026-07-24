export interface WeightReading {
  id: number;
  hive_id: number;
  timestamp: string;
  weight_kg: number;
  created_at: string;
}

export interface WeightReadingCreate {
  timestamp?: string;
  weight_kg: number;
}
