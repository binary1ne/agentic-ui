import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
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
}

@Injectable({
    providedIn: 'root'
})
export class ComponentService {
    constructor(private http: HttpClient) { }

    getAllComponents(): Observable<ComponentList> {
        return this.http.get<ComponentList>(API_ENDPOINTS.COMPONENTS.BASE);
    }

    getNavigationComponents(): Observable<NavigationItem[]> {
        return this.http.get<{ navigation: NavigationItem[] }>(API_ENDPOINTS.COMPONENTS.NAVIGATION).pipe(
            map(response => response.navigation || [])
        );
    }

    getComponentAccess(componentId: number): Observable<ComponentAccess[]> {
        return this.http.get<ComponentAccess[]>(API_ENDPOINTS.COMPONENTS.BY_ID(componentId));
    }

    updateComponentAccess(id: number, data: Partial<ComponentAccess>): Observable<ComponentAccess> {
        return this.http.put<ComponentAccess>(API_ENDPOINTS.COMPONENTS.BY_ID(id), data);
    }
}
