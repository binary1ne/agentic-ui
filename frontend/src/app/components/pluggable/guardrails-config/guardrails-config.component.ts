import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GuardrailsService, GuardrailConfig } from '../../../services/guardrails.service';

@Component({
  selector: 'app-guardrails-config',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './guardrails-config.component.html',
  styleUrls: ['./guardrails-config.component.css']
})
export class GuardrailsConfigComponent implements OnInit {
  rules: GuardrailConfig[] = [];

  constructor(private guardrailsService: GuardrailsService) { }

  ngOnInit(): void {
    this.loadRules();
  }

  loadRules(): void {
    this.guardrailsService.getGuardrailsConfig().subscribe(rules => this.rules = rules);
  }

  toggleRule(rule: GuardrailConfig): void {
    this.guardrailsService.updateGuardrail(rule.id, { enabled: rule.enabled }).subscribe();
  }
}
