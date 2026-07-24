import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { BeekeepingService } from '../../core/services/beekeeping.service';
import { ApiaryService } from '../../core/services/apiary.service';
import { HiveService } from '../../core/services/hive.service';
import { ZuchtreihenComponent } from './zuchtreihen.component';

describe('ZuchtreihenComponent', () => {
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

  const apiary = { id: 1, stock_number: 'ST-1', name: 'Heimstand', address: null, latitude: null, longitude: null, notes: null, owner_id: 1, hive_count: 3, created_at: '', updated_at: null };
  const hive = { id: 5, name: 'Volk 5', apiary_id: 1, is_breeding_candidate: true };

  const beekeepingServiceMock = {
    getZuchtreihen: vi.fn().mockReturnValue(of([zuchtreihe])),
    createZuchtreihe: vi.fn().mockReturnValue(of(zuchtreihe)),
    updateZuchtreihe: vi.fn().mockReturnValue(of(zuchtreihe)),
    deleteZuchtreihe: vi.fn().mockReturnValue(of(undefined))
  };
  const apiaryServiceMock = { getApiaries: vi.fn().mockReturnValue(of([apiary])) };
  const hiveServiceMock = { getHives: vi.fn().mockReturnValue(of([hive])) };

  beforeEach(async () => {
    vi.clearAllMocks();
    beekeepingServiceMock.getZuchtreihen.mockReturnValue(of([zuchtreihe]));
    beekeepingServiceMock.createZuchtreihe.mockReturnValue(of(zuchtreihe));
    beekeepingServiceMock.updateZuchtreihe.mockReturnValue(of(zuchtreihe));
    beekeepingServiceMock.deleteZuchtreihe.mockReturnValue(of(undefined));
    apiaryServiceMock.getApiaries.mockReturnValue(of([apiary]));
    hiveServiceMock.getHives.mockReturnValue(of([hive]));

    await TestBed.configureTestingModule({
      imports: [ZuchtreihenComponent],
      providers: [
        { provide: BeekeepingService, useValue: beekeepingServiceMock },
        { provide: ApiaryService, useValue: apiaryServiceMock },
        { provide: HiveService, useValue: hiveServiceMock },
        provideRouter([])
      ]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(ZuchtreihenComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should load zuchtreihen on init', () => {
    TestBed.createComponent(ZuchtreihenComponent);
    expect(beekeepingServiceMock.getZuchtreihen).toHaveBeenCalledTimes(1);
  });

  it('should create a zuchtreihe on submit', () => {
    const fixture = TestBed.createComponent(ZuchtreihenComponent);
    const component = fixture.componentInstance as unknown as {
      form: { patchValue: (v: unknown) => void; setValue: (v: unknown) => void };
      onSubmit: () => void;
    };

    component.form.setValue({
      name: 'Zuchtreihe 2026-B',
      apiary_id: 1,
      herkunftsvolk_id: null,
      anzahl_larven: null,
      anzahl_angenommen: null,
      anzahl_geschluepft: null,
      anzahl_begattet: null,
      notes: ''
    });
    component.onSubmit();

    expect(beekeepingServiceMock.createZuchtreihe).toHaveBeenCalledWith(
      expect.objectContaining({ name: 'Zuchtreihe 2026-B', apiary_id: 1 })
    );
  });

  it('should delete a zuchtreihe after confirmation', () => {
    vi.stubGlobal('confirm', vi.fn().mockReturnValue(true));
    const fixture = TestBed.createComponent(ZuchtreihenComponent);
    const component = fixture.componentInstance as unknown as { deleteZuchtreihe: (z: typeof zuchtreihe) => void };

    component.deleteZuchtreihe(zuchtreihe);

    expect(beekeepingServiceMock.deleteZuchtreihe).toHaveBeenCalledWith(zuchtreihe.id);
    vi.unstubAllGlobals();
  });
});
