import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  {
    path: 'login',
    loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./pages/register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard]
  },
  {
    path: 'apiaries',
    loadComponent: () => import('./pages/apiaries/apiaries.component').then(m => m.ApiariesComponent),
    canActivate: [authGuard]
  },
  {
    path: 'beehives',
    loadComponent: () => import('./pages/beehives/beehives.component').then(m => m.BeehivesComponent),
    canActivate: [authGuard]
  },
  {
    path: 'honey-harvest',
    loadComponent: () => import('./pages/honey-harvest/honey-harvest.component').then(m => m.HoneyHarvestComponent),
    canActivate: [authGuard]
  },
  {
    path: 'appointments',
    loadComponent: () => import('./pages/appointments/appointments.component').then(m => m.AppointmentsComponent),
    canActivate: [authGuard]
  },
  {
    path: 'inspections',
    loadComponent: () => import('./pages/inspections/inspections.component').then(m => m.InspectionsComponent),
    canActivate: [authGuard]
  }
];
