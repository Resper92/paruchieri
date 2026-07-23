import { HttpClient } from '@angular/common/http';
import { Service, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Role, User } from '../models/user.model';

@Service()
export class AdminService {
  private readonly http = inject(HttpClient);

  listUsers(skip = 0, limit = 100): Observable<User[]> {
    return this.http.get<User[]>(`${environment.apiUrl}/admin/users`, {
      params: { skip, limit },
    });
  }

  updateRole(userId: number, role: Role): Observable<User> {
    return this.http.patch<User>(`${environment.apiUrl}/admin/users/${userId}/role`, { role });
  }
}
