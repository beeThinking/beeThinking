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
  next_steps?: string;
  notes?: string;
}
