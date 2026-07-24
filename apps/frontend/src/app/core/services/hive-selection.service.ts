import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  HiveSelectionBatchTaskRequest,
  HiveSelectionBatchTaskResponse,
  HiveSelectionCandidate,
  HiveSelectionFilterRequest
} from '../models/hive-selection.models';

@Injectable({ providedIn: 'root' })
export class HiveSelectionService {
  private readonly api = inject(ApiService);

  filterHives(payload: HiveSelectionFilterRequest): Observable<HiveSelectionCandidate[]> {
    return this.api.post<HiveSelectionCandidate[]>('/api/hive-selection/filter', payload);
  }

  batchCreateTasks(payload: HiveSelectionBatchTaskRequest): Observable<HiveSelectionBatchTaskResponse> {
    return this.api.post<HiveSelectionBatchTaskResponse>('/api/hive-selection/batch-tasks', payload);
  }
}
