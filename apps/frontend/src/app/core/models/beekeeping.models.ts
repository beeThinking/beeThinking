export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';
export type TaskStatus = 'open' | 'done' | 'cancelled';
export type TaskSource = 'manual' | 'inspection' | 'system';

export interface Photo {
  id: number;
  owner_id: number;
  hive_id: number | null;
  inspection_id: number | null;
  object_key: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  caption: string | null;
  created_at: string;
}

export interface PhotoPreview {
  url: string;
}

export interface PhotoWithPreview extends Photo {
  preview_url: string | null;
}

export interface Task {
  id: number;
  owner_id: number;
  hive_id: number | null;
  apiary_id: number | null;
  title: string;
  description: string | null;
  due_date: string | null;
  priority: TaskPriority;
  status: TaskStatus;
  source: TaskSource;
  created_at: string;
  updated_at: string | null;
  completed_at: string | null;
}

export interface TaskCreate {
  hive_id?: number | null;
  apiary_id?: number | null;
  title: string;
  description?: string;
  due_date?: string;
  priority?: TaskPriority;
  status?: TaskStatus;
  source?: TaskSource;
}

export type TaskUpdate = Partial<TaskCreate>;

export interface Treatment {
  id: number;
  owner_id: number;
  hive_id: number;
  started_at: string;
  ended_at: string | null;
  product: string;
  method: string | null;
  dosage: string | null;
  reason: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface TreatmentCreate {
  hive_id: number;
  started_at: string;
  ended_at?: string;
  product: string;
  method?: string;
  dosage?: string;
  reason?: string;
  notes?: string;
}

export type TreatmentUpdate = Partial<TreatmentCreate>;

export interface Harvest {
  id: number;
  owner_id: number;
  apiary_id: number | null;
  hive_id: number | null;
  harvest_date: string;
  crop_type: string | null;
  amount_kg: number;
  batch_code: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface HarvestCreate {
  apiary_id?: number | null;
  hive_id?: number | null;
  harvest_date: string;
  crop_type?: string;
  amount_kg: number;
  batch_code?: string;
  notes?: string;
}

export type HarvestUpdate = Partial<HarvestCreate>;

export interface DashboardHiveStatus {
  hive_id: number;
  name: string;
  status: string;
  swarm_risk: string;
  latest_inspection_date: string | null;
}

export interface DashboardSummary {
  apiary_count: number;
  hive_count: number;
  open_task_count: number;
  overdue_task_count: number;
  tasks_due_this_week: number;
  treatment_count: number;
  harvest_kg_total: number;
  latest_inspection_date: string | null;
  hives: DashboardHiveStatus[];
}

export interface TimelineEvent {
  type: 'inspection' | 'task' | 'treatment' | 'harvest' | 'photo';
  id: number;
  date: string;
  title: string;
  notes?: string | null;
  status?: string;
  warnings?: string[];
  amount_kg?: number;
  caption?: string | null;
}
