import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_ENDPOINTS } from '../../environments/api_controller';
import { User } from './auth.service';

@Injectable({
    providedIn: 'root'
})
export class UserService {
    constructor(private http: HttpClient) { }

    getAllUsers(): Observable<User[]> {
        return this.http.get<User[]>(API_ENDPOINTS.USERS.BASE);
    }

    getUserById(id: number): Observable<User> {
        return this.http.get<User>(API_ENDPOINTS.USERS.BY_ID(id));
    }

    createUser(email: string, password: string, role: string = 'user', fullName?: string): Observable<User> {
        return this.http.post<User>(API_ENDPOINTS.USERS.BASE, {
            email,
            password,
            role,
            full_name: fullName
        });
    }

    updateUser(id: number, data: Partial<User>): Observable<User> {
        return this.http.put<User>(API_ENDPOINTS.USERS.BY_ID(id), data);
    }

    updateUserRole(id: number, role: string): Observable<User> {
        return this.updateUser(id, { roles: [role] });
    }

    deleteUser(id: number): Observable<any> {
        return this.http.delete(API_ENDPOINTS.USERS.BY_ID(id));
    }
}
