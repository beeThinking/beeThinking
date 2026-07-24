import { TaskKind, TaskPriority } from './beekeeping.models';

export interface CriterionAverageFilter {
  criterion_id: number;
  min_average?: number | null;
  max_average?: number | null;
}

export interface HiveSelectionFilterRequest {
  criteria: CriterionAverageFilter[];
  tags: string[];
  match_all_tags: boolean;
}

export interface HiveSelectionCandidate {
  hive_id: number;
  hive_name: string;
  apiary_id: number;
  tags: string[];
  criterion_averages: Record<number, number>;
  inspection_count: number;
}

export interface HiveSelectionBatchTaskRequest {
  hive_ids: number[];
  title: string;
  description?: string;
  due_date?: string;
  kind?: TaskKind;
  priority?: TaskPriority;
}

export interface HiveSelectionBatchTaskResponse {
  created_task_ids: number[];
}
