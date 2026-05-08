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
        localStorage.setItem(this.TOKEN_KEY, response.access_token);
        this.isAuthenticated.set(true);
      })
    );
  }

  register(userData: RegisterRequest): Observable<UserResponse> {
    return this.apiService.post<UserResponse>('/api/auth/register', userData);
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    this.isAuthenticated.set(false);
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  private hasToken(): boolean {
    return !!localStorage.getItem(this.TOKEN_KEY);
  }
}
