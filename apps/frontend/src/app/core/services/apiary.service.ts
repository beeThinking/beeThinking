import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Apiary, ApiaryCreate, ApiaryUpdate } from '../models/apiary.models';
import { VarroaTreatmentType, VarroaWeatherWindow } from '../models/beekeeping.models';

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

  getVarroaWeather(id: number, treatmentType: VarroaTreatmentType = 'formic_acid_short'): Observable<VarroaWeatherWindow[]> {
    return this.api.get<VarroaWeatherWindow[]>(`/api/apiaries/${id}/varroa-weather?treatment_type=${treatmentType}`);
  }

  refreshVarroaWeather(id: number): Observable<VarroaWeatherWindow[]> {
    return this.api.post<VarroaWeatherWindow[]>(`/api/apiaries/${id}/varroa-weather/refresh`, {});
  }
}
