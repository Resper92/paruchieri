import { Component, OnInit, inject, signal } from '@angular/core';

import { AdminService } from '../../core/services/admin';
import { Role, User } from '../../core/models/user.model';

@Component({
  selector: 'app-admin',
  imports: [],
  templateUrl: './admin.html',
  styleUrl: './admin.scss',
})
export class Admin implements OnInit {
  private readonly adminService = inject(AdminService);

  readonly Role = Role;
  readonly roles = [Role.Client, Role.Parrucchiere, Role.Superadmin];
  readonly users = signal<User[]>([]);
  readonly errorMessage = signal<string | null>(null);

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this.adminService.listUsers().subscribe((users) => this.users.set(users));
  }

  changeRole(user: User, role: Role): void {
    if (role === user.role) {
      return;
    }

    this.errorMessage.set(null);
    this.adminService.updateRole(user.id, role).subscribe({
      next: (updated) => {
        this.users.update((current) => current.map((u) => (u.id === updated.id ? updated : u)));
      },
      error: () => {
        this.errorMessage.set(`Could not update role for ${user.email}.`);
      },
    });
  }
}
