import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../services/user.service';
import { User, AuthService } from '../../services/auth.service';
import { RoleService, Role } from '../../services/role.service';

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './user-management.component.html',
  styleUrls: ['./user-management.component.css']
})
export class UserManagementComponent implements OnInit {
  users: User[] = [];
  roles: Role[] = [];
  showModal = false;
  isEditing = false;
  currentUser: any = { selectedRoles: [] };

  signupEnabled = true;
  updatingConfig = false;
  error = '';

  constructor(
    private userService: UserService,
    private authService: AuthService,
    private roleService: RoleService
  ) { }

  ngOnInit(): void {
    this.loadUsers();
    this.loadSignupConfig();
    this.loadRoles();
  }

  loadSignupConfig(): void {
    this.authService.getSignupConfig().subscribe({
      next: (config) => this.signupEnabled = config.enabled,
      error: (err) => console.error('Failed to load signup config', err)
    });
  }

  toggleSignup(event: any): void {
    const enabled = event.target.checked;
    this.updatingConfig = true;
    this.authService.updateSignupConfig(enabled).subscribe({
      next: (res) => {
        this.signupEnabled = res.enabled;
        this.updatingConfig = false;
      },
      error: (err) => {
        this.error = 'Failed to update signup configuration';
        this.updatingConfig = false;
        event.target.checked = !enabled;
      }
    });
  }

  loadUsers(): void {
    this.userService.getAllUsers().subscribe(users => this.users = users);
  }

  loadRoles(): void {
    console.log('Loading roles...');
    this.roleService.getAllRoles().subscribe({
      next: (roles) => {
        console.log('Roles loaded:', roles);
        this.roles = roles;
      },
      error: (err) => {
        console.error('Failed to load roles', err);
        this.error = 'Failed to load roles. ' + (err.error?.message || err.message);
      }
    });
  }

  openModal(user?: User): void {
    this.isEditing = !!user;
    if (user) {
      this.currentUser = { ...user, selectedRoles: [...user.roles] };
    } else {
      this.currentUser = { selectedRoles: ['user'] };
    }
    this.showModal = true;
  }

  closeModal(): void {
    this.showModal = false;
    this.currentUser = { selectedRoles: [] };
  }

  toggleRole(roleName: string): void {
    const index = this.currentUser.selectedRoles.indexOf(roleName);
    if (index > -1) {
      this.currentUser.selectedRoles.splice(index, 1);
    } else {
      this.currentUser.selectedRoles.push(roleName);
    }
  }

  isRoleSelected(roleName: string): boolean {
    return this.currentUser.selectedRoles?.includes(roleName) || false;
  }

  saveUser(): void {
    if (this.isEditing) {
      // Update existing user
      const updateData: any = {
        full_name: this.currentUser.full_name
      };

      // Include roles if they changed
      if (this.currentUser.selectedRoles) {
        updateData.roles = this.currentUser.selectedRoles;
      }

      this.userService.updateUser(this.currentUser.id, updateData).subscribe(() => {
        this.loadUsers();
        this.closeModal();
      });
    } else {
      // Create new user
      this.userService.createUser(
        this.currentUser.email,
        this.currentUser.password,
        this.currentUser.selectedRoles[0] || 'user',
        this.currentUser.full_name
      ).subscribe({
        next: () => {
          this.loadUsers();
          this.closeModal();
        },
        error: (err) => {
          console.error('Error creating user:', err);
          const errorMsg = err.error ? JSON.stringify(err.error, null, 2) : err.message;
          alert('Failed to create user:\n' + errorMsg);
        }
      });
    }
  }

  deleteUser(user: User): void {
    if (confirm(`Are you sure you want to delete ${user.email}?`)) {
      this.userService.deleteUser(user.id).subscribe(() => this.loadUsers());
    }
  }
}
