import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { HiveService } from '../../core/services/hive.service';
import { StockCardComponent } from './stock-card.component';

describe('StockCardComponent', () => {
  const hive = {
    id: 7,
    name: 'Volk 7',
    stock_number: '7',
    type: 'zander',
    colony_kind: 'ableger',
    status: 'active',
    is_active: true,
    archived_at: null,
    established_at: '2026-05-15',
    tags: ['sanft'],
    active_queen_year: 2026,
    active_queen_color: 'grün',
    active_queen_marking: '12',
    queen_introduced_at: '2026-05-15',
    merged_into_hive_id: null,
    notes: null,
    owner_id: 1,
    apiary_id: 1,
    is_breeding_candidate: false,
    scale_enabled: false,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: null
  };

  const queen = {
    id: 3,
    owner_id: 1,
    hive_id: 7,
    name: null,
    year: 2026,
    origin: null,
    marking_color: 'grün',
    marking_code: '12',
    introduced_at: '2026-05-15',
    is_active: true,
    notes: null,
    rasse: null,
    linie: null,
    lebensnummer: null,
    paartyp: null,
    zuchtbuchnummer_land: null,
    zuchtbuchnummer_lv: null,
    zuchtbuchnummer_zuechter: null,
    zuchtbuchnummer_nr: null,
    zuchtbuchnummer_jahr: null,
    zuchtbuchnummer_mutter_land: null,
    zuchtbuchnummer_mutter_lv: null,
    zuchtbuchnummer_mutter_zuechter: null,
    zuchtbuchnummer_mutter_nr: null,
    zuchtbuchnummer_mutter_jahr: null,
    zuchtbuchnummer_drohnen_land: null,
    zuchtbuchnummer_drohnen_lv: null,
    zuchtbuchnummer_drohnen_zuechter: null,
    zuchtbuchnummer_drohnen_nr: null,
    zuchtbuchnummer_drohnen_jahr: null,
    pedigree_pedigree: null,
    pedigree_kasten_nr: null,
    pedigree_zuechter: null,
    pedigree_jahr: null,
    belegstelle_land: null,
    belegstelle_verband: null,
    belegstelle_nummer: null,
    belegstelle_durchgang: null,
    created_at: '2026-05-15T00:00:00Z',
    updated_at: null
  };

  const stockCard = { hive, qr_url: '/stock-card/7', events: [] };

  const hiveServiceMock = {
    getStockCard: vi.fn().mockReturnValue(of(stockCard)),
    getQueens: vi.fn().mockReturnValue(of([queen])),
    updateHive: vi.fn().mockReturnValue(of({ ...hive, is_breeding_candidate: true })),
    updateQueen: vi.fn().mockReturnValue(of({ ...queen, rasse: 'Carnica' })),
    getHiveQrSvg: vi.fn().mockReturnValue(of(new Blob())),
    getHiveAnalytics: vi.fn().mockReturnValue(of({
      hive_id: 7,
      from_date: null,
      to_date: null,
      grouping: 'month',
      kpi: { total_harvest_kg: 0, total_feeding_kg_or_l: 0, inspection_count: 0, treatment_count: 0, event_count: 0 },
      chart: []
    })),
    getWeightReadings: vi.fn().mockReturnValue(of([]))
  };

  const paramMap = convertToParamMap({ hiveId: '7' });
  const activatedRouteMock = { snapshot: { paramMap } };

  beforeEach(async () => {
    vi.clearAllMocks();
    hiveServiceMock.getStockCard.mockReturnValue(of(stockCard));
    hiveServiceMock.getQueens.mockReturnValue(of([queen]));
    hiveServiceMock.updateHive.mockReturnValue(of({ ...hive, is_breeding_candidate: true }));
    hiveServiceMock.updateQueen.mockReturnValue(of({ ...queen, rasse: 'Carnica' }));
    hiveServiceMock.getHiveAnalytics.mockReturnValue(of({
      hive_id: 7,
      from_date: null,
      to_date: null,
      grouping: 'month',
      kpi: { total_harvest_kg: 0, total_feeding_kg_or_l: 0, inspection_count: 0, treatment_count: 0, event_count: 0 },
      chart: []
    }));
    hiveServiceMock.getWeightReadings.mockReturnValue(of([]));

    await TestBed.configureTestingModule({
      imports: [StockCardComponent],
      providers: [
        { provide: HiveService, useValue: hiveServiceMock },
        { provide: ActivatedRoute, useValue: activatedRouteMock }
      ]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(StockCardComponent);
    expect(fixture.componentInstance).toBeTruthy();
    expect(hiveServiceMock.getHiveAnalytics).toHaveBeenCalledWith(7, 'month', undefined, undefined);
    expect(hiveServiceMock.getWeightReadings).toHaveBeenCalledWith(7);
  });

  it('should open the breeding panel with the active queen data prefilled', () => {
    const fixture = TestBed.createComponent(StockCardComponent);
    const component = fixture.componentInstance as unknown as {
      openBreedingPanel: () => void;
      showBreedingPanel: () => boolean;
      breedingCandidate: () => boolean;
    };

    component.openBreedingPanel();

    expect(component.showBreedingPanel()).toBe(true);
    expect(component.breedingCandidate()).toBe(false);
  });

  it('should save breeding data for both hive and queen', () => {
    const fixture = TestBed.createComponent(StockCardComponent);
    const component = fixture.componentInstance as unknown as {
      openBreedingPanel: () => void;
      breedingCandidate: { set: (v: boolean) => void };
      rasse: { set: (v: string) => void };
      saveBreedingData: () => void;
    };

    component.openBreedingPanel();
    component.breedingCandidate.set(true);
    component.rasse.set('Carnica');
    component.saveBreedingData();

    expect(hiveServiceMock.updateHive).toHaveBeenCalledWith(7, { is_breeding_candidate: true });
    expect(hiveServiceMock.updateQueen).toHaveBeenCalledWith(3, expect.objectContaining({ rasse: 'Carnica' }));
  });

  it('should save the hive scale setting', () => {
    const fixture = TestBed.createComponent(StockCardComponent);
    const component = fixture.componentInstance as unknown as { toggleScale(value: boolean): void };

    component.toggleScale(true);

    expect(hiveServiceMock.updateHive).toHaveBeenCalledWith(7, { scale_enabled: true });
  });
});
