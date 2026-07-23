import { ApplicationConfig, inject, provideAppInitializer, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideRouter } from '@angular/router';
import { catchError, firstValueFrom, of } from 'rxjs';

import { authInterceptor } from './core/interceptors/auth-interceptor';
import { Auth } from './core/services/auth';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAppInitializer(() => {
      const auth = inject(Auth);
      if (!auth.token) {
        return undefined;
      }
      return firstValueFrom(
        auth.fetchCurrentUser().pipe(
          catchError(() => {
            auth.logout();
            return of(null);
          }),
        ),
      );
    }),
  ]
};
