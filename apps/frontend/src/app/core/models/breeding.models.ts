export type BreedingStepName =
  | 'pflegevolk_vorbereiten'
  | 'umlarven'
  | 'annahmekontrolle'
  | 'kaefigen_1'
  | 'kaefigen_2'
  | 'schlupf'
  | 'voelkchen_bilden'
  | 'belegstelle'
  | 'abholen';

export const BREEDING_STEP_ORDER: BreedingStepName[] = [
  'pflegevolk_vorbereiten',
  'umlarven',
  'annahmekontrolle',
  'kaefigen_1',
  'kaefigen_2',
  'schlupf',
  'voelkchen_bilden',
  'belegstelle',
  'abholen'
];

export interface BreedingStep {
  id: number;
  zuchtreihe_id: number;
  name: BreedingStepName;
  date: string;
  notes: string | null;
  task_id: number | null;
  created_at: string;
  updated_at: string | null;
}

export interface BreedingStepCreate {
  name: BreedingStepName;
  date: string;
  notes?: string | null;
}

export interface BreedingStepUpdate {
  name?: BreedingStepName;
  date?: string;
  notes?: string | null;
}

export interface BreedingStepsGenerateRequest {
  umlarven_date: string;
}

export interface Zuchtreihe {
  id: number;
  owner_id: number;
  name: string;
  apiary_id: number;
  herkunftsvolk_id: number | null;
  anzahl_larven: number | null;
  anzahl_angenommen: number | null;
  anzahl_geschluepft: number | null;
  anzahl_begattet: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
  success_rate_angenommen: number | null;
  success_rate_geschluepft: number | null;
  success_rate_begattet: number | null;
  steps: BreedingStep[];
}

export interface ZuchtreiheCreate {
  name: string;
  apiary_id: number;
  herkunftsvolk_id?: number | null;
  anzahl_larven?: number | null;
  anzahl_angenommen?: number | null;
  anzahl_geschluepft?: number | null;
  anzahl_begattet?: number | null;
  notes?: string | null;
}

export interface ZuchtreiheUpdate {
  name?: string;
  apiary_id?: number;
  herkunftsvolk_id?: number | null;
  anzahl_larven?: number | null;
  anzahl_angenommen?: number | null;
  anzahl_geschluepft?: number | null;
  anzahl_begattet?: number | null;
  notes?: string | null;
}

export interface CriterionWeight {
  id: number;
  user_id: number;
  criterion_id: number;
  weight: number;
  created_at: string;
  updated_at: string | null;
}

export interface CriterionWeightUpsert {
  criterion_id: number;
  weight: number;
}

export interface BreedingCandidate {
  hive_id: number;
  hive_name: string;
  score: number;
  latest_inspection_id: number | null;
  latest_inspection_date: string | null;
}
