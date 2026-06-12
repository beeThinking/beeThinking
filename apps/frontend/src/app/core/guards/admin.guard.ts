import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { catchError, map, of } from 'rxjs';
import { AuthService } from '../services/auth.service';

export const adminGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isAuthenticated()) {
    return router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } });
  }

  const current = authService.currentUser();
  if (current) {
    return current.is_admin ? true : router.createUrlTree(['/dashboard']);
  }

  return authService.loadCurrentUser().pipe(
    map(user => user.is_admin ? true : router.createUrlTree(['/dashboard'])),
    catchError(() => of(router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } })))
  );
};
