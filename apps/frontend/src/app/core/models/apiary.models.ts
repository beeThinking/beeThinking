export interface Apiary {
  id: number;
  name: string;
  address: string | null;
  latitude: number | null;
  longitude: number | null;
  notes: string | null;
  owner_id: number;
  hive_count: number;
  created_at: string;
  updated_at: string | null;
}

export interface ApiaryCreate {
  name: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  notes?: string;
}

export interface ApiaryUpdate {
  name?: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  notes?: string;
}
