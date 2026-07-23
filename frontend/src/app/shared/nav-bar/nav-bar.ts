import { Component, computed, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';

import { Role } from '../../core/models/user.model';
import { Auth } from '../../core/services/auth';

@Component({
  selector: 'app-nav-bar',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './nav-bar.html',
  styleUrl: './nav-bar.scss',
})
export class NavBar {
  private readonly auth = inject(Auth);
  private readonly router = inject(Router);

  readonly isAuthenticated = this.auth.isAuthenticated;
  readonly currentUser = this.auth.currentUser;

  readonly canManageSalon = computed(() => {
    const role = this.currentUser()?.role;
    return role === Role.Parrucchiere || role === Role.Superadmin;
  });

  readonly isSuperadmin = computed(() => this.currentUser()?.role === Role.Superadmin);

  logout(): void {
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
