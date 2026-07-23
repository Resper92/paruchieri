import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { Salon } from '../../core/models/salon.model';
import { Service as ServiceItem } from '../../core/models/service.model';
import { SalonService } from '../../core/services/salon';
import { ServiceCatalogService } from '../../core/services/service-catalog';

@Component({
  selector: 'app-services',
  imports: [ReactiveFormsModule],
  templateUrl: './services.html',
  styleUrl: './services.scss',
})
export class Services implements OnInit {
  private readonly serviceCatalog = inject(ServiceCatalogService);
  private readonly salonService = inject(SalonService);
  private readonly fb = inject(FormBuilder);

  readonly services = signal<ServiceItem[]>([]);
  readonly salons = signal<Salon[]>([]);
  readonly errorMessage = signal<string | null>(null);
  readonly isSubmitting = signal(false);

  readonly form = this.fb.nonNullable.group({
    salon_id: [0, [Validators.required, Validators.min(1)]],
    name: ['', Validators.required],
    price: [0, [Validators.required, Validators.min(0)]],
    duration_minutes: [30, [Validators.required, Validators.min(1)]],
  });

  ngOnInit(): void {
    this.serviceCatalog.list().subscribe((services) => this.services.set(services));
    this.salonService.list().subscribe((salons) => this.salons.set(salons));
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.errorMessage.set(null);
    this.isSubmitting.set(true);

    this.serviceCatalog.create(this.form.getRawValue()).subscribe({
      next: (service) => {
        this.services.update((current) => [...current, service]);
        this.form.reset({ salon_id: 0, name: '', price: 0, duration_minutes: 30 });
        this.isSubmitting.set(false);
      },
      error: () => {
        this.isSubmitting.set(false);
        this.errorMessage.set('Could not add the service.');
      },
    });
  }
}
