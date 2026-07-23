import { HttpClient } from '@angular/common/http';
import { Service, inject } from '@angular/core';

import { environment } from '../../../environments/environment';
import { Staff, StaffCreate } from '../models/staff.model';
import { CrudService } from './crud';

@Service()
export class StaffService extends CrudService<Staff, StaffCreate> {
  constructor() {
    super(inject(HttpClient), `${environment.apiUrl}/staff/`);
  }
}
