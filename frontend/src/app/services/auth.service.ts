import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { API_ENDPOINTS } from '../../environments/api_controller';

export interface User {
    id: number;
    email: string;
    full_name?: string;
    roles: string[];
    activeRole?: string; // The role currently being used
    file_upload_enabled?: boolean;
    two_factor_auth_enabled?: boolean;
    created_at: string;
}

export interface LoginResponse {
    user: User;
    access_token: string;
    requires_2fa?: boolean;
    message?: string;
    email?: string;
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private currentUserSubject = new BehaviorSubject<User | null>(null);
    public currentUser$ = this.currentUserSubject.asObservable();

    private tokenKey = 'access_token';

    constructor(private http: HttpClient) {
        this.loadUserFromStorage();
    }

    signup(email: string, password: string, role: string = 'user', fullName?: string): Observable<LoginResponse> {
        return this.http.post<LoginResponse>(API_ENDPOINTS.AUTH.SIGNUP, {
            email,
            password,
            role,
            full_name: fullName
        }).pipe(
            tap(response => this.handleAuthResponse(response))
        );
    }

    checkEmail(email: string): Observable<any> {
        return this.http.post(API_ENDPOINTS.AUTH.CHECK_EMAIL, { email });
    }

    getSignupConfig(): Observable<{ enabled: boolean }> {
        return this.http.get<{ enabled: boolean }>(API_ENDPOINTS.AUTH.SIGNUP_CONFIG);
    }

    updateSignupConfig(enabled: boolean): Observable<any> {
        return this.http.post(API_ENDPOINTS.AUTH.SIGNUP_CONFIG, { enabled });
    }

    login(email: string, password: string, role?: string): Observable<LoginResponse> {
        return this.http.post<LoginResponse>(API_ENDPOINTS.AUTH.LOGIN, {
            email,
            password,
            role
        }).pipe(
            tap(response => {
                if (!response.requires_2fa) {
                    this.handleAuthResponse(response);
                }
            })
        );
    }

    verifyOtp(email: string, otp: string, role?: string): Observable<LoginResponse> {
        return this.http.post<LoginResponse>(API_ENDPOINTS.AUTH.VERIFY_OTP || '/api/auth/verify-otp', {
            email,
            otp,
            role
        }).pipe(
            tap(response => this.handleAuthResponse(response))
        );
    }

    logout(): void {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem('currentUser');
        this.currentUserSubject.next(null);
    }

    getToken(): string | null {
        return localStorage.getItem(this.tokenKey);
    }

    isAuthenticated(): boolean {
        return !!this.getToken();
    }

    getCurrentUser(): User | null {
        return this.currentUserSubject.value;
    }

    hasRole(roleName: string): boolean {
        const user = this.getCurrentUser();
        return user?.roles?.includes(roleName) || false;
    }

    isAdmin(): boolean {
        return this.hasRole('admin');
    }

    setActiveRole(roleName: string): void {
        const user = this.getCurrentUser();
        if (user && user.roles.includes(roleName)) {
            user.activeRole = roleName;
            localStorage.setItem('currentUser', JSON.stringify(user));
            this.currentUserSubject.next(user);
        }
    }

    getActiveRole(): string | undefined {
        return this.getCurrentUser()?.activeRole;
    }

    private handleAuthResponse(response: LoginResponse): void {
        localStorage.setItem(this.tokenKey, response.access_token);
        // Set default active role to the first role (or 'admin' if present)
        const activeRole = response.user.roles.includes('admin')
            ? 'admin'
            : response.user.roles[0];
        response.user.activeRole = activeRole;
        localStorage.setItem('currentUser', JSON.stringify(response.user));
        this.currentUserSubject.next(response.user);
    }

    private loadUserFromStorage(): void {
        const userJson = localStorage.getItem('currentUser');
        if (userJson) {
            try {
                const user = JSON.parse(userJson);
                this.currentUserSubject.next(user);
            } catch (e) {
                this.logout();
            }
        }
    }
}
