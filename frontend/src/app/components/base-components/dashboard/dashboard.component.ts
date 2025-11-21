import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { AuthService, User } from '../../../services/auth.service';
import { ComponentService, NavigationItem } from '../../../services/component.service';
import { RagComponent } from '../../pluggable/rag/rag.component';
import { ToolChatComponent } from '../../pluggable/tool-chat/tool-chat.component';
import { UserManagementComponent } from '../user-management/user-management.component';
import { ComponentManagementComponent } from '../component-management/component-management.component';
import { GuardrailsInsightsComponent } from '../../pluggable/guardrails-insights/guardrails-insights.component';
import { GuardrailsConfigComponent } from '../../pluggable/guardrails-config/guardrails-config.component';
import { RoleManagementComponent } from '../role-management/role-management.component';
import { HeaderComponent } from '../header/header.component';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { NavigationService } from '../../../services/navigation.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    HeaderComponent,
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
  navItems: NavigationItem[] = [];
  loading: boolean = true;
  currentView: 'home' | 'child' = 'home';

  constructor(
    private authService: AuthService,
    private componentService: ComponentService,
    private navigationService: NavigationService,
    private router: Router
  ) {
    this.currentUser = this.authService.getCurrentUser();
  }

  ngOnInit(): void {
    this.loadNavigation();

    // Track route changes to update currentView
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      this.currentView = event.urlAfterRedirects === '/dashboard' ? 'home' : 'child';
    });
  }

  loadNavigation(): void {
    this.loading = true;
    this.componentService.getNavigationComponents().subscribe({
      next: (items: NavigationItem[]) => {
        this.navItems = items;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading navigation:', err);
        this.loading = false;
      }
    });
  }

  onCardClick(item: NavigationItem): void {
    // const routeMap: Record<string, string> = {
    //   'AGENTIC_RAG': 'rag',
    //   'NORMAL_CHAT': 'chat',
    //   'USER_MANAGEMENT': 'users',
    //   'COMPONENT_MANAGEMENT': 'components',
    //   'ROLE_MANAGEMENT': 'roles',
    //   'GUARDRAILS_INSIGHTS': 'guardrails',
    //   'GUARDRAILS_CONFIGURATION': 'guardrails/config'
    // };

    // const route = routeMap[item.label];
    // if (route) this.router.navigate(['/dashboard', route]);

    console.log("item",item);
    const extraParams = { example: 'value' }; // Optional, can be null
    this.navigationService.navigate(item.mode, item.value, extraParams);
  }

  goBack(): void {
    this.router.navigate(['/dashboard']);
  }

  handleLogout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
