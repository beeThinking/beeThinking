import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Hive, HiveCreate, HiveUpdate } from '../models/hive.models';
import { TimelineEvent, VarroaAssistant, VarroaTreatmentType } from '../models/beekeeping.models';

@Injectable({
  providedIn: 'root'
})
export class HiveService {
  private readonly api = inject(ApiService);

  getHives(): Observable<Hive[]> {
    return this.api.get<Hive[]>('/api/hives');
  }

  getHive(id: number): Observable<Hive> {
    return this.api.get<Hive>(`/api/hives/${id}`);
  }

  getHiveTimeline(id: number): Observable<TimelineEvent[]> {
    return this.api.get<TimelineEvent[]>(`/api/hives/${id}/timeline`);
  }

  getVarroaAssistant(id: number, treatmentType: VarroaTreatmentType = 'formic_acid_short'): Observable<VarroaAssistant> {
    return this.api.get<VarroaAssistant>(`/api/hives/${id}/varroa-assistant?treatment_type=${treatmentType}`);
  }

  createHive(hive: HiveCreate): Observable<Hive> {
    return this.api.post<Hive>('/api/hives', hive);
  }

  updateHive(id: number, hive: HiveUpdate): Observable<Hive> {
    return this.api.put<Hive>(`/api/hives/${id}`, hive);
  }

  deleteHive(id: number): Observable<void> {
    return this.api.delete<void>(`/api/hives/${id}`);
  }
}
