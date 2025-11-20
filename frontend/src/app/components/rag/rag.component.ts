import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RagService, Document, ChatResponse } from '../../services/rag.service';

@Component({
  selector: 'app-rag',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './rag.component.html',
  styleUrls: ['./rag.component.css']
})
export class RagComponent implements OnInit {
  documents: Document[] = [];
  chatHistory: Array<{ type: string; content: string; timestamp: Date }> = [];
  query = '';
  useInternet = false;
  loading = false;
  uploading = false;

  constructor(private ragService: RagService) { }

  ngOnInit(): void {
    this.loadDocuments();
  }

  loadDocuments(): void {
    this.ragService.getDocuments().subscribe({
      next: (docs) => {
        this.documents = docs;
      },
      error: (err) => console.error('Error loading documents:', err)
    });
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.uploading = true;
      this.ragService.uploadDocument(file).subscribe({
        next: (doc) => {
          this.documents.push(doc);
          this.uploading = false;
          event.target.value = '';
        },
        error: (err) => {
          console.error('Upload error:', err);
          this.uploading = false;
        }
      });
    }
  }

  sendMessage(): void {
    if (!this.query.trim()) return;

    this.chatHistory.push({ type: 'user', content: this.query, timestamp: new Date() });
    const userQuery = this.query;
    this.query = '';
    this.loading = true;

    this.ragService.chat(userQuery, this.useInternet).subscribe({
      next: (response) => {
        this.chatHistory.push({ type: 'ai', content: response.answer, timestamp: new Date() });
        this.loading = false;
      },
      error: (err) => {
        this.chatHistory.push({
          type: 'ai',
          content: 'Error: ' + (err.error?.message || 'Failed to get response'),
          timestamp: new Date()
        });
        this.loading = false;
      }
    });
  }

  deleteDocument(id: number): void {
    if (confirm('Are you sure you want to delete this document?')) {
      this.ragService.deleteDocument(id).subscribe({
        next: () => {
          this.documents = this.documents.filter(d => d.id !== id);
        },
        error: (err) => console.error('Delete error:', err)
      });
    }
  }

  formatFileSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }
}
