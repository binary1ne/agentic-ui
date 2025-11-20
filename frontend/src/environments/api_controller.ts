import { environment } from './environment';

/**
 * Centralized API Endpoints Controller
 * All API endpoints are defined here for easy management and type safety
 */

const BASE_URL = environment.apiUrl;

export const API_ENDPOINTS = {
    // Authentication Endpoints
    AUTH: {
        LOGIN: `${BASE_URL}/auth/login`,
        SIGNUP: `${BASE_URL}/auth/signup`,
        CHECK_EMAIL: `${BASE_URL}/auth/check-email`,
        SIGNUP_CONFIG: `${BASE_URL}/auth/config/signup`,
    },

    // User Management Endpoints
    USERS: {
        BASE: `${BASE_URL}/users`,
        BY_ID: (id: number) => `${BASE_URL}/users/${id}`,
    },

    // Role Management Endpoints
    ROLES: {
        BASE: `${BASE_URL}/roles`,
        BY_ID: (id: number) => `${BASE_URL}/roles/${id}`,
        ASSIGN: `${BASE_URL}/roles/assign`,
    },

    // Component Management Endpoints
    COMPONENTS: {
        BASE: `${BASE_URL}/components`,
        BY_ID: (id: number) => `${BASE_URL}/components/${id}`,
        NAVIGATION: `${BASE_URL}/components/navigation`,
    },

    // RAG (Agentic Chat) Endpoints
    RAG: {
        UPLOAD: `${BASE_URL}/rag/upload`,
        CHAT: `${BASE_URL}/rag/chat`,
        DOCUMENTS: `${BASE_URL}/rag/documents`,
        DOCUMENT_BY_ID: (id: number) => `${BASE_URL}/rag/documents/${id}`,
    },

    // Tool Chat Endpoints
    CHAT: {
        TOOL_CALLING: `${BASE_URL}/chat/tool-calling`,
        HISTORY: `${BASE_URL}/chat/history`,
    },

    // Guardrails Endpoints
    GUARDRAILS: {
        BASE: `${BASE_URL}/guardrails`,
        RULES: `${BASE_URL}/guardrails/rules`,
        RULE_BY_ID: (id: number) => `${BASE_URL}/guardrails/rules/${id}`,
        INSIGHTS: `${BASE_URL}/guardrails/insights`,
        VALIDATE: `${BASE_URL}/guardrails/validate`,
    },
} as const;

/**
 * Helper function to build query parameters
 */
export function buildQueryParams(params: Record<string, any>): string {
    const queryString = Object.entries(params)
        .filter(([_, value]) => value !== null && value !== undefined)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join('&');
    return queryString ? `?${queryString}` : '';
}

/**
 * Type-safe API endpoint getter
 */
export type ApiEndpoint = typeof API_ENDPOINTS;
