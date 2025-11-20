import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RoleService, Role } from '../../services/role.service';
import { UserService } from '../../services/user.service';
import { User } from '../../services/auth.service';

@Component({
    selector: 'app-role-management',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './role-management.component.html',
    styleUrls: ['./role-management.component.css']
})
export class RoleManagementComponent implements OnInit {
    roles: Role[] = [];
    users: User[] = [];
    showRoleModal = false;
    showAssignModal = false;
    isEditing = false;
    currentRole: Partial<Role> = {};
    selectedUser: User | null = null;
    selectedRoles: string[] = [];
    error = '';

    constructor(
        private roleService: RoleService,
        private userService: UserService
    ) { }

    ngOnInit(): void {
        this.loadRoles();
        this.loadUsers();
    }

    loadRoles(): void {
        this.roleService.getAllRoles().subscribe({
            next: (roles) => this.roles = roles,
            error: (err) => {
                this.error = 'Failed to load roles';
                console.error(err);
            }
        });
    }

    loadUsers(): void {
        this.userService.getAllUsers().subscribe({
            next: (users) => this.users = users,
            error: (err) => {
                this.error = 'Failed to load users';
                console.error(err);
            }
        });
    }

    openRoleModal(role?: Role): void {
        this.isEditing = !!role;
        this.currentRole = role ? { ...role } : {};
        this.showRoleModal = true;
    }

    closeRoleModal(): void {
        this.showRoleModal = false;
        this.currentRole = {};
        this.error = '';
    }

    openAssignModal(user: User): void {
        this.selectedUser = user;
        this.selectedRoles = [...user.roles];
        this.showAssignModal = true;
    }

    closeAssignModal(): void {
        this.showAssignModal = false;
        this.selectedUser = null;
        this.selectedRoles = [];
        this.error = '';
    }

    toggleRole(roleName: string): void {
        const index = this.selectedRoles.indexOf(roleName);
        if (index > -1) {
            this.selectedRoles.splice(index, 1);
        } else {
            this.selectedRoles.push(roleName);
        }
    }

    isRoleSelected(roleName: string): boolean {
        return this.selectedRoles.includes(roleName);
    }

    saveRole(): void {
        if (!this.currentRole.name) {
            this.error = 'Role name is required';
            return;
        }

        if (this.isEditing && this.currentRole.id) {
            this.roleService.updateRole(this.currentRole.id, this.currentRole).subscribe({
                next: () => {
                    this.loadRoles();
                    this.closeRoleModal();
                },
                error: (err) => {
                    this.error = err.error?.message || 'Failed to update role';
                }
            });
        } else {
            this.roleService.createRole(this.currentRole.name!, this.currentRole.description).subscribe({
                next: () => {
                    this.loadRoles();
                    this.closeRoleModal();
                },
                error: (err) => {
                    this.error = err.error?.message || 'Failed to create role';
                }
            });
        }
    }

    assignRoles(): void {
        if (!this.selectedUser || this.selectedRoles.length === 0) {
            this.error = 'Please select at least one role';
            return;
        }

        this.roleService.assignRolesToUser(this.selectedUser.id, this.selectedRoles).subscribe({
            next: () => {
                this.loadUsers();
                this.closeAssignModal();
            },
            error: (err) => {
                this.error = err.error?.message || 'Failed to assign roles';
            }
        });
    }

    deleteRole(role: Role): void {
        if (role.name === 'admin' || role.name === 'user') {
            alert('Cannot delete default system roles');
            return;
        }

        if (confirm(`Are you sure you want to delete the role "${role.name}"?`)) {
            this.roleService.deleteRole(role.id).subscribe({
                next: () => this.loadRoles(),
                error: (err) => {
                    alert(err.error?.message || 'Failed to delete role');
                }
            });
        }
    }
}
