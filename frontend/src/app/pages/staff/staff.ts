import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { Salon } from '../../core/models/salon.model';
import { Staff as StaffMember } from '../../core/models/staff.model';
import { SalonService } from '../../core/services/salon';
import { StaffService } from '../../core/services/staff';

@Component({
  selector: 'app-staff',
  imports: [ReactiveFormsModule],
  templateUrl: './staff.html',
  styleUrl: './staff.scss',
})
export class Staff implements OnInit {
  private readonly staffService = inject(StaffService);
  private readonly salonService = inject(SalonService);
  private readonly fb = inject(FormBuilder);

  readonly staff = signal<StaffMember[]>([]);
  readonly salons = signal<Salon[]>([]);
  readonly errorMessage = signal<string | null>(null);
  readonly isSubmitting = signal(false);

  readonly form = this.fb.nonNullable.group({
    salon_id: [0, [Validators.required, Validators.min(1)]],
    name: ['', Validators.required],
  });

  ngOnInit(): void {
    this.staffService.list().subscribe((staff) => this.staff.set(staff));
    this.salonService.list().subscribe((salons) => this.salons.set(salons));
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.errorMessage.set(null);
    this.isSubmitting.set(true);

    this.staffService.create(this.form.getRawValue()).subscribe({
      next: (member) => {
        this.staff.update((current) => [...current, member]);
        this.form.reset({ salon_id: 0, name: '' });
        this.isSubmitting.set(false);
      },
      error: () => {
        this.isSubmitting.set(false);
        this.errorMessage.set('Could not add the staff member.');
      },
    });
  }
}
