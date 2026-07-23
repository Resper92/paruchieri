import { HttpClient } from '@angular/common/http';
import { Service, inject } from '@angular/core';

import { environment } from '../../../environments/environment';
import { Service as ServiceItem, ServiceCreate } from '../models/service.model';
import { CrudService } from './crud';

@Service()
export class ServiceCatalogService extends CrudService<ServiceItem, ServiceCreate> {
  constructor() {
    super(inject(HttpClient), `${environment.apiUrl}/services/`);
  }
}
