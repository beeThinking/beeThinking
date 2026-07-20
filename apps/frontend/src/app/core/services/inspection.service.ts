import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Inspection, InspectionCreate, InspectionCriterion, InspectionCriterionCreate, InspectionCriterionUpdate, InspectionUpdate } from '../models/inspection.models';

@Injectable({
  providedIn: 'root'
})
export class InspectionService {
  private readonly api = inject(ApiService);

  getInspections(hiveId: number): Observable<Inspection[]> {
    return this.api.get<Inspection[]>(`/api/hives/${hiveId}/inspections`);
  }

  createInspection(hiveId: number, inspection: InspectionCreate): Observable<Inspection> {
    return this.api.post<Inspection>(`/api/hives/${hiveId}/inspections`, inspection);
  }

  updateInspection(hiveId: number, inspectionId: number, update: InspectionUpdate): Observable<Inspection> {
    return this.api.put<Inspection>(`/api/hives/${hiveId}/inspections/${inspectionId}`, update);
  }

  deleteInspection(hiveId: number, inspectionId: number): Observable<void> {
    return this.api.delete<void>(`/api/hives/${hiveId}/inspections/${inspectionId}`);
  }

  getCriteria(): Observable<InspectionCriterion[]> {
    return this.api.get<InspectionCriterion[]>('/api/inspection-criteria');
  }

  createCriterion(criterion: InspectionCriterionCreate): Observable<InspectionCriterion> {
    return this.api.post<InspectionCriterion>('/api/inspection-criteria', criterion);
  }

  updateCriterion(id: number, criterion: InspectionCriterionUpdate): Observable<InspectionCriterion> {
    return this.api.put<InspectionCriterion>(`/api/inspection-criteria/${id}`, criterion);
  }

  deleteCriterion(id: number): Observable<void> {
    return this.api.delete<void>(`/api/inspection-criteria/${id}`);
  }
}
