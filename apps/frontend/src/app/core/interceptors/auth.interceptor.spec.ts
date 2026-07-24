import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { AuthService } from '../services/auth.service';
import { authInterceptor } from './auth.interceptor';

describe('authInterceptor', () => {
  let http: HttpClient;
  let httpTesting: HttpTestingController;
  let auth: AuthService;
  let storage: Storage;

  beforeEach(() => {
    const values = new Map<string, string>();
    storage = {
      getItem: key => values.get(key) ?? null,
      setItem: (key, value) => values.set(key, value),
      removeItem: key => values.delete(key),
      clear: () => values.clear(),
      key: index => [...values.keys()][index] ?? null,
      get length() { return values.size; }
    } as Storage;
    Object.defineProperty(globalThis, 'localStorage', { configurable: true, value: storage });
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting()
      ]
    });
    http = TestBed.inject(HttpClient);
    httpTesting = TestBed.inject(HttpTestingController);
    auth = TestBed.inject(AuthService);
    storage.setItem('access_token', 'expired-access-token');
    storage.setItem('refresh_token', 'refresh-token');
  });

  it('uses one refresh request and retries concurrent unauthorized requests', () => {
    const first = vi.fn();
    const second = vi.fn();

    http.get('/api/first').subscribe(first);
    http.get('/api/second').subscribe(second);

    const firstRequest = httpTesting.expectOne('/api/first');
    const secondRequest = httpTesting.expectOne('/api/second');
    expect(firstRequest.request.headers.get('Authorization')).toBe('Bearer expired-access-token');
    firstRequest.flush({ detail: 'expired' }, { status: 401, statusText: 'Unauthorized' });
    secondRequest.flush({ detail: 'expired' }, { status: 401, statusText: 'Unauthorized' });

    const refresh = httpTesting.expectOne(request => request.url.endsWith('/api/auth/refresh'));
    expect(refresh.request.headers.has('Authorization')).toBe(false);
    expect(refresh.request.body).toEqual({ refresh_token: 'refresh-token' });
    refresh.flush({ access_token: 'new-access-token', refresh_token: 'new-refresh-token', token_type: 'bearer' });

    const retriedFirst = httpTesting.expectOne('/api/first');
    const retriedSecond = httpTesting.expectOne('/api/second');
    expect(retriedFirst.request.headers.get('Authorization')).toBe('Bearer new-access-token');
    expect(retriedSecond.request.headers.get('Authorization')).toBe('Bearer new-access-token');
    retriedFirst.flush({ value: 'first' });
    retriedSecond.flush({ value: 'second' });

    expect(first).toHaveBeenCalledWith({ value: 'first' });
    expect(second).toHaveBeenCalledWith({ value: 'second' });
    expect(storage.getItem('refresh_token')).toBe('new-refresh-token');
  });

  it('clears tokens and navigates once when refresh fails', () => {
    const router = TestBed.inject(Router);
    const navigate = vi.spyOn(router, 'navigate').mockResolvedValue(true);
    const firstError = vi.fn();
    const secondError = vi.fn();

    http.get('/api/first').subscribe({ error: firstError });
    http.get('/api/second').subscribe({ error: secondError });
    httpTesting.expectOne('/api/first').flush({}, { status: 401, statusText: 'Unauthorized' });
    httpTesting.expectOne('/api/second').flush({}, { status: 401, statusText: 'Unauthorized' });
    httpTesting.expectOne(request => request.url.endsWith('/api/auth/refresh')).flush({}, { status: 401, statusText: 'Unauthorized' });

    expect(firstError).toHaveBeenCalledOnce();
    expect(secondError).toHaveBeenCalledOnce();
    expect(storage.getItem('access_token')).toBeNull();
    expect(storage.getItem('refresh_token')).toBeNull();
    expect(navigate).toHaveBeenCalledOnce();
  });

  it('does not refresh an unauthorized auth endpoint', () => {
    const error = vi.fn();
    http.post('/api/auth/login', {}).subscribe({ error });
    const request = httpTesting.expectOne('/api/auth/login');
    expect(request.request.headers.has('Authorization')).toBe(false);
    request.flush({}, { status: 401, statusText: 'Unauthorized' });

    expect(error).toHaveBeenCalledOnce();
    httpTesting.expectNone(request => request.url.endsWith('/api/auth/refresh'));
    expect(auth.getToken()).toBe('expired-access-token');
  });
});
