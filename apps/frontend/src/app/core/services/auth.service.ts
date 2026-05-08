import { Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { ApiService } from './api.service';
import { LoginRequest, Token, UserResponse, RegisterRequest } from '../models/auth.models';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly TOKEN_KEY = 'access_token';
  private readonly USER_KEY = 'current_user';

  // Signal to track authentication state
  isAuthenticated = signal<boolean>(this.hasToken());
  currentUser = signal<UserResponse | null>(this.getCurrentUser());

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  login(credentials: LoginRequest): Observable<Token> {
    // Backend expects URL-encoded form data for OAuth2PasswordRequestForm
    const body = new URLSearchParams();
    body.set('grant_type', 'password');
    body.set('username', credentials.username);
    body.set('password', credentials.password);
    body.set('scope', '');
    body.set('client_id', '');
    body.set('client_secret', '');

    return this.apiService.post<Token>('/api/auth/login', body.toString()).pipe(
      tap(response => {
        this.setToken(response.access_token);
        this.isAuthenticated.set(true);
        // Note: Backend doesn't return user info on login, would need separate endpoint
      })
    );
  }

  register(userData: RegisterRequest): Observable<UserResponse> {
    return this.apiService.post<UserResponse>('/api/auth/register', userData);
  }

  logout(): void {
    this.clearToken();
    this.clearUser();
    this.isAuthenticated.set(false);
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  private setToken(token: string): void {
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  private clearToken(): void {
    localStorage.removeItem(this.TOKEN_KEY);
  }

  private hasToken(): boolean {
    return !!this.getToken();
  }

  private getCurrentUser(): UserResponse | null {
    const userJson = localStorage.getItem(this.USER_KEY);
    return userJson ? JSON.parse(userJson) : null;
  }

  private clearUser(): void {
    localStorage.removeItem(this.USER_KEY);
  }

  // Helper method to get authorization header
  getAuthHeader(): { Authorization: string } | {} {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
}
