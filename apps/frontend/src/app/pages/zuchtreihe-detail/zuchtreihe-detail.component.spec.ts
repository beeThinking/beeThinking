import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { BeekeepingService } from '../../core/services/beekeeping.service';
import { ApiaryService } from '../../core/services/apiary.service';
import { HiveService } from '../../core/services/hive.service';
import { ZuchtreiheDetailComponent } from './zuchtreihe-detail.component';

describe('ZuchtreiheDetailComponent', () => {
  const zuchtreihe = {
    id: 1,
    owner_id: 1,
    name: 'Zuchtreihe 2026-A',
    apiary_id: 1,
    herkunftsvolk_id: 5,
    anzahl_larven: 30,
    anzahl_angenommen: 25,
    anzahl_geschluepft: 20,
    anzahl_begattet: 15,
    notes: null,
    created_at: '2026-07-24T10:00:00Z',
    updated_at: null,
    success_rate_angenommen: 83,
    success_rate_geschluepft: 80,
    success_rate_begattet: 75,
    steps: []
  };

  const step = {
    id: 1,
    zuchtreihe_id: 1,
    name: 'umlarven' as const,
    date: '2026-05-01',
    notes: null,
    task_id: null,
    created_at: '2026-05-01T10:00:00Z',
    updated_at: null
  };

  const apiary = { id: 1, stock_number: 'ST-1', name: 'Heimstand', address: null, latitude: null, longitude: null, notes: null, owner_id: 1, hive_count: 3, created_at: '', updated_at: null };
  const hive = { id: 5, name: 'Volk 5', apiary_id: 1, is_breeding_candidate: true };

  const beekeepingServiceMock = {
    getZuchtreihe: vi.fn().mockReturnValue(of(zuchtreihe)),
    generateBreedingSteps: vi.fn().mockReturnValue(of([step])),
    updateBreedingStep: vi.fn().mockReturnValue(of(step))
  };
  const apiaryServiceMock = { getApiaries: vi.fn().mockReturnValue(of([apiary])) };
  const hiveServiceMock = { getHives: vi.fn().mockReturnValue(of([hive])) };

  beforeEach(async () => {
    vi.clearAllMocks();
    beekeepingServiceMock.getZuchtreihe.mockReturnValue(of(zuchtreihe));
    beekeepingServiceMock.generateBreedingSteps.mockReturnValue(of([step]));
    beekeepingServiceMock.updateBreedingStep.mockReturnValue(of(step));
    apiaryServiceMock.getApiaries.mockReturnValue(of([apiary]));
    hiveServiceMock.getHives.mockReturnValue(of([hive]));

    await TestBed.configureTestingModule({
      imports: [ZuchtreiheDetailComponent],
      providers: [
        { provide: BeekeepingService, useValue: beekeepingServiceMock },
        { provide: ApiaryService, useValue: apiaryServiceMock },
        { provide: HiveService, useValue: hiveServiceMock },
        provideRouter([]),
        { provide: ActivatedRoute, useValue: { snapshot: { paramMap: convertToParamMap({ id: '1' }) } } }
      ]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(ZuchtreiheDetailComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should load the zuchtreihe on init', () => {
    TestBed.createComponent(ZuchtreiheDetailComponent);
    expect(beekeepingServiceMock.getZuchtreihe).toHaveBeenCalledWith(1);
  });

  it('should generate breeding steps from an umlarven date', () => {
    const fixture = TestBed.createComponent(ZuchtreiheDetailComponent);
    const component = fixture.componentInstance as unknown as {
      umlarvenDate: { set: (v: string) => void };
      generateSteps: () => void;
    };

    component.umlarvenDate.set('2026-05-01');
    component.generateSteps();

    expect(beekeepingServiceMock.generateBreedingSteps).toHaveBeenCalledWith(1, '2026-05-01');
  });

  it('should save an edited step date', () => {
    const fixture = TestBed.createComponent(ZuchtreiheDetailComponent);
    const component = fixture.componentInstance as unknown as {
      openStepEdit: (s: typeof step) => void;
      editDate: { set: (v: string) => void };
      saveStep: () => void;
    };

    component.openStepEdit(step);
    component.editDate.set('2026-05-02');
    component.saveStep();

    expect(beekeepingServiceMock.updateBreedingStep).toHaveBeenCalledWith(1, 1, { date: '2026-05-02', notes: null });
  });
});
