import { computed, Injectable, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, finalize, shareReplay, tap, throwError } from 'rxjs';
import { ApiService } from './api.service';
import { LoginRequest, Token, UserResponse, RegisterRequest } from '../models/auth.models';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly TOKEN_KEY = 'access_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private readonly apiService = inject(ApiService);
  private readonly router = inject(Router);
  private readonly storage = this.getStorage();
  private refreshInFlight$: Observable<Token> | null = null;
  private unauthorizedHandled = false;

  readonly isAuthenticated = signal<boolean>(this.hasToken());
  readonly currentUser = signal<UserResponse | null>(null);
  readonly isAdmin = computed(() => !!this.currentUser()?.is_admin);

  constructor() {
    if (this.hasToken()) {
      this.loadCurrentUser().subscribe({ error: () => undefined });
    }
  }

  login(credentials: LoginRequest): Observable<Token> {
    const body = new URLSearchParams();
    body.set('grant_type', 'password');
    body.set('username', credentials.username);
    body.set('password', credentials.password);
    body.set('scope', '');
    body.set('client_id', '');
    body.set('client_secret', '');

    return this.apiService.post<Token>('/api/auth/login', body.toString()).pipe(
      tap(response => {
        this.storeTokens(response);
        this.loadCurrentUser().subscribe({ error: () => undefined });
      })
    );
  }

  register(userData: RegisterRequest): Observable<UserResponse> {
    return this.apiService.post<UserResponse>('/api/auth/register', userData);
  }

  logout(): void {
    const refreshToken = this.getRefreshToken();
    this.clearSession();
    if (refreshToken) {
      this.apiService.post<void>('/api/auth/logout', { refresh_token: refreshToken }).subscribe({ error: () => undefined });
    }
    this.router.navigate(['/login']);
  }

  handleUnauthorized(returnUrl: string): void {
    this.clearSession();

    if (this.unauthorizedHandled || this.router.url.startsWith('/login')) return;
    this.unauthorizedHandled = true;

    this.router.navigate(['/login'], {
      queryParams: { returnUrl: returnUrl || '/dashboard' }
    });
  }

  getToken(): string | null {
    return this.storage?.getItem(this.TOKEN_KEY) ?? null;
  }

  refreshTokens(): Observable<Token> {
    if (this.refreshInFlight$) return this.refreshInFlight$;

    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      this.handleUnauthorized(this.router.url);
      return throwError(() => new Error('No refresh token available'));
    }

    this.refreshInFlight$ = this.apiService.post<Token>('/api/auth/refresh', { refresh_token: refreshToken }).pipe(
      tap({
        next: response => this.storeTokens(response),
        error: () => this.handleUnauthorized(this.router.url)
      }),
      finalize(() => (this.refreshInFlight$ = null)),
      shareReplay({ bufferSize: 1, refCount: false })
    );
    return this.refreshInFlight$;
  }

  getRefreshToken(): string | null {
    return this.storage?.getItem(this.REFRESH_TOKEN_KEY) ?? null;
  }

  downloadAccountExport(): Observable<Blob> {
    return this.apiService.getBlob('/api/users/me/export');
  }

  loadCurrentUser(): Observable<UserResponse> {
    return this.apiService.get<UserResponse>('/api/users/me').pipe(
      tap(user => this.currentUser.set(user))
    );
  }

  private hasToken(): boolean {
    return !!this.getToken();
  }

  private storeTokens(response: Token): void {
    this.storage?.setItem(this.TOKEN_KEY, response.access_token);
    this.storage?.setItem(this.REFRESH_TOKEN_KEY, response.refresh_token);
    this.unauthorizedHandled = false;
    this.isAuthenticated.set(true);
  }

  private clearSession(): void {
    this.storage?.removeItem(this.TOKEN_KEY);
    this.storage?.removeItem(this.REFRESH_TOKEN_KEY);
    this.isAuthenticated.set(false);
    this.currentUser.set(null);
  }

  private getStorage(): Storage | null {
    return typeof localStorage === 'undefined' ? null : localStorage;
  }
}
