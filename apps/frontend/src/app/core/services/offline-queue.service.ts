import { Injectable, inject, signal } from '@angular/core';
import { ApiService } from './api.service';

export interface QueuedRequest {
  id: string;
  endpoint: string;
  body: unknown;
  label: string;
  queued_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class OfflineQueueService {
  private readonly api = inject(ApiService);
  private readonly storageKey = 'beethinking:offline-queue';
  private flushing = false;

  readonly pending = signal<QueuedRequest[]>(this.load());

  constructor() {
    if (typeof window !== 'undefined') {
      window.addEventListener('online', () => this.flush());
    }
  }

  enqueue(endpoint: string, body: unknown, label: string): QueuedRequest {
    const request: QueuedRequest = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      endpoint,
      body,
      label,
      queued_at: new Date().toISOString()
    };
    const next = [...this.pending(), request];
    this.persist(next);
    return request;
  }

  flush(): void {
    if (this.flushing || typeof navigator !== 'undefined' && !navigator.onLine) {
      return;
    }
    const [head] = this.pending();
    if (!head) {
      return;
    }
    this.flushing = true;
    this.api.post(head.endpoint, head.body).subscribe({
      next: () => {
        this.persist(this.pending().filter(item => item.id !== head.id));
        this.flushing = false;
        this.flush();
      },
      error: () => {
        this.flushing = false;
      }
    });
  }

  private load(): QueuedRequest[] {
    try {
      const raw = localStorage.getItem(this.storageKey);
      return raw ? (JSON.parse(raw) as QueuedRequest[]) : [];
    } catch {
      return [];
    }
  }

  private persist(requests: QueuedRequest[]): void {
    this.pending.set(requests);
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(requests));
    } catch {
      return;
    }
  }
}
