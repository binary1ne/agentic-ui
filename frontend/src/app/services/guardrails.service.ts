import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_ENDPOINTS } from '../../environments/api_controller';

export interface GuardrailConfig {
    id: number;
    rule_type: string;
    enabled: boolean;
    severity: string;
    description: string;
    pattern: string;
}

export interface GuardrailLog {
    id: number;
    user_id: number;
    user_email: string;
    detected_rule: string;
    content_snippet: string;
    timestamp: string;
    action_taken: string;
}

@Injectable({
    providedIn: 'root'
})
export class GuardrailsService {
    constructor(private http: HttpClient) { }

    getGuardrailsConfig(): Observable<GuardrailConfig[]> {
        return this.http.get<GuardrailConfig[]>(API_ENDPOINTS.GUARDRAILS.BASE);
    }

    getGuardrailRules(): Observable<GuardrailConfig[]> {
        return this.http.get<GuardrailConfig[]>(API_ENDPOINTS.GUARDRAILS.RULES);
    }

    createGuardrail(data: Partial<GuardrailConfig>): Observable<GuardrailConfig> {
        return this.http.post<GuardrailConfig>(API_ENDPOINTS.GUARDRAILS.RULES, data);
    }

    updateGuardrail(id: number, data: Partial<GuardrailConfig>): Observable<GuardrailConfig> {
        return this.http.put<GuardrailConfig>(API_ENDPOINTS.GUARDRAILS.RULE_BY_ID(id), data);
    }

    deleteGuardrail(id: number): Observable<any> {
        return this.http.delete(API_ENDPOINTS.GUARDRAILS.RULE_BY_ID(id));
    }

    getGuardrailsLogs(): Observable<GuardrailLog[]> {
        return this.http.get<GuardrailLog[]>(API_ENDPOINTS.GUARDRAILS.INSIGHTS);
    }

    validateContent(content: string): Observable<any> {
        return this.http.post(API_ENDPOINTS.GUARDRAILS.VALIDATE, { content });
    }
}
