import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const authEndpoints = ['/api/auth/login', '/api/auth/refresh', '/api/auth/logout'];
  const isAuthEndpoint = authEndpoints.some(endpoint => req.url.includes(endpoint));
  const token = authService.getToken();

  const authReq = token && !isAuthEndpoint
    ? req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      })
    : req;

  return next(authReq).pipe(
    catchError(error => {
      if (error instanceof HttpErrorResponse && error.status === 401 && !isAuthEndpoint) {
        return authService.refreshTokens().pipe(
          switchMap(() => {
            const refreshedToken = authService.getToken();
            return next(refreshedToken
              ? req.clone({ setHeaders: { Authorization: `Bearer ${refreshedToken}` } })
              : req);
          }),
          catchError(refreshError => throwError(() => refreshError))
        );
      }

      return throwError(() => error);
    })
  );
};
