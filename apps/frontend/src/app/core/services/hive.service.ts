import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  Hive,
  HiveCopyRequest,
  HiveCreate,
  HiveEvent,
  HiveLifecycleRequest,
  HiveMoveRequest,
  HiveRequeenRequest,
  HiveStatus,
  HiveUpdate,
  Queen,
  QueenUpdate,
  VarroaCheck,
  VarroaCheckCreate
} from '../models/hive.models';
import { StockCard, TimelineEvent, VarroaAssistant, VarroaTreatmentType } from '../models/beekeeping.models';

@Injectable({
  providedIn: 'root'
})
export class HiveService {
  private readonly api = inject(ApiService);

  getHives(status: HiveStatus = 'active'): Observable<Hive[]> {
    return this.api.get<Hive[]>(`/api/hives?status=${status}`);
  }

  getHive(id: number): Observable<Hive> {
    return this.api.get<Hive>(`/api/hives/${id}`);
  }

  getHiveTimeline(id: number): Observable<TimelineEvent[]> {
    return this.api.get<TimelineEvent[]>(`/api/hives/${id}/timeline`);
  }

  getStockCard(id: number): Observable<StockCard> {
    return this.api.get<StockCard>(`/api/hives/${id}/stock-card`);
  }

  getHiveHistory(id: number): Observable<HiveEvent[]> {
    return this.api.get<HiveEvent[]>(`/api/hives/${id}/history`);
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

  archiveHive(id: number, payload: HiveLifecycleRequest): Observable<Hive> {
    return this.api.post<Hive>(`/api/hives/${id}/archive`, payload);
  }

  dissolveHive(id: number, payload: HiveLifecycleRequest): Observable<Hive> {
    return this.api.post<Hive>(`/api/hives/${id}/dissolve`, payload);
  }

  mergeHive(id: number, payload: HiveLifecycleRequest): Observable<Hive> {
    return this.api.post<Hive>(`/api/hives/${id}/merge`, payload);
  }

  moveHive(id: number, payload: HiveMoveRequest): Observable<Hive> {
    return this.api.post<Hive>(`/api/hives/${id}/move`, payload);
  }

  copyHive(id: number, payload: HiveCopyRequest): Observable<Hive> {
    return this.api.post<Hive>(`/api/hives/${id}/copy`, payload);
  }

  requeenHive(id: number, payload: HiveRequeenRequest): Observable<Queen> {
    return this.api.post<Queen>(`/api/hives/${id}/requeen`, payload);
  }

  getQueens(hiveId: number): Observable<Queen[]> {
    return this.api.get<Queen[]>(`/api/queens?hive_id=${hiveId}`);
  }

  getVarroaChecks(hiveId: number): Observable<VarroaCheck[]> {
    return this.api.get<VarroaCheck[]>(`/api/varroa-checks?hive_id=${hiveId}`);
  }

  createVarroaCheck(payload: VarroaCheckCreate): Observable<VarroaCheck> {
    return this.api.post<VarroaCheck>('/api/varroa-checks', payload);
  }

  deleteVarroaCheck(id: number): Observable<void> {
    return this.api.delete<void>(`/api/varroa-checks/${id}`);
  }

  updateQueen(id: number, payload: QueenUpdate): Observable<Queen> {
    return this.api.put<Queen>(`/api/queens/${id}`, payload);
  }

  updateTimelineEntry(id: number, event: TimelineEvent, payload: { date: string; title: string; notes: string }): Observable<{ updated: boolean }> {
    return this.api.patch<{ updated: boolean }>(`/api/hives/${id}/timeline/${event.type}/${event.id}`, payload);
  }

  deleteTimelineEntry(id: number, event: TimelineEvent): Observable<void> {
    return this.api.delete<void>(`/api/hives/${id}/timeline/${event.type}/${event.id}`);
  }

  getHiveQrSvg(id: number): Observable<Blob> {
    return this.api.getBlob(`/api/hives/${id}/qr.svg`);
  }

  getQrLabelSheet(): Observable<Blob> {
    return this.api.getBlob('/api/hives/qr-labels.pdf');
  }
}
