import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { GoogleCalendarStatus, GoogleCalendarSyncResult } from '../models/google-calendar.models';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class GoogleCalendarService {
  private readonly api = inject(ApiService);

  getStatus(): Observable<GoogleCalendarStatus> {
    return this.api.get<GoogleCalendarStatus>('/api/google-calendar/status');
  }

  startConnection(): Observable<{ authorization_url: string }> {
    return this.api.post<{ authorization_url: string }>('/api/google-calendar/oauth/start', {});
  }

  sync(): Observable<GoogleCalendarSyncResult> {
    return this.api.post<GoogleCalendarSyncResult>('/api/google-calendar/sync', {});
  }

  disconnect(): Observable<void> {
    return this.api.delete<void>('/api/google-calendar/connection');
  }
}
