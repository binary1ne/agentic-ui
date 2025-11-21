import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../../services/user.service';
import { User, AuthService } from '../../../services/auth.service';
import { RoleService, Role } from '../../../services/role.service';

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
      next: (config: any) => this.signupEnabled = config.enabled,
      error: (err: any) => console.error('Failed to load signup config', err)
    });
  }

  toggleSignup(event: any): void {
    const enabled = event.target.checked;
    this.updatingConfig = true;
    this.authService.updateSignupConfig(enabled).subscribe({
      next: (res: any) => {
        this.signupEnabled = res.enabled;
        this.updatingConfig = false;
      },
      error: (err: any) => {
        this.error = 'Failed to update signup configuration';
        this.updatingConfig = false;
        event.target.checked = !enabled;
      }
    });
  }

  loadUsers(): void {
    this.userService.getAllUsers().subscribe({
      next: (users: User[]) => {
        // Normalize roles to ensure they're arrays
        this.users = users.map(user => ({
          ...user,
          roles: this.normalizeRoles(user.roles)
        }));
        console.log('Users loaded:', this.users);
      },
      error: (err: any) => {
        console.error('Failed to load users', err);
        this.error = 'Failed to load users. ' + (err.error?.message || err.message);
      }
    });
  }

  normalizeRoles(roles: any): string[] {
    // If roles is already an array, return it
    if (Array.isArray(roles)) {
      return roles;
    }
    // If roles is a string that looks like an array, parse it
    if (typeof roles === 'string') {
      try {
        // Try to parse as JSON first
        const parsed = JSON.parse(roles);
        return Array.isArray(parsed) ? parsed : [roles];
      } catch {
        // If parsing fails, treat as single role
        return [roles];
      }
    }
    // Default to empty array
    return [];
  }

  loadRoles(): void {
    console.log('Loading roles...');
    this.roleService.getAllRoles().subscribe({
      next: (roles: Role[]) => {
        console.log('Roles loaded - count:', roles?.length);
        console.log('Roles data:', JSON.stringify(roles, null, 2));
        this.roles = roles || [];
        if (this.roles.length === 0) {
          this.error = 'No roles available in the system.';
        }
      },
      error: (err: any) => {
        console.error('Failed to load roles', err);
        this.error = 'Failed to load roles. ' + (err.error?.message || err.message);
      }
    });
  }

  openModal(user?: User): void {
    // Clear any previous errors
    this.error = '';
    
    this.isEditing = !!user;
    if (user) {
      // Ensure roles is an array before spreading
      const userRoles = this.normalizeRoles(user.roles);
      this.currentUser = {
        ...user,
        selectedRoles: [...userRoles],
        file_upload_enabled: user.file_upload_enabled || false,
        two_factor_auth_enabled: user.two_factor_auth_enabled || false
      };
      console.log('Opening modal for user:', user.email, 'with roles:', userRoles);
      console.log('Available roles in system:', this.roles);
    } else {
      // For new users, start with empty roles
      this.currentUser = {
        email: '',
        password: '',
        full_name: '',
        selectedRoles: [],
        file_upload_enabled: false,
        two_factor_auth_enabled: false
      };
      console.log('Opening modal for new user');
      console.log('Available roles in system:', this.roles);
    }
    this.showModal = true;
  }

  closeModal(): void {
    this.showModal = false;
    this.currentUser = { selectedRoles: [] };
  }

  toggleRole(roleName: string): void {
    console.log('toggleRole called for:', roleName);
    console.log('Current selectedRoles before toggle:', this.currentUser.selectedRoles);
    
    const index = this.currentUser.selectedRoles.indexOf(roleName);
    if (index > -1) {
      this.currentUser.selectedRoles.splice(index, 1);
      console.log('Removed role:', roleName);
    } else {
      this.currentUser.selectedRoles.push(roleName);
      console.log('Added role:', roleName);
    }
    
    console.log('Current selectedRoles after toggle:', this.currentUser.selectedRoles);
  }

  isRoleSelected(roleName: string): boolean {
    const selected = this.currentUser.selectedRoles?.includes(roleName) || false;
    return selected;
  }

  saveUser(): void {
    if (this.isEditing) {
      // Update existing user
      const updateData: any = {
        full_name: this.currentUser.full_name,
        file_upload_enabled: this.currentUser.file_upload_enabled,
        two_factor_auth_enabled: this.currentUser.two_factor_auth_enabled
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
      // Note: UserService.createUser might need update to accept these new fields or we pass them in a separate call/object
      // For now, assuming we update the service or pass extra args if supported.
      // Let's update the service call signature in next step if needed, or pass as object.
      // Checking UserService... it likely needs update.
      // For now, I'll assume I can pass them.
      this.userService.createUser(
        this.currentUser.email,
        this.currentUser.password,
        this.currentUser.selectedRoles[0] || 'user',
        this.currentUser.full_name,
        this.currentUser.file_upload_enabled,
        this.currentUser.two_factor_auth_enabled
      ).subscribe({
        next: () => {
          this.loadUsers();
          this.closeModal();
        },
        error: (err: any) => {
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
