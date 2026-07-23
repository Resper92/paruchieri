import { HttpClient } from '@angular/common/http';
import { Service, inject } from '@angular/core';

import { environment } from '../../../environments/environment';
import { Salon, SalonCreate } from '../models/salon.model';
import { CrudService } from './crud';

@Service()
export class SalonService extends CrudService<Salon, SalonCreate> {
  constructor() {
    super(inject(HttpClient), `${environment.apiUrl}/salons/`);
  }
}
