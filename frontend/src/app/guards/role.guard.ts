import { inject } from '@angular/core';
import { Router, ActivatedRouteSnapshot } from '@angular/router';
import { ComponentService } from '../services/component.service';
import { map, catchError } from 'rxjs/operators';
import { of } from 'rxjs';

/**
 * Role-based route guard that verifies user has access to specific components
 * 
 * Usage in routes:
 * {
 *   path: 'users',
 *   component: UserManagementComponent,
 *   canActivate: [authGuard, roleGuard],
 *   data: { requiredComponent: 'USER_MANAGEMENT' }
 * }
 */
export const roleGuard = (route: ActivatedRouteSnapshot) => {
    const componentService = inject(ComponentService);
    const router = inject(Router);

    const requiredComponent = route.data['requiredComponent'];

    if (!requiredComponent) {
        // No component requirement specified, allow access
        return true;
    }

    // Check if user has access to this component
    return componentService.hasComponentAccess(requiredComponent).pipe(
        map((hasAccess: boolean) => {
            if (hasAccess) {
                return true;
            } else {
                // Redirect to dashboard home if access denied
                console.warn(`Access denied to component: ${requiredComponent}`);
                router.navigate(['/dashboard']);
                return false;
            }
        }),
        catchError((error: any) => {
            console.error('Error checking component access:', error);
            router.navigate(['/dashboard']);
            return of(false);
        })
    );
};
