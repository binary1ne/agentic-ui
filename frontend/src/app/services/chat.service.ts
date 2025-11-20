import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_ENDPOINTS } from '../../environments/api_controller';

export interface ChatHistory {
    id: number;
    user_id: number;
    message: string;
    response: string;
    chat_type: string;
    timestamp: string;
    metadata: any;
}

export interface ToolChatResponse {
    answer: string;
    tools_used: string[];
    tool_results: Array<{
        tool: string;
        input: string;
        result: string;
    }>;
}

@Injectable({
    providedIn: 'root'
})
export class ChatService {
    constructor(private http: HttpClient) { }

    chatWithTools(message: string): Observable<ToolChatResponse> {
        return this.http.post<ToolChatResponse>(API_ENDPOINTS.CHAT.TOOL_CALLING, { message });
    }

    getChatHistory(): Observable<ChatHistory[]> {
        return this.http.get<ChatHistory[]>(API_ENDPOINTS.CHAT.HISTORY);
    }

    clearChatHistory(): Observable<any> {
        return this.http.delete(API_ENDPOINTS.CHAT.HISTORY);
    }
}
