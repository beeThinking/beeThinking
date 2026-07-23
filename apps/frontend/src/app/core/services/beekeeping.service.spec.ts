import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { beforeEach, describe, expect, it } from 'vitest';
import { environment } from '../../../environments/environment';
import { Batch } from '../models/beekeeping.models';
import { BeekeepingService } from './beekeeping.service';

describe('BeekeepingService batches', () => {
  let service: BeekeepingService;
  let http: HttpTestingController;

  const batch: Batch = {
    id: 1,
    owner_id: 5,
    lot_number: '2026-001',
    best_before: '2028-07-23',
    total_amount_kg: 12.5,
    notes: null,
    created_at: '2026-07-23T10:00:00Z',
    updated_at: null,
    harvests: []
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()]
    });
    service = TestBed.inject(BeekeepingService);
    http = TestBed.inject(HttpTestingController);
  });

  it('loads all batches', () => {
    service.getBatches().subscribe(result => expect(result).toEqual([batch]));

    const request = http.expectOne(`${environment.apiUrl}/api/batches`);
    expect(request.request.method).toBe('GET');
    request.flush([batch]);
    http.verify();
  });

  it('creates a batch with the given harvest ids', () => {
    service.createBatch({ harvest_ids: [10, 11], best_before: '2028-07-23' }).subscribe(result => expect(result).toEqual(batch));

    const request = http.expectOne(`${environment.apiUrl}/api/batches`);
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({ harvest_ids: [10, 11], best_before: '2028-07-23' });
    request.flush(batch);
    http.verify();
  });

  it('updates a batch', () => {
    service.updateBatch(1, { notes: 'Frühtracht' }).subscribe(result => expect(result).toEqual(batch));

    const request = http.expectOne(`${environment.apiUrl}/api/batches/1`);
    expect(request.request.method).toBe('PUT');
    expect(request.request.body).toEqual({ notes: 'Frühtracht' });
    request.flush(batch);
    http.verify();
  });

  it('deletes a batch', () => {
    service.deleteBatch(1).subscribe();

    const request = http.expectOne(`${environment.apiUrl}/api/batches/1`);
    expect(request.request.method).toBe('DELETE');
    request.flush(null);
    http.verify();
  });

  it('attaches a harvest to a batch', () => {
    service.attachHarvestToBatch(1, 10).subscribe(result => expect(result).toEqual(batch));

    const request = http.expectOne(`${environment.apiUrl}/api/batches/1/harvests/10`);
    expect(request.request.method).toBe('POST');
    request.flush(batch);
    http.verify();
  });

  it('detaches a harvest from a batch', () => {
    service.detachHarvestFromBatch(1, 10).subscribe(result => expect(result).toEqual(batch));

    const request = http.expectOne(`${environment.apiUrl}/api/batches/1/harvests/10`);
    expect(request.request.method).toBe('DELETE');
    request.flush(batch);
    http.verify();
  });
});
