import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ComponentService, ComponentList } from '../../services/component.service';

@Component({
  selector: 'app-component-management',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './component-management.component.html',
  styleUrls: ['./component-management.component.css']
})
export class ComponentManagementComponent implements OnInit {
  assignableComponents: string[] = [];
  adminComponents: string[] = [];
  userComponents: string[] = [];

  constructor(private componentService: ComponentService) { }

  ngOnInit(): void {
    this.componentService.getAllComponents().subscribe({
      next: (data: ComponentList) => {
        this.assignableComponents = data.assignable;
        this.adminComponents = data.admin_only;
      },
      error: (err: any) => {
        console.error('Failed to load components', err);
      }
    });
  }

  isAdminOnly(component: string): boolean {
    return this.adminComponents.includes(component);
  }
}
