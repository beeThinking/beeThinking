import { Injectable } from '@angular/core';
import { InspectionCreate } from '../models/inspection.models';

export interface InspectionDraft {
  hive_id: number;
  data: InspectionCreate;
  updated_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class InspectionDraftService {
  private readonly prefix = 'beethinking:inspection-draft:';

  getDraft(hiveId: number): InspectionDraft | null {
    const raw = this.read(this.key(hiveId));
    if (!raw) {
      return null;
    }
    try {
      return JSON.parse(raw) as InspectionDraft;
    } catch {
      return null;
    }
  }

  saveDraft(hiveId: number, data: InspectionCreate): InspectionDraft {
    const draft: InspectionDraft = {
      hive_id: hiveId,
      data,
      updated_at: new Date().toISOString()
    };
    this.write(this.key(hiveId), JSON.stringify(draft));
    return draft;
  }

  clearDraft(hiveId: number): void {
    try {
      localStorage.removeItem(this.key(hiveId));
    } catch {
      return;
    }
  }

  private key(hiveId: number): string {
    return `${this.prefix}${hiveId}`;
  }

  private read(key: string): string | null {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  }

  private write(key: string, value: string): void {
    try {
      localStorage.setItem(key, value);
    } catch {
      return;
    }
  }
}
