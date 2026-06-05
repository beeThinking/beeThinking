import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  DashboardSummary,
  Harvest,
  HarvestCreate,
  HarvestUpdate,
  Photo,
  PhotoPreview,
  Task,
  TaskCreate,
  TaskStatus,
  TaskUpdate,
  Treatment,
  TreatmentCreate,
  TreatmentUpdate
} from '../models/beekeeping.models';

@Injectable({ providedIn: 'root' })
export class BeekeepingService {
  private readonly api = inject(ApiService);

  getDashboardSummary(): Observable<DashboardSummary> {
    return this.api.get<DashboardSummary>('/api/dashboard/summary');
  }

  getTasks(status?: TaskStatus): Observable<Task[]> {
    const query = status ? `?task_status=${status}` : '';
    return this.api.get<Task[]>(`/api/tasks${query}`);
  }

  createTask(task: TaskCreate): Observable<Task> {
    return this.api.post<Task>('/api/tasks', task);
  }

  updateTask(id: number, task: TaskUpdate): Observable<Task> {
    return this.api.put<Task>(`/api/tasks/${id}`, task);
  }

  completeTask(id: number): Observable<Task> {
    return this.api.post<Task>(`/api/tasks/${id}/complete`, {});
  }

  deleteTask(id: number): Observable<void> {
    return this.api.delete<void>(`/api/tasks/${id}`);
  }

  getTreatments(): Observable<Treatment[]> {
    return this.api.get<Treatment[]>('/api/treatments');
  }

  createTreatment(treatment: TreatmentCreate): Observable<Treatment> {
    return this.api.post<Treatment>('/api/treatments', treatment);
  }

  updateTreatment(id: number, treatment: TreatmentUpdate): Observable<Treatment> {
    return this.api.put<Treatment>(`/api/treatments/${id}`, treatment);
  }

  deleteTreatment(id: number): Observable<void> {
    return this.api.delete<void>(`/api/treatments/${id}`);
  }

  getHarvests(): Observable<Harvest[]> {
    return this.api.get<Harvest[]>('/api/harvests');
  }

  createHarvest(harvest: HarvestCreate): Observable<Harvest> {
    return this.api.post<Harvest>('/api/harvests', harvest);
  }

  updateHarvest(id: number, harvest: HarvestUpdate): Observable<Harvest> {
    return this.api.put<Harvest>(`/api/harvests/${id}`, harvest);
  }

  deleteHarvest(id: number): Observable<void> {
    return this.api.delete<void>(`/api/harvests/${id}`);
  }

  getPhotos(): Observable<Photo[]> {
    return this.api.get<Photo[]>('/api/photos');
  }

  uploadPhoto(input: { file: File; hive_id?: number; inspection_id?: number; caption?: string }): Observable<Photo> {
    const form = new FormData();
    form.append('file', input.file);
    if (input.hive_id) {
      form.append('hive_id', String(input.hive_id));
    }
    if (input.inspection_id) {
      form.append('inspection_id', String(input.inspection_id));
    }
    if (input.caption?.trim()) {
      form.append('caption', input.caption.trim());
    }
    return this.api.post<Photo>('/api/photos/upload', form);
  }

  getPhotoPreview(id: number): Observable<PhotoPreview> {
    return this.api.get<PhotoPreview>(`/api/photos/${id}/preview`);
  }

  deletePhoto(id: number): Observable<void> {
    return this.api.delete<void>(`/api/photos/${id}`);
  }
}
