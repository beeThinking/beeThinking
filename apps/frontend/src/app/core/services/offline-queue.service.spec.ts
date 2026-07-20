import { TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiService } from './api.service';
import { OfflineQueueService } from './offline-queue.service';

describe('OfflineQueueService', () => {
  const apiServiceMock = {
    post: vi.fn().mockReturnValue(of({}))
  };

  beforeEach(() => {
    globalThis.localStorage?.clear?.();
    TestBed.configureTestingModule({
      providers: [{ provide: ApiService, useValue: apiServiceMock }]
    });
    vi.clearAllMocks();
    apiServiceMock.post.mockReturnValue(of({}));
  });

  it('should enqueue requests and persist them', () => {
    const service = TestBed.inject(OfflineQueueService);

    service.enqueue('/api/feedings', { feed_type: 'Sirup' }, 'Fütterung');

    expect(service.pending().length).toBe(1);
    expect(service.pending()[0].endpoint).toBe('/api/feedings');
    expect(service.pending()[0].label).toBe('Fütterung');
  });

  it('should flush queued requests in order and clear the queue', () => {
    const service = TestBed.inject(OfflineQueueService);
    service.enqueue('/api/feedings', { a: 1 }, 'Fütterung');
    service.enqueue('/api/harvests', { b: 2 }, 'Ernte');

    service.flush();

    expect(apiServiceMock.post).toHaveBeenCalledTimes(2);
    expect(apiServiceMock.post).toHaveBeenNthCalledWith(1, '/api/feedings', { a: 1 });
    expect(apiServiceMock.post).toHaveBeenNthCalledWith(2, '/api/harvests', { b: 2 });
    expect(service.pending().length).toBe(0);
  });

  it('should keep entries when the flush fails', () => {
    const service = TestBed.inject(OfflineQueueService);
    service.enqueue('/api/feedings', { a: 1 }, 'Fütterung');
    apiServiceMock.post.mockReturnValue(throwError(() => ({ status: 500 })));

    service.flush();

    expect(service.pending().length).toBe(1);
  });
});
