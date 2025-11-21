import { Routes } from '@angular/router';
import { LoginComponent } from './components/base-components/login/login.component';
import { SignupComponent } from './components/base-components/signup/signup.component';
import { DashboardComponent } from './components/base-components/dashboard/dashboard.component';
import { authGuard } from './guards/auth.guard';
import { roleGuard } from './guards/role.guard';

// Feature components - Pluggable
import { RagComponent } from './components/pluggable/rag/rag.component';
import { ToolChatComponent } from './components/pluggable/tool-chat/tool-chat.component';
import { GuardrailsInsightsComponent } from './components/pluggable/guardrails-insights/guardrails-insights.component';
import { GuardrailsConfigComponent } from './components/pluggable/guardrails-config/guardrails-config.component';

// Admin components - Base
import { UserManagementComponent } from './components/base-components/user-management/user-management.component';
import { RoleManagementComponent } from './components/base-components/role-management/role-management.component';
import { ComponentManagementComponent } from './components/base-components/component-management/component-management.component';

export const routes: Routes = [
    { path: '', redirectTo: '/login', pathMatch: 'full' },
    { path: 'login', component: LoginComponent },
    { path: 'signup', component: SignupComponent },
    {
        path: 'dashboard',
        component: DashboardComponent,
        canActivate: [authGuard],
        children: [
            // Default redirect to home view
            { path: '', redirectTo: 'home', pathMatch: 'full' },

            // Feature routes - accessible by all authenticated users (with component access)
            {
                path: 'rag',
                component: RagComponent,
                canActivate: [roleGuard],
                data: { requiredComponent: 'AGENTIC_RAG' }
            },
            {
                path: 'chat',
                component: ToolChatComponent,
                canActivate: [roleGuard],
                data: { requiredComponent: 'NORMAL_CHAT' }
            },
            {
                path: 'guardrails',
                component: GuardrailsInsightsComponent,
                canActivate: [roleGuard],
                data: { requiredComponent: 'GUARDRAILS_INSIGHTS' }
            },

            // Admin routes - require specific component access
            {
                path: 'users',
                component: UserManagementComponent,
                canActivate: [roleGuard],
                data: { requiredComponent: 'USER_MANAGEMENT' }
            },
            {
                path: 'roles',
                component: RoleManagementComponent,
                canActivate: [roleGuard],
                data: { requiredComponent: 'ROLE_MANAGEMENT' }
            },
            {
                path: 'components',
                component: ComponentManagementComponent,
                canActivate: [roleGuard],
                data: { requiredComponent: 'COMPONENT_MANAGEMENT' }
            },
            {
                path: 'guardrails/config',
                component: GuardrailsConfigComponent,
                canActivate: [roleGuard],
                data: { requiredComponent: 'GUARDRAILS_CONFIGURATION' }
            }
        ]
    },
    { path: '**', redirectTo: '/login' }
];
