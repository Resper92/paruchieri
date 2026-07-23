import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth-guard';
import { roleGuard } from './core/guards/role-guard';
import { Role } from './core/models/user.model';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'salons' },
  {
    path: 'login',
    loadComponent: () => import('./pages/login/login').then((m) => m.Login),
  },
  {
    path: 'register',
    loadComponent: () => import('./pages/register/register').then((m) => m.Register),
  },
  {
    path: 'salons',
    loadComponent: () => import('./pages/salons/salons').then((m) => m.Salons),
    canActivate: [authGuard],
  },
  {
    path: 'staff',
    loadComponent: () => import('./pages/staff/staff').then((m) => m.Staff),
    canActivate: [authGuard, roleGuard(Role.Parrucchiere, Role.Superadmin)],
  },
  {
    path: 'services',
    loadComponent: () => import('./pages/services/services').then((m) => m.Services),
    canActivate: [authGuard, roleGuard(Role.Parrucchiere, Role.Superadmin)],
  },
  {
    path: 'appointments',
    loadComponent: () =>
      import('./pages/appointments/appointments').then((m) => m.Appointments),
    canActivate: [authGuard],
  },
  {
    path: 'admin',
    loadComponent: () => import('./pages/admin/admin').then((m) => m.Admin),
    canActivate: [authGuard, roleGuard(Role.Superadmin)],
  },
  { path: '**', redirectTo: 'salons' },
];
