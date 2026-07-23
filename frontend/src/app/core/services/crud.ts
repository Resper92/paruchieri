import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export abstract class CrudService<T, C> {
  protected constructor(
    protected readonly http: HttpClient,
    protected readonly resourceUrl: string,
  ) {}

  list(skip = 0, limit = 100): Observable<T[]> {
    return this.http.get<T[]>(this.resourceUrl, { params: { skip, limit } });
  }

  get(id: number): Observable<T> {
    return this.http.get<T>(`${this.resourceUrl}/${id}`);
  }

  create(payload: C): Observable<T> {
    return this.http.post<T>(this.resourceUrl, payload);
  }
}
