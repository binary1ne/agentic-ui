import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { AuthService, User } from '../../services/auth.service';
import { ComponentService, NavigationItem } from '../../services/component.service';

// Feature Components
import { RagComponent } from '../rag/rag.component';
import { ToolChatComponent } from '../tool-chat/tool-chat.component';
import { UserManagementComponent } from '../user-management/user-management.component';
import { ComponentManagementComponent } from '../component-management/component-management.component';
import { GuardrailsInsightsComponent } from '../guardrails-insights/guardrails-insights.component';
import { GuardrailsConfigComponent } from '../guardrails-config/guardrails-config.component';
import { RoleManagementComponent } from '../role-management/role-management.component';

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [
        CommonModule,
        RouterModule,
        RagComponent,
        ToolChatComponent,
        UserManagementComponent,
        ComponentManagementComponent,
        GuardrailsInsightsComponent,
        GuardrailsConfigComponent,
        RoleManagementComponent
    ],
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
    currentUser: User | null = null;
    currentView: string = 'home';
    navItems: NavigationItem[] = [];
    loading = true;
    activeRole: string | null = null;

    constructor(
        private authService: AuthService,
        private componentService: ComponentService,
        private router: Router
    ) {
        this.currentUser = this.authService.getCurrentUser();
    }

    ngOnInit(): void {

        this.loadNavigation();
    }

    loadNavigation(): void {
        this.loading = true;
        this.componentService.getNavigationComponents().subscribe({
            next: (items) => {
                this.navItems = items;
                this.loading = false;
            },
            error: (err) => {
                console.error('Error loading navigation:', err);
                this.loading = false;
            }
        });
    }

    onCardClick(componentName: string): void {
        // Map backend component names to view IDs
        const viewMap: { [key: string]: string } = {
            'AGENTIC_RAG': 'rag',
            'NORMAL_CHAT': 'chat',
            'USER_MANAGEMENT': 'users',
            'COMPONENT_MANAGEMENT': 'components',
            'ROLE_MANAGEMENT': 'roles',
            'GUARDRAILS_INSIGHTS': 'guardrails-insights',
            'GUARDRAILS_CONFIGURATION': 'guardrails-config'
        };

        this.currentView = viewMap[componentName] || 'home';
    }

    goBack(): void {
        this.currentView = 'home';
    }

    logout(): void {
        this.authService.logout();
        this.router.navigate(['/login']);
    }
}
