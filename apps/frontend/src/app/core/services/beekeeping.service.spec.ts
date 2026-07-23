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
    remaining_kg: 12.5,
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

  it('bottles a batch with the given items', () => {
    const response = { batch: { ...batch, remaining_kg: 8 }, inventory_items: [] };
    service.bottleBatch(1, { items: [{ article_id: 5, quantity: 4, price: 9.9, best_before: '2028-01-01' }] })
      .subscribe(result => expect(result).toEqual(response));

    const request = http.expectOne(`${environment.apiUrl}/api/batches/1/bottle`);
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({ items: [{ article_id: 5, quantity: 4, price: 9.9, best_before: '2028-01-01' }] });
    request.flush(response);
    http.verify();
  });
});

describe('BeekeepingService traceability', () => {
  let service: BeekeepingService;
  let http: HttpTestingController;

  const batch: Batch = {
    id: 1,
    owner_id: 5,
    lot_number: '2026-001',
    best_before: '2028-07-23',
    total_amount_kg: 12.5,
    remaining_kg: 12.5,
    notes: null,
    created_at: '2026-07-23T10:00:00Z',
    updated_at: null,
    harvests: []
  };

  const response = {
    lot_number: '2026-001',
    batch,
    harvests: [],
    inventory_items: []
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()]
    });
    service = TestBed.inject(BeekeepingService);
    http = TestBed.inject(HttpTestingController);
  });

  it('loads traceability data for a lot number', () => {
    service.getTraceability('2026-001').subscribe(result => expect(result).toEqual(response));

    const request = http.expectOne(`${environment.apiUrl}/api/traceability/2026-001`);
    expect(request.request.method).toBe('GET');
    request.flush(response);
    http.verify();
  });

  it('returns null when the lot number is not found', () => {
    service.getTraceability('unknown-lot').subscribe(result => expect(result).toBeNull());

    const request = http.expectOne(`${environment.apiUrl}/api/traceability/unknown-lot`);
    request.flush({ detail: 'Lot number not found' }, { status: 404, statusText: 'Not Found' });
    http.verify();
  });

  it('propagates non-404 errors', () => {
    let caught: unknown = null;
    service.getTraceability('2026-001').subscribe({
      error: error => { caught = error; }
    });

    const request = http.expectOne(`${environment.apiUrl}/api/traceability/2026-001`);
    request.flush({ detail: 'Server error' }, { status: 500, statusText: 'Server Error' });
    http.verify();

    expect(caught).not.toBeNull();
  });
});

describe('BeekeepingService honeybook', () => {
  let service: BeekeepingService;
  let http: HttpTestingController;

  const entries = [
    {
      lot_number: '2026-001',
      status: 'batched' as const,
      harvest_date: '2026-06-01',
      apiary_name: 'Stand Nord',
      hive_name: 'Volk 1',
      crop_type: 'Frühtracht',
      amount_kg: 10,
      water_content_percent: 17.5,
      best_before: '2028-06-01',
      bottled_quantity: 5,
      bottled_articles: ['Glas 500g']
    }
  ];

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()]
    });
    service = TestBed.inject(BeekeepingService);
    http = TestBed.inject(HttpTestingController);
  });

  it('loads the honeybook register for a given year', () => {
    service.getHoneybookRegister(2026).subscribe(result => expect(result).toEqual(entries));

    const request = http.expectOne(`${environment.apiUrl}/api/honeybook/register?year=2026`);
    expect(request.request.method).toBe('GET');
    request.flush(entries);
    http.verify();
  });

  it('loads the honeybook register without a year filter', () => {
    service.getHoneybookRegister().subscribe(result => expect(result).toEqual(entries));

    const request = http.expectOne(`${environment.apiUrl}/api/honeybook/register`);
    expect(request.request.method).toBe('GET');
    request.flush(entries);
    http.verify();
  });

  it('downloads the honeybook register as a pdf', () => {
    const blob = new Blob(['pdf content'], { type: 'application/pdf' });
    service.downloadHoneybookPdf(2026).subscribe(result => expect(result).toEqual(blob));

    const request = http.expectOne(`${environment.apiUrl}/api/honeybook/register.pdf?year=2026`);
    expect(request.request.method).toBe('GET');
    request.flush(blob);
    http.verify();
  });

  it('downloads the treatment journal as a pdf', () => {
    const blob = new Blob(['pdf content'], { type: 'application/pdf' });
    service.downloadTreatmentJournalPdf(2026).subscribe(result => expect(result).toEqual(blob));

    const request = http.expectOne(`${environment.apiUrl}/api/treatments/journal/export.pdf?year=2026`);
    expect(request.request.method).toBe('GET');
    request.flush(blob);
    http.verify();
  });

  it('downloads the inventory material report as a pdf', () => {
    const blob = new Blob(['pdf content'], { type: 'application/pdf' });
    service.downloadInventoryMaterialPdf().subscribe(result => expect(result).toEqual(blob));

    const request = http.expectOne(`${environment.apiUrl}/api/reports/inventory-material.pdf`);
    expect(request.request.method).toBe('GET');
    request.flush(blob);
    http.verify();
  });

  it('downloads the inventory finished goods report as a pdf', () => {
    const blob = new Blob(['pdf content'], { type: 'application/pdf' });
    service.downloadInventoryFinishedGoodsPdf().subscribe(result => expect(result).toEqual(blob));

    const request = http.expectOne(`${environment.apiUrl}/api/reports/inventory-finished-goods.pdf`);
    expect(request.request.method).toBe('GET');
    request.flush(blob);
    http.verify();
  });

  it('downloads the feedings report as a pdf with date range', () => {
    const blob = new Blob(['pdf content'], { type: 'application/pdf' });
    service.downloadFeedingsPdf('2026-01-01', '2026-12-31').subscribe(result => expect(result).toEqual(blob));

    const request = http.expectOne(`${environment.apiUrl}/api/reports/feedings.pdf?from_date=2026-01-01&to_date=2026-12-31`);
    expect(request.request.method).toBe('GET');
    request.flush(blob);
    http.verify();
  });

  it('downloads the feedings report as a pdf without date range', () => {
    const blob = new Blob(['pdf content'], { type: 'application/pdf' });
    service.downloadFeedingsPdf().subscribe(result => expect(result).toEqual(blob));

    const request = http.expectOne(`${environment.apiUrl}/api/reports/feedings.pdf`);
    expect(request.request.method).toBe('GET');
    request.flush(blob);
    http.verify();
  });
});
