import { HttpClient, HttpParams } from '@angular/common/http';
import { Service, computed, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { RegisterRequest, User } from '../models/user.model';
import { Token } from '../models/token.model';

const TOKEN_KEY = 'access_token';

@Service()
export class Auth {
  private readonly http = inject(HttpClient);
  private readonly currentUserSignal = signal<User | null>(null);
  readonly currentUser = this.currentUserSignal.asReadonly();
  readonly isAuthenticated = computed(() => !!this.token);

  get token(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  login(email: string, password: string): Observable<Token> {
    const body = new HttpParams().set('username', email).set('password', password);
    return this.http
      .post<Token>(`${environment.apiUrl}/auth/login`, body, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      .pipe(tap((token) => localStorage.setItem(TOKEN_KEY, token.access_token)));
  }

  register(payload: RegisterRequest): Observable<User> {
    return this.http.post<User>(`${environment.apiUrl}/auth/register`, payload);
  }

  fetchCurrentUser(): Observable<User> {
    return this.http
      .get<User>(`${environment.apiUrl}/users/me`)
      .pipe(tap((user) => this.currentUserSignal.set(user)));
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    this.currentUserSignal.set(null);
  }
}
