import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { Salon } from '../../core/models/salon.model';
import { Role } from '../../core/models/user.model';
import { Auth } from '../../core/services/auth';
import { SalonService } from '../../core/services/salon';

@Component({
  selector: 'app-salons',
  imports: [ReactiveFormsModule],
  templateUrl: './salons.html',
  styleUrl: './salons.scss',
})
export class Salons implements OnInit {
  private readonly salonService = inject(SalonService);
  private readonly auth = inject(Auth);
  private readonly fb = inject(FormBuilder);

  readonly canCreate = computed(() => {
    const role = this.auth.currentUser()?.role;
    return role === Role.Parrucchiere || role === Role.Superadmin;
  });

  readonly salons = signal<Salon[]>([]);
  readonly errorMessage = signal<string | null>(null);
  readonly isSubmitting = signal(false);

  readonly form = this.fb.nonNullable.group({
    name: ['', Validators.required],
    address: [''],
  });

  ngOnInit(): void {
    this.salonService.list().subscribe((salons) => this.salons.set(salons));
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const ownerId = this.auth.currentUser()?.id;
    if (!ownerId) {
      this.errorMessage.set('You must be logged in to create a salon.');
      return;
    }

    const { name, address } = this.form.getRawValue();
    this.errorMessage.set(null);
    this.isSubmitting.set(true);

    this.salonService.create({ owner_id: ownerId, name, address: address || null }).subscribe({
      next: (salon) => {
        this.salons.update((current) => [...current, salon]);
        this.form.reset({ name: '', address: '' });
        this.isSubmitting.set(false);
      },
      error: () => {
        this.isSubmitting.set(false);
        this.errorMessage.set('Could not create the salon.');
      },
    });
  }
}
