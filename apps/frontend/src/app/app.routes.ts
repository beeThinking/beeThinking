import {Routes} from '@angular/router';
import {DashboardComponent} from './pages/dashboard/dashboard.component';
import {BeehivesComponent} from './pages/beehives/beehives.component';
import {HoneyHarvestComponent} from './pages/honey-harvest/honey-harvest.component';
import {AppointmentsComponent} from './pages/appointments/appointments.component';
import {LoginComponent} from './pages/login/login.component';
import {RegisterComponent} from './pages/register/register.component';
import {authGuard} from './core/guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'dashboard', component: DashboardComponent, canActivate: [authGuard] },
  { path: 'beehives', component: BeehivesComponent, canActivate: [authGuard] },
  { path: 'honey-harvest', component: HoneyHarvestComponent, canActivate: [authGuard] },
  { path: 'appointments', component: AppointmentsComponent, canActivate: [authGuard] }
];
