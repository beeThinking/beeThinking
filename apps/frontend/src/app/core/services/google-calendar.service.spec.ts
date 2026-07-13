import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { beforeEach, describe, expect, it } from 'vitest';
import { environment } from '../../../environments/environment';
import { GoogleCalendarService } from './google-calendar.service';

describe('GoogleCalendarService', () => {
  let service: GoogleCalendarService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()]
    });
    service = TestBed.inject(GoogleCalendarService);
    http = TestBed.inject(HttpTestingController);
  });

  it('loads connection status', () => {
    const status = { enabled: true, connected: false, calendar_name: null, last_sync_at: null, last_error: null };
    service.getStatus().subscribe(result => expect(result).toEqual(status));

    const request = http.expectOne(`${environment.apiUrl}/api/google-calendar/status`);
    expect(request.request.method).toBe('GET');
    request.flush(status);
    http.verify();
  });

  it('starts server-side OAuth', () => {
    service.startConnection().subscribe(result => expect(result.authorization_url).toContain('accounts.google.com'));

    const request = http.expectOne(`${environment.apiUrl}/api/google-calendar/oauth/start`);
    expect(request.request.method).toBe('POST');
    request.flush({ authorization_url: 'https://accounts.google.com/oauth' });
    http.verify();
  });

  it('starts calendar synchronization', () => {
    service.sync().subscribe(result => expect(result.updated).toBe(2));

    const request = http.expectOne(`${environment.apiUrl}/api/google-calendar/sync`);
    expect(request.request.method).toBe('POST');
    request.flush({ created: 1, updated: 2, deleted: 0, synced_at: '2026-07-13T14:00:00Z' });
    http.verify();
  });

  it('disconnects Google Calendar', () => {
    service.disconnect().subscribe();

    const request = http.expectOne(`${environment.apiUrl}/api/google-calendar/connection`);
    expect(request.request.method).toBe('DELETE');
    request.flush(null);
    http.verify();
  });
});
