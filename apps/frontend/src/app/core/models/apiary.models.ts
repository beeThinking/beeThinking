export interface Apiary {
  id: number;
  stock_number: string;
  name: string | null;
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
  stock_number: string;
  name?: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  notes?: string;
}

export interface ApiaryUpdate {
  stock_number?: string;
  name?: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  notes?: string;
}

export type ApiaryMemberRole = 'owner' | 'admin' | 'member' | 'viewer';

export interface ApiaryMember {
  id: number;
  apiary_id: number;
  user_id: number;
  role: ApiaryMemberRole;
  invited_by_user_id: number | null;
  accepted_at: string | null;
  created_at: string;
  user: {
    id: number;
    username: string;
    email: string;
  };
  apiary: {
    id: number;
    stock_number: string;
    name: string | null;
  };
}
