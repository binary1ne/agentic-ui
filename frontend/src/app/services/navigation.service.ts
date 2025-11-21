import { Injectable, Type } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root',
})
export class NavigationService {
  constructor(private router: Router) {}

  /**
   * Navigate to a path or load a component dynamically
   * @param mode 'path' for routing, 'component' for dynamic component loading
   * @param value path string or component class reference
   * @param params optional query params or component input data
   */
  navigate(
    mode: String,
    value: string | Type<any> | null,
    params?: { [key: string]: any }
  ): void {
    // Guard against null/undefined
    if (!mode || !value) {
      console.warn('NavigationService: mode or value is missing', { mode, value });
      return;
    }

    if (mode === 'path') {
      // Automatically prepend /dashboard
      const routePath = ['/dashboard', value as string];
      this.router.navigate(routePath, { queryParams: params || {} }).catch(err => {
        console.error('NavigationService: Failed to navigate', err);
      });
    } else if (mode === 'component') {
      // For now, just show alert; replace with dynamic component loader later
      alert(
        `Load component: ${(value as Type<any>).name} with params ${JSON.stringify(
          params || {}
        )}`
      );
    } else {
      console.warn('NavigationService: Invalid mode', mode);
    }
  }
}
