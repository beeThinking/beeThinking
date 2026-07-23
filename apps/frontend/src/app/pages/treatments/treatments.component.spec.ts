import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { Treatment } from '../../core/models/beekeeping.models';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HiveService } from '../../core/services/hive.service';
import { TreatmentsComponent } from './treatments.component';

describe('TreatmentsComponent', () => {
  const treatments: Treatment[] = [
    {
      id: 1,
      owner_id: 1,
      hive_id: 1,
      started_at: '2026-06-01',
      ended_at: null,
      product: 'Oxalsäure',
      method: null,
      dosage: null,
      reason: null,
      notes: null,
      weather_window_id: null,
      weather_rating: null,
      weather_source: null,
      weather_fetched_at: null,
      created_at: '2026-06-01',
      updated_at: null
    }
  ];

  const beekeepingServiceMock = {
    getTreatments: vi.fn().mockReturnValue(of(treatments)),
    downloadTreatmentJournalPdf: vi.fn()
  };

  const hiveServiceMock = {
    getHives: vi.fn().mockReturnValue(of([])),
    getVarroaAssistant: vi.fn().mockReturnValue(of({ windows: [], source_note: '' }))
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TreatmentsComponent],
      providers: [
        { provide: BeekeepingService, useValue: beekeepingServiceMock },
        { provide: HiveService, useValue: hiveServiceMock }
      ]
    }).compileComponents();

    vi.clearAllMocks();
    beekeepingServiceMock.getTreatments.mockReturnValue(of(treatments));
    hiveServiceMock.getHives.mockReturnValue(of([]));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(TreatmentsComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should trigger the journal pdf download for the current year', () => {
    beekeepingServiceMock.downloadTreatmentJournalPdf.mockReturnValue(of(new Blob(['pdf'])));
    const createObjectURLSpy = vi.fn().mockReturnValue('blob:mock');
    const revokeObjectURLSpy = vi.fn();
    vi.stubGlobal('URL', { createObjectURL: createObjectURLSpy, revokeObjectURL: revokeObjectURLSpy });

    const fixture = TestBed.createComponent(TreatmentsComponent);
    const component = fixture.componentInstance as unknown as { downloadJournalPdf: () => void };
    fixture.detectChanges();

    component.downloadJournalPdf();

    expect(beekeepingServiceMock.downloadTreatmentJournalPdf).toHaveBeenCalledWith(new Date().getFullYear());
    expect(createObjectURLSpy).toHaveBeenCalled();
  });
});
