import { Injectable, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { ApiService } from './api.service';
import { LoginRequest, Token, UserResponse, RegisterRequest } from '../models/auth.models';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly TOKEN_KEY = 'access_token';
  private readonly apiService = inject(ApiService);
  private readonly router = inject(Router);
  private readonly storage = this.getStorage();

  readonly isAuthenticated = signal<boolean>(this.hasToken());
  readonly currentUser = signal<UserResponse | null>(null);

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
        this.storage?.setItem(this.TOKEN_KEY, response.access_token);
        this.isAuthenticated.set(true);
      })
    );
  }

  register(userData: RegisterRequest): Observable<UserResponse> {
    return this.apiService.post<UserResponse>('/api/auth/register', userData);
  }

  logout(): void {
    this.storage?.removeItem(this.TOKEN_KEY);
    this.isAuthenticated.set(false);
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return this.storage?.getItem(this.TOKEN_KEY) ?? null;
  }

  private hasToken(): boolean {
    return !!this.getToken();
  }

  private getStorage(): Storage | null {
    return typeof localStorage === 'undefined' ? null : localStorage;
  }
}
