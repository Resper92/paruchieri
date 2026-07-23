import { DatePipe } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { Appointment } from '../../core/models/appointment.model';
import { Service as ServiceItem } from '../../core/models/service.model';
import { Staff } from '../../core/models/staff.model';
import { Role } from '../../core/models/user.model';
import { Auth } from '../../core/services/auth';
import { AppointmentService } from '../../core/services/appointment';
import { ServiceCatalogService } from '../../core/services/service-catalog';
import { StaffService } from '../../core/services/staff';

@Component({
  selector: 'app-appointments',
  imports: [ReactiveFormsModule, DatePipe],
  templateUrl: './appointments.html',
  styleUrl: './appointments.scss',
})
export class Appointments implements OnInit {
  private readonly appointmentService = inject(AppointmentService);
  private readonly staffService = inject(StaffService);
  private readonly serviceCatalog = inject(ServiceCatalogService);
  private readonly auth = inject(Auth);
  private readonly fb = inject(FormBuilder);

  readonly canBook = computed(() => this.auth.currentUser()?.role === Role.Client);

  readonly appointments = signal<Appointment[]>([]);
  readonly staff = signal<Staff[]>([]);
  readonly services = signal<ServiceItem[]>([]);
  readonly errorMessage = signal<string | null>(null);
  readonly isSubmitting = signal(false);

  readonly form = this.fb.nonNullable.group({
    staff_id: [0, [Validators.required, Validators.min(1)]],
    service_id: [0, [Validators.required, Validators.min(1)]],
    start_time: ['', Validators.required],
    end_time: ['', Validators.required],
  });

  ngOnInit(): void {
    this.appointmentService.list().subscribe((appointments) => this.appointments.set(appointments));
    this.staffService.list().subscribe((staff) => this.staff.set(staff));
    this.serviceCatalog.list().subscribe((services) => this.services.set(services));
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const { staff_id, service_id, start_time, end_time } = this.form.getRawValue();
    this.errorMessage.set(null);
    this.isSubmitting.set(true);

    this.appointmentService
      .create({
        staff_id,
        service_id,
        start_time: new Date(start_time).toISOString(),
        end_time: new Date(end_time).toISOString(),
      })
      .subscribe({
        next: (appointment) => {
          this.appointments.update((current) => [...current, appointment]);
          this.form.reset({ staff_id: 0, service_id: 0, start_time: '', end_time: '' });
          this.isSubmitting.set(false);
        },
        error: () => {
          this.isSubmitting.set(false);
          this.errorMessage.set('Could not create the appointment.');
        },
      });
  }
}
