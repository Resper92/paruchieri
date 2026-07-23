import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { Role } from '../models/user.model';
import { Auth } from '../services/auth';

export const roleGuard = (...allowedRoles: Role[]): CanActivateFn => {
  return () => {
    const auth = inject(Auth);
    const router = inject(Router);

    const role = auth.currentUser()?.role;
    if (role && allowedRoles.includes(role)) {
      return true;
    }

    return router.parseUrl('/salons');
  };
};
