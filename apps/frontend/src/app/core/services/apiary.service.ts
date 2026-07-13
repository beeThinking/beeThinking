import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Apiary, ApiaryCreate, ApiaryMember, ApiaryMemberRole, ApiaryUpdate } from '../models/apiary.models';
import { BatchActionCreate, VarroaTreatmentType, VarroaWeatherWindow } from '../models/beekeeping.models';

@Injectable({
  providedIn: 'root'
})
export class ApiaryService {
  private readonly api = inject(ApiService);

  getApiaries(): Observable<Apiary[]> {
    return this.api.get<Apiary[]>('/api/apiaries');
  }

  getApiary(id: number): Observable<Apiary> {
    return this.api.get<Apiary>(`/api/apiaries/${id}`);
  }

  createApiary(apiary: ApiaryCreate): Observable<Apiary> {
    return this.api.post<Apiary>('/api/apiaries', apiary);
  }

  updateApiary(id: number, apiary: ApiaryUpdate): Observable<Apiary> {
    return this.api.put<Apiary>(`/api/apiaries/${id}`, apiary);
  }

  deleteApiary(id: number): Observable<void> {
    return this.api.delete<void>(`/api/apiaries/${id}`);
  }

  getMembers(id: number): Observable<ApiaryMember[]> {
    return this.api.get<ApiaryMember[]>(`/api/apiaries/${id}/members`);
  }

  inviteMember(id: number, usernameOrEmail: string, role: Exclude<ApiaryMemberRole, 'owner'>): Observable<ApiaryMember> {
    return this.api.post<ApiaryMember>(`/api/apiaries/${id}/members`, {
      username_or_email: usernameOrEmail,
      role
    });
  }

  updateMemberRole(id: number, memberId: number, role: Exclude<ApiaryMemberRole, 'owner'>): Observable<ApiaryMember> {
    return this.api.put<ApiaryMember>(`/api/apiaries/${id}/members/${memberId}`, { role });
  }

  removeMember(id: number, memberId: number): Observable<void> {
    return this.api.delete<void>(`/api/apiaries/${id}/members/${memberId}`);
  }

  getInvitations(): Observable<ApiaryMember[]> {
    return this.api.get<ApiaryMember[]>('/api/apiaries/invitations');
  }

  acceptInvitation(memberId: number): Observable<ApiaryMember> {
    return this.api.post<ApiaryMember>(`/api/apiaries/invitations/${memberId}/accept`, {});
  }

  declineInvitation(memberId: number): Observable<void> {
    return this.api.delete<void>(`/api/apiaries/invitations/${memberId}`);
  }

  getVarroaWeather(id: number, treatmentType: VarroaTreatmentType = 'formic_acid_short'): Observable<VarroaWeatherWindow[]> {
    return this.api.get<VarroaWeatherWindow[]>(`/api/apiaries/${id}/varroa-weather?treatment_type=${treatmentType}`);
  }

  refreshVarroaWeather(id: number): Observable<VarroaWeatherWindow[]> {
    return this.api.post<VarroaWeatherWindow[]>(`/api/apiaries/${id}/varroa-weather/refresh`, {});
  }

  createBatchAction(id: number, actionType: 'inspection' | 'treatment' | 'feeding' | 'harvest', payload: BatchActionCreate): Observable<{ action_type: string; created: number; hive_ids: number[] }> {
    return this.api.post<{ action_type: string; created: number; hive_ids: number[] }>(`/api/apiaries/${id}/batch-actions/${actionType}`, payload);
  }
}
