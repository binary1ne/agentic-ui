import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_ENDPOINTS } from '../../environments/api_controller';

export interface Document {
    id: number;
    filename: string;
    user_id: number;
    uploaded_at: string;
    file_size: number;
}

export interface ChatResponse {
    answer: string;
    sources: Array<{
        content: string;
        metadata: any;
    }>;
    use_internet: boolean;
}

@Injectable({
    providedIn: 'root'
})
export class RagService {
    constructor(private http: HttpClient) { }

    uploadDocument(file: File): Observable<any> {
        const formData = new FormData();
        formData.append('file', file);
        return this.http.post(API_ENDPOINTS.RAG.UPLOAD, formData);
    }

    chat(question: string, useInternet: boolean = false): Observable<ChatResponse> {
        return this.http.post<ChatResponse>(API_ENDPOINTS.RAG.CHAT, {
            question,
            use_internet: useInternet
        });
    }

    getDocuments(): Observable<Document[]> {
        return this.http.get<Document[]>(API_ENDPOINTS.RAG.DOCUMENTS);
    }

    deleteDocument(id: number): Observable<any> {
        return this.http.delete(API_ENDPOINTS.RAG.DOCUMENT_BY_ID(id));
    }
}
