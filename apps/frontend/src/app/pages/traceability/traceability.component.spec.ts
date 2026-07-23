import { TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { TraceabilityResponse } from '../../core/models/beekeeping.models';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { TraceabilityComponent } from './traceability.component';

describe('TraceabilityComponent', () => {
  const response: TraceabilityResponse = {
    lot_number: '2026-001',
    batch: {
      id: 1,
      owner_id: 1,
      lot_number: '2026-001',
      best_before: '2028-06-10',
      total_amount_kg: 10,
      remaining_kg: 5,
      notes: null,
      created_at: '2026-06-10T10:00:00Z',
      updated_at: null,
      harvests: []
    },
    harvests: [
      {
        harvest: {
          id: 1,
          owner_id: 1,
          apiary_id: 1,
          hive_id: 1,
          harvest_date: '2026-05-01',
          crop_type: 'Frühtracht',
          amount_kg: 10,
          water_content_percent: null,
          batch_code: null,
          batch_id: 1,
          notes: null,
          created_at: '2026-05-01T10:00:00Z',
          updated_at: null
        },
        hive: { id: 1, name: 'Stock 1', stock_number: null },
        apiary: { id: 1, name: 'Garten', stock_number: 'A-1' }
      }
    ],
    inventory_items: [
      { id: 1, article_id: 1, quantity: 5, unit: 'piece', best_before: null, archived: false }
    ]
  };

  const beekeepingServiceMock = {
    getTraceability: vi.fn().mockReturnValue(of(response))
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TraceabilityComponent],
      providers: [{ provide: BeekeepingService, useValue: beekeepingServiceMock }]
    }).compileComponents();

    vi.clearAllMocks();
    beekeepingServiceMock.getTraceability.mockReturnValue(of(response));
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(TraceabilityComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should look up a lot number and render batch, harvest and inventory data', () => {
    const fixture = TestBed.createComponent(TraceabilityComponent);
    const component = fixture.componentInstance as unknown as {
      lotNumber: { set: (v: string) => void };
      search: () => void;
    };

    component.lotNumber.set('2026-001');
    component.search();
    fixture.detectChanges();

    expect(beekeepingServiceMock.getTraceability).toHaveBeenCalledWith('2026-001');
    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('2026-001');
    expect(element.textContent).toContain('Stock 1');
    expect(element.textContent).toContain('Garten');
  });

  it('should show "unknown" fallback when hive or apiary is missing', () => {
    beekeepingServiceMock.getTraceability.mockReturnValue(of({
      ...response,
      harvests: [{ ...response.harvests[0], hive: null, apiary: null }]
    }));
    const fixture = TestBed.createComponent(TraceabilityComponent);
    const component = fixture.componentInstance as unknown as {
      lotNumber: { set: (v: string) => void };
      search: () => void;
    };

    component.lotNumber.set('2026-001');
    component.search();
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('unbekannt');
  });

  it('should show a not-found message on 404', () => {
    beekeepingServiceMock.getTraceability.mockReturnValue(of(null));
    const fixture = TestBed.createComponent(TraceabilityComponent);
    const component = fixture.componentInstance as unknown as {
      lotNumber: { set: (v: string) => void };
      search: () => void;
      notFound: () => boolean;
    };

    component.lotNumber.set('unknown-lot');
    component.search();
    fixture.detectChanges();

    expect(component.notFound()).toBe(true);
    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('nicht gefunden');
  });

  it('should show an error message when the lookup fails unexpectedly', () => {
    beekeepingServiceMock.getTraceability.mockReturnValue(throwError(() => new Error('network error')));
    const fixture = TestBed.createComponent(TraceabilityComponent);
    const component = fixture.componentInstance as unknown as {
      lotNumber: { set: (v: string) => void };
      search: () => void;
      errorMessage: () => string;
    };

    component.lotNumber.set('2026-001');
    component.search();
    fixture.detectChanges();

    expect(component.errorMessage()).not.toBe('');
  });
});
