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
export type ColonyKind = 'wirtschaftsvolk' | 'ableger' | 'schwarm' | 'kunstschwarm' | 'other';

export interface Hive {
  id: number;
  name: string;
  stock_number: string | null;
  type: HiveType;
  colony_kind: ColonyKind;
  status: HiveStatus;
  is_active: boolean;
  archived_at: string | null;
  established_at: string | null;
  tags: string[] | null;
  sort_order: number;
  active_queen_year: number | null;
  active_queen_color: string | null;
  active_queen_marking: string | null;
  queen_introduced_at: string | null;
  merged_into_hive_id: number | null;
  notes: string | null;
  owner_id: number;
  apiary_id: number;
  is_breeding_candidate: boolean;
  scale_enabled: boolean;
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
  stock_number?: string | null;
  type?: HiveType;
  colony_kind?: ColonyKind;
  status?: HiveStatus;
  established_at?: string | null;
  tags?: string[] | null;
  sort_order?: number;
  notes?: string;
  is_breeding_candidate?: boolean;
  scale_enabled?: boolean;
}

export interface HiveUpdate {
  name?: string;
  apiary_id?: number;
  stock_number?: string | null;
  type?: HiveType;
  colony_kind?: ColonyKind;
  status?: HiveStatus;
  established_at?: string | null;
  tags?: string[] | null;
  sort_order?: number;
  notes?: string;
  is_breeding_candidate?: boolean;
  scale_enabled?: boolean;
}

export interface HiveMoveRequest {
  target_apiary_id: number;
  date: string;
  note?: string;
}

export interface HiveCopyRequest {
  date: string;
  name?: string;
  stock_number?: string;
  note?: string;
}

export interface HiveRequeenRequest {
  date: string;
  year: number;
  marking_color?: string;
  marking_code?: string;
  introduced_at?: string;
  name?: string;
  origin?: string;
  reason?: string;
  note?: string;
}

export interface QueenBreedingFields {
  rasse: string | null;
  linie: string | null;
  lebensnummer: string | null;
  paartyp: string | null;

  zuchtbuchnummer_land: string | null;
  zuchtbuchnummer_lv: string | null;
  zuchtbuchnummer_zuechter: string | null;
  zuchtbuchnummer_nr: string | null;
  zuchtbuchnummer_jahr: number | null;

  zuchtbuchnummer_mutter_land: string | null;
  zuchtbuchnummer_mutter_lv: string | null;
  zuchtbuchnummer_mutter_zuechter: string | null;
  zuchtbuchnummer_mutter_nr: string | null;
  zuchtbuchnummer_mutter_jahr: number | null;

  zuchtbuchnummer_drohnen_land: string | null;
  zuchtbuchnummer_drohnen_lv: string | null;
  zuchtbuchnummer_drohnen_zuechter: string | null;
  zuchtbuchnummer_drohnen_nr: string | null;
  zuchtbuchnummer_drohnen_jahr: number | null;

  pedigree_pedigree: string | null;
  pedigree_kasten_nr: string | null;
  pedigree_zuechter: string | null;
  pedigree_jahr: number | null;

  belegstelle_land: string | null;
  belegstelle_verband: string | null;
  belegstelle_nummer: string | null;
  belegstelle_durchgang: string | null;
}

export interface Queen extends QueenBreedingFields {
  id: number;
  owner_id: number;
  hive_id: number | null;
  name: string | null;
  year: number;
  origin: string | null;
  marking_color: string | null;
  marking_code: string | null;
  introduced_at: string | null;
  is_active: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface QueenUpdate extends Partial<QueenBreedingFields> {
  year?: number;
  name?: string | null;
  origin?: string | null;
  marking_color?: string | null;
  marking_code?: string | null;
  introduced_at?: string | null;
  notes?: string | null;
}

export interface VarroaCheck {
  id: number;
  owner_id: number;
  hive_id: number;
  date: string;
  method: string | null;
  mite_count: number | null;
  mites_per_day: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface VarroaCheckCreate {
  hive_id: number;
  date: string;
  method?: string;
  mite_count?: number | null;
  mites_per_day?: number | null;
  notes?: string;
}
