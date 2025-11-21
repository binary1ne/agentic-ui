import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_ENDPOINTS } from '../../environments/api_controller';

export interface Role {
    id: number;
    name: string;
    description?: string;
    created_at: string;
}

@Injectable({
    providedIn: 'root'
})
export class RoleService {
    getRoles() {
      throw new Error('Method not implemented.');
    }
    constructor(private http: HttpClient) { }

    getAllRoles(): Observable<Role[]> {
        return this.http.get<Role[]>(API_ENDPOINTS.ROLES.BASE);
    }

    getRoleById(id: number): Observable<Role> {
        return this.http.get<Role>(API_ENDPOINTS.ROLES.BY_ID(id));
    }

    createRole(name: string, description?: string): Observable<Role> {
        return this.http.post<Role>(API_ENDPOINTS.ROLES.BASE, { name, description });
    }

    updateRole(id: number, data: Partial<Role>): Observable<Role> {
        return this.http.put<Role>(API_ENDPOINTS.ROLES.BY_ID(id), data);
    }

    deleteRole(id: number): Observable<any> {
        return this.http.delete(API_ENDPOINTS.ROLES.BY_ID(id));
    }

    assignRolesToUser(userId: number, roleNames: string[]): Observable<any> {
        return this.http.post(API_ENDPOINTS.ROLES.ASSIGN, {
            user_id: userId,
            role_names: roleNames
        });
    }
}
