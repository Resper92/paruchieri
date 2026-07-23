import { HttpClient } from '@angular/common/http';
import { Service, inject } from '@angular/core';

import { environment } from '../../../environments/environment';
import { Appointment, AppointmentCreate } from '../models/appointment.model';
import { CrudService } from './crud';

@Service()
export class AppointmentService extends CrudService<Appointment, AppointmentCreate> {
  constructor() {
    super(inject(HttpClient), `${environment.apiUrl}/appointments/`);
  }
}
