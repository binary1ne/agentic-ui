import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
    selector: 'app-signup',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterModule],
    templateUrl: './signup.component.html',
    styleUrls: ['./signup.component.css']
})
export class SignupComponent {
    email = '';
    password = '';
    confirmPassword = '';
    fullName = '';

    loading = false;
    error = '';

    constructor(
        private authService: AuthService,
        private router: Router
    ) { }

    isValid(): boolean {
        return !!this.email && !!this.password && !!this.fullName &&
            this.password === this.confirmPassword && this.password.length >= 6;
    }

    onSubmit(): void {
        if (!this.isValid()) return;

        this.loading = true;
        this.error = '';

        this.authService.signup(this.email, this.password, 'user', this.fullName).subscribe({
            next: () => {
                this.router.navigate(['/dashboard']);
            },
            error: (err) => {
                this.error = err.error?.message || 'Registration failed';
                this.loading = false;
            },
            complete: () => {
                this.loading = false;
            }
        });
    }
}
