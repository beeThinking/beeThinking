export type HiveStatus =
  | 'active'
  | 'archived'
  | 'dissolved'
  | 'merged'
  | 'sold'
  | 'dead'
  | 'inactive'
  | 'lost'
  | 'created_by_mistake';
export type HiveType = 'langstroth' | 'dadant' | 'zander' | 'other';

export interface Hive {
  id: number;
  name: string;
  type: HiveType;
  status: HiveStatus;
  is_active: boolean;
  archived_at: string | null;
  merged_into_hive_id: number | null;
  notes: string | null;
  owner_id: number;
  apiary_id: number;
  created_at: string;
  updated_at: string | null;
}

export interface HiveLifecycleRequest {
  reason: string;
  date: string;
  note?: string;
  target_hive_id?: number | null;
}

export interface HiveEvent {
  id: number;
  user_id: number;
  hive_id: number;
  event_type: string;
  event_date: string;
  title: string;
  description: string | null;
  related_entity_type: string | null;
  related_entity_id: number | null;
  metadata_json: Record<string, unknown> | null;
  created_by: number;
  created_at: string;
  updated_at: string | null;
}

export interface HiveCreate {
  name: string;
  apiary_id: number;
  type?: HiveType;
  status?: HiveStatus;
  notes?: string;
}

export interface HiveUpdate {
  name?: string;
  apiary_id?: number;
  type?: HiveType;
  status?: HiveStatus;
  notes?: string;
}
