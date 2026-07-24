import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { HiveSelectionService } from '../../core/services/hive-selection.service';
import { InspectionService } from '../../core/services/inspection.service';
import { HiveSelectionComponent } from './hive-selection.component';

describe('HiveSelectionComponent', () => {
  const criterion = { id: 1, owner_id: 1, name: 'Sanftmut', section: 'verhalten' as const, value_type: 'stars' as const, options: null, option_scores: null, field_key: null, sort_order: 0, is_active: true, created_at: '', updated_at: null };
  const textCriterion = { ...criterion, id: 2, name: 'Notizen', value_type: 'text' as const };
  const candidate = { hive_id: 1, hive_name: 'Volk 1', apiary_id: 1, tags: ['sanft'], criterion_averages: { 1: 4.2 }, inspection_count: 3 };

  const hiveSelectionServiceMock = {
    filterHives: vi.fn().mockReturnValue(of([candidate])),
    batchCreateTasks: vi.fn().mockReturnValue(of({ created_task_ids: [1] }))
  };
  const inspectionServiceMock = {
    getCriteria: vi.fn().mockReturnValue(of([criterion, textCriterion]))
  };

  beforeEach(async () => {
    vi.clearAllMocks();
    hiveSelectionServiceMock.filterHives.mockReturnValue(of([candidate]));
    hiveSelectionServiceMock.batchCreateTasks.mockReturnValue(of({ created_task_ids: [1] }));
    inspectionServiceMock.getCriteria.mockReturnValue(of([criterion, textCriterion]));

    await TestBed.configureTestingModule({
      imports: [HiveSelectionComponent],
      providers: [
        { provide: HiveSelectionService, useValue: hiveSelectionServiceMock },
        { provide: InspectionService, useValue: inspectionServiceMock }
      ]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(HiveSelectionComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should only offer stars/number criteria for averaging', () => {
    const fixture = TestBed.createComponent(HiveSelectionComponent);
    const component = fixture.componentInstance as unknown as { averagedCriteria: () => { id: number }[] };
    expect(component.averagedCriteria().map(c => c.id)).toEqual([1]);
  });

  it('should search hives with the configured filters', () => {
    const fixture = TestBed.createComponent(HiveSelectionComponent);
    const component = fixture.componentInstance as unknown as {
      setMin: (id: number, value: string) => void;
      search: () => void;
      candidates: () => { hive_id: number }[];
    };
    component.setMin(1, '3');
    component.search();
    expect(hiveSelectionServiceMock.filterHives).toHaveBeenCalledWith(expect.objectContaining({
      criteria: [{ criterion_id: 1, min_average: 3, max_average: null }]
    }));
    expect(component.candidates().map(c => c.hive_id)).toEqual([1]);
  });

  it('should batch-create tasks for the selected hives', () => {
    const fixture = TestBed.createComponent(HiveSelectionComponent);
    const component = fixture.componentInstance as unknown as {
      search: () => void;
      toggleSelection: (id: number) => void;
      batchTitle: { set: (v: string) => void };
      createBatchTasks: () => void;
    };
    component.search();
    component.toggleSelection(1);
    component.batchTitle.set('Varroa behandeln');
    component.createBatchTasks();
    expect(hiveSelectionServiceMock.batchCreateTasks).toHaveBeenCalledWith(expect.objectContaining({
      hive_ids: [1],
      title: 'Varroa behandeln'
    }));
  });
});
