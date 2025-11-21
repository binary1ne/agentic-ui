import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GuardrailsService, GuardrailLog } from '../../../services/guardrails.service';

@Component({
  selector: 'app-guardrails-insights',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './guardrails-insights.component.html',
  styleUrls: ['./guardrails-insights.component.css']
})
export class GuardrailsInsightsComponent implements OnInit {
  logs: GuardrailLog[] = [];

  constructor(private guardrailsService: GuardrailsService) { }

  ngOnInit(): void {
    this.guardrailsService.getGuardrailsLogs().subscribe(logs => this.logs = logs);
  }

  formatDate(timestamp: string): string {
    return new Date(timestamp).toLocaleString();
  }
}
