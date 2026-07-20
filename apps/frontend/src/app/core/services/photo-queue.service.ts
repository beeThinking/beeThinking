import { Injectable, inject, signal } from '@angular/core';
import { BeekeepingService } from './beekeeping.service';

export interface QueuedPhoto {
  id: string;
  file: Blob;
  filename: string;
  hive_id: number;
  caption: string;
  queued_at: string;
}

const DB_NAME = 'beethinking-offline';
const STORE = 'photo-queue';

@Injectable({
  providedIn: 'root'
})
export class PhotoQueueService {
  private readonly beekeeping = inject(BeekeepingService);
  private memoryQueue: QueuedPhoto[] = [];
  private flushing = false;

  readonly pendingCount = signal(0);

  constructor() {
    if (typeof window !== 'undefined') {
      window.addEventListener('online', () => this.flush());
      this.refreshCount();
    }
  }

  async enqueue(file: File, hiveId: number, caption: string): Promise<void> {
    const photo: QueuedPhoto = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      file,
      filename: file.name,
      hive_id: hiveId,
      caption,
      queued_at: new Date().toISOString()
    };
    const db = await this.openDb();
    if (db) {
      await this.withStore(db, 'readwrite', store => store.put(photo));
    } else {
      this.memoryQueue.push(photo);
    }
    await this.refreshCount();
  }

  async flush(): Promise<void> {
    if (this.flushing || (typeof navigator !== 'undefined' && !navigator.onLine)) {
      return;
    }
    this.flushing = true;
    try {
      const photos = await this.all();
      for (const photo of photos) {
        const file = new File([photo.file], photo.filename, { type: photo.file.type || 'image/jpeg' });
        try {
          await new Promise<void>((resolve, reject) => {
            this.beekeeping.uploadPhoto({ file, hive_id: photo.hive_id, caption: photo.caption }).subscribe({
              next: () => resolve(),
              error: error => reject(error)
            });
          });
          await this.remove(photo.id);
        } catch {
          break;
        }
      }
    } finally {
      this.flushing = false;
      await this.refreshCount();
    }
  }

  private async all(): Promise<QueuedPhoto[]> {
    const db = await this.openDb();
    if (!db) {
      return [...this.memoryQueue];
    }
    return this.withStore(db, 'readonly', store => store.getAll()) as Promise<QueuedPhoto[]>;
  }

  private async remove(id: string): Promise<void> {
    const db = await this.openDb();
    if (db) {
      await this.withStore(db, 'readwrite', store => store.delete(id));
    } else {
      this.memoryQueue = this.memoryQueue.filter(photo => photo.id !== id);
    }
  }

  private async refreshCount(): Promise<void> {
    const photos = await this.all();
    this.pendingCount.set(photos.length);
  }

  private openDb(): Promise<IDBDatabase | null> {
    if (typeof indexedDB === 'undefined') {
      return Promise.resolve(null);
    }
    return new Promise(resolve => {
      const request = indexedDB.open(DB_NAME, 1);
      request.onupgradeneeded = () => {
        if (!request.result.objectStoreNames.contains(STORE)) {
          request.result.createObjectStore(STORE, { keyPath: 'id' });
        }
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => resolve(null);
    });
  }

  private withStore<T>(
    db: IDBDatabase,
    mode: IDBTransactionMode,
    action: (store: IDBObjectStore) => IDBRequest<T>
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(STORE, mode);
      const request = action(transaction.objectStore(STORE));
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }
}
