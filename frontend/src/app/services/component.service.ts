import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, BehaviorSubject } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';
import { API_ENDPOINTS } from '../../environments/api_controller';

export interface ComponentList {
    assignable: string[];
    admin_only: string[];
}

export interface ComponentAccess {
    id: number;
    role: string;
    component_name: string;
    has_access: boolean;
}

export interface NavigationItem {
    name: string;
    label: string;
    icon: string;
    description: string;
    admin_only: boolean;
    mode: string;
    value: string;
}

@Injectable({
    providedIn: 'root'
})
export class ComponentService {
    private userComponentsSubject = new BehaviorSubject<string[]>([]);
    public userComponents$ = this.userComponentsSubject.asObservable();

    constructor(private http: HttpClient) { }

    getAllComponents(): Observable<ComponentList> {
        return this.http.get<ComponentList>(API_ENDPOINTS.COMPONENTS.BASE);
    }

    getNavigationComponents(): Observable<NavigationItem[]> {
        return this.http.get<{ navigation: NavigationItem[] }>(API_ENDPOINTS.COMPONENTS.NAVIGATION).pipe(
            map(response => response.navigation || []),  // extracts array
            catchError(error => {
                console.error('Error fetching navigation:', error);
                return of([]);  // return empty array on error
            })
        );
    }


    /**
     * Get list of components accessible by current user
     */
    getUserComponents(): Observable<string[]> {
        return this.http.get<{ components: string[] }>(API_ENDPOINTS.COMPONENTS.BASE + '/user').pipe(
            map(response => response.components),
            tap(components => this.userComponentsSubject.next(components)),
            catchError(error => {
                console.error('Error fetching user components:', error);
                return of([]);
            })
        );
    }

    /**
     * Check if user has access to a specific component
     */
    hasComponentAccess(componentName: string): Observable<boolean> {
        const currentComponents = this.userComponentsSubject.value;

        if (currentComponents.length === 0) {
            // Load components if not cached
            return this.getUserComponents().pipe(
                map(components => components.includes(componentName))
            );
        }

        return of(currentComponents.includes(componentName));
    }

    /**
     * Refresh user components cache
     */
    refreshComponents(): Observable<string[]> {
        return this.getUserComponents();
    }

    getComponentAccess(componentId: number): Observable<ComponentAccess[]> {
        return this.http.get<ComponentAccess[]>(API_ENDPOINTS.COMPONENTS.BY_ID(componentId));
    }

    updateComponentAccess(id: number, data: Partial<ComponentAccess>): Observable<ComponentAccess> {
        return this.http.put<ComponentAccess>(API_ENDPOINTS.COMPONENTS.BY_ID(id), data);
    }
}
