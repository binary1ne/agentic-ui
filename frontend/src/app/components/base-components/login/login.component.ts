
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../services/auth.service';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterModule],
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
    email = '';
    password = '';
    selectedRole = '';

    loading = false;
    emailChecked = false;
    showRoleSelection = false;
    error = '';
    signupEnabled = true;

    userRoleFromBackend: string[] = [];

    otp = '';
    showOtpInput = false;

    constructor(
        private authService: AuthService,
        private router: Router
    ) { }

    ngOnInit(): void {
        this.checkSignupStatus();
    }

    checkSignupStatus(): void {
        this.authService.getSignupConfig().subscribe({
            next: (config) => {
                this.signupEnabled = config.enabled;
            },
            error: (err) => console.error('Failed to check signup status', err)
        });
    }

    checkEmail(): void {
        if (!this.email || !this.email.includes('@') || this.emailChecked) return;

        this.loading = true;
        this.error = '';

        this.authService.checkEmail(this.email).subscribe({
            next: (res) => {
                this.loading = false;
                if (res.exists) {
                    this.emailChecked = true;
                    this.showRoleSelection = true;
                    this.userRoleFromBackend = res.roles;
                    // Auto-select the correct role for better UX, but user can change it (and fail validation)
                    if (res.roles && res.roles.length > 0) {
                        this.selectedRole = res.roles.includes('admin') ? 'admin' : res.roles[0];
                    }
                } else {
                    this.error = 'Email not found. Please sign up.';
                }
            },
            error: (err) => {
                this.loading = false;
                this.error = 'Error checking email';
            }
        });
    }

    resetForm(): void {
        this.emailChecked = false;
        this.showRoleSelection = false;
        this.showOtpInput = false;
        this.password = '';
        this.otp = '';
        this.selectedRole = '';
        this.error = '';
    }

    isValid(): boolean {
        if (this.showOtpInput) return !!this.otp && this.otp.length >= 6;
        if (!this.emailChecked) return !!this.email;
        return !!this.password && !!this.selectedRole;
    }

    onSubmit(): void {
        if (this.showOtpInput) {
            this.verifyOtp();
            return;
        }

        if (!this.emailChecked) {
            this.checkEmail();
            return;
        }

        this.loading = true;
        this.error = '';

        this.authService.login(this.email, this.password, this.selectedRole).subscribe({
            next: (response) => {
                if (response.requires_2fa) {
                    this.showOtpInput = true;
                    this.loading = false;
                    return;
                }
                this.handleLoginSuccess(response);
            },
            error: (err) => {
                console.log(err);
                this.error = err.error?.message || 'Login failed';
                this.loading = false;
            }
        });
    }

    verifyOtp(): void {
        this.loading = true;
        this.error = '';

        this.authService.verifyOtp(this.email, this.otp, this.selectedRole).subscribe({
            next: (response) => {
                this.handleLoginSuccess(response);
            },
            error: (err) => {
                this.error = err.error?.message || 'Invalid OTP';
                this.loading = false;
            }
        });
    }

    handleLoginSuccess(response: any): void {
        this.router.navigate(['/dashboard'], {
            state: {
                activeRole: this.selectedRole,
                userName: response.user.full_name || response.user.email,
                userRoles: response.user.roles
            }
        });
    }
}


