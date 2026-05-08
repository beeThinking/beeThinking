export type HiveStatus = 'active' | 'inactive' | 'lost';
export type HiveType = 'langstroth' | 'dadant' | 'zander' | 'other';

export interface Hive {
  id: number;
  name: string;
  location: string | null;
  type: HiveType;
  status: HiveStatus;
  notes: string | null;
  owner_id: number;
  created_at: string;
  updated_at: string | null;
}

export interface HiveCreate {
  name: string;
  location?: string;
  type?: HiveType;
  status?: HiveStatus;
  notes?: string;
}

export interface HiveUpdate {
  name?: string;
  location?: string;
  type?: HiveType;
  status?: HiveStatus;
  notes?: string;
}
