import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { BeekeepingService } from '../../core/services/beekeeping.service';
import { InspectionService } from '../../core/services/inspection.service';
import { ZuchtSelektionComponent } from './zucht-selektion.component';

describe('ZuchtSelektionComponent', () => {
  const candidateLow = { hive_id: 2, hive_name: 'Volk 2', score: 3.5, latest_inspection_id: 10, latest_inspection_date: '2026-06-01' };
  const candidateHigh = { hive_id: 1, hive_name: 'Volk 1', score: 8.2, latest_inspection_id: 11, latest_inspection_date: '2026-06-15' };

  const criterion = { id: 1, owner_id: 1, name: 'Sanftmut', section: 'verhalten' as const, value_type: 'select' as const, options: ['ruhig', 'aggressiv'], option_scores: { ruhig: 2 }, field_key: null, sort_order: 0, is_active: true, created_at: '', updated_at: null };
  const weight = { id: 1, user_id: 1, criterion_id: 1, weight: 2, created_at: '', updated_at: null };

  const beekeepingServiceMock = {
    getBreedingCandidates: vi.fn().mockReturnValue(of([candidateLow, candidateHigh])),
    getCriterionWeights: vi.fn().mockReturnValue(of([weight])),
    upsertCriterionWeight: vi.fn().mockReturnValue(of(weight))
  };
  const inspectionServiceMock = {
    getCriteria: vi.fn().mockReturnValue(of([criterion])),
    updateCriterion: vi.fn().mockReturnValue(of(criterion))
  };

  beforeEach(async () => {
    vi.clearAllMocks();
    beekeepingServiceMock.getBreedingCandidates.mockReturnValue(of([candidateLow, candidateHigh]));
    beekeepingServiceMock.getCriterionWeights.mockReturnValue(of([weight]));
    beekeepingServiceMock.upsertCriterionWeight.mockReturnValue(of(weight));
    inspectionServiceMock.getCriteria.mockReturnValue(of([criterion]));
    inspectionServiceMock.updateCriterion.mockReturnValue(of(criterion));

    await TestBed.configureTestingModule({
      imports: [ZuchtSelektionComponent],
      providers: [
        { provide: BeekeepingService, useValue: beekeepingServiceMock },
        { provide: InspectionService, useValue: inspectionServiceMock }
      ]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(ZuchtSelektionComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should sort candidates by descending score', () => {
    const fixture = TestBed.createComponent(ZuchtSelektionComponent);
    const component = fixture.componentInstance as unknown as { candidates: () => { hive_id: number }[] };

    expect(component.candidates().map(c => c.hive_id)).toEqual([1, 2]);
  });

  it('should save a criterion weight', () => {
    const fixture = TestBed.createComponent(ZuchtSelektionComponent);
    const component = fixture.componentInstance as unknown as { setWeight: (c: typeof criterion, v: number) => void };

    component.setWeight(criterion, 3);

    expect(beekeepingServiceMock.upsertCriterionWeight).toHaveBeenCalledWith({ criterion_id: 1, weight: 3 });
  });

  it('should save an option score for select criteria', () => {
    const fixture = TestBed.createComponent(ZuchtSelektionComponent);
    const component = fixture.componentInstance as unknown as { setOptionScore: (c: typeof criterion, option: string, v: number) => void };

    component.setOptionScore(criterion, 'aggressiv', -1);

    expect(inspectionServiceMock.updateCriterion).toHaveBeenCalledWith(1, { option_scores: { ruhig: 2, aggressiv: -1 } });
  });
});
