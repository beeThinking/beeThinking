import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router, convertToParamMap } from '@angular/router';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { InspectionCriterion } from '../../core/models/inspection.models';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { InspectionDraftService } from '../../core/services/inspection-draft.service';
import { InspectionService } from '../../core/services/inspection.service';
import { HiveInspectComponent } from './hive-inspect.component';

describe('HiveInspectComponent', () => {
  const criteria: Partial<InspectionCriterion>[] = [
    { id: 1, name: 'Sanftmut', section: 'verhalten', value_type: 'stars', options: null, sort_order: 10, is_active: true },
    { id: 2, name: 'Abgeschwärmt', section: 'allg_befund', value_type: 'bool', options: null, sort_order: 20, is_active: true },
    { id: 3, name: 'Futterart', section: 'verschiedenes', value_type: 'select', options: ['Honig', 'Sirup'], sort_order: 30, is_active: true },
    { id: 4, name: 'Inaktiv', section: 'klima', value_type: 'text', options: null, sort_order: 40, is_active: false }
  ];

  const inspectionServiceMock = {
    getCriteria: vi.fn().mockReturnValue(of(criteria)),
    createCriterion: vi.fn(),
    updateCriterion: vi.fn(),
    deleteCriterion: vi.fn(),
    createInspection: vi.fn().mockReturnValue(of({ id: 42 }))
  };

  const beekeepingServiceMock = {
    createTask: vi.fn().mockReturnValue(of({ id: 1 })),
    uploadPhoto: vi.fn().mockReturnValue(of({ id: 1 }))
  };

  const draftServiceMock = {
    getDraft: vi.fn().mockReturnValue(null),
    saveDraft: vi.fn().mockReturnValue({ updated_at: '2026-07-18T10:00:00Z' }),
    clearDraft: vi.fn()
  };

  const paramMap = convertToParamMap({ id: '7' });

  const routerMock = {
    navigate: vi.fn(),
    createUrlTree: vi.fn().mockReturnValue({}),
    serializeUrl: vi.fn().mockReturnValue('/'),
    events: of({})
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HiveInspectComponent],
      providers: [
        { provide: InspectionService, useValue: inspectionServiceMock },
        { provide: BeekeepingService, useValue: beekeepingServiceMock },
        { provide: InspectionDraftService, useValue: draftServiceMock },
        { provide: ActivatedRoute, useValue: { paramMap: of(paramMap), snapshot: { paramMap, queryParams: {} } } },
        { provide: Router, useValue: routerMock }
      ]
    }).compileComponents();

    vi.clearAllMocks();
    inspectionServiceMock.getCriteria.mockReturnValue(of(criteria));
    inspectionServiceMock.createInspection.mockReturnValue(of({ id: 42 }));
    beekeepingServiceMock.createTask.mockReturnValue(of({ id: 1 }));
    draftServiceMock.getDraft.mockReturnValue(null);
    draftServiceMock.saveDraft.mockReturnValue({ updated_at: '2026-07-18T10:00:00Z' });
  });

  it('should create and load criteria', () => {
    const fixture = TestBed.createComponent(HiveInspectComponent);

    expect(fixture.componentInstance).toBeTruthy();
    expect(inspectionServiceMock.getCriteria).toHaveBeenCalledTimes(1);
  });

  it('should render active criteria grouped by section, hiding inactive ones', () => {
    const fixture = TestBed.createComponent(HiveInspectComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('Sanftmut');
    expect(element.textContent).toContain('Abgeschwärmt');
    expect(element.textContent).toContain('Futterart');
    expect(element.textContent).not.toContain('Inaktiv');
  });

  it('should include criteria values and hive weight in the payload', () => {
    const fixture = TestBed.createComponent(HiveInspectComponent);
    const component = fixture.componentInstance as unknown as {
      save: () => void;
      setCriterionValue: (id: number, value: unknown) => void;
      form: { patchValue: (value: Record<string, unknown>) => void };
    };

    component.setCriterionValue(1, 5);
    component.form.patchValue({ hive_weight_kg: 38.2 });
    component.save();

    expect(inspectionServiceMock.createInspection).toHaveBeenCalledTimes(1);
    const payload = inspectionServiceMock.createInspection.mock.calls[0][1];
    expect(payload.criteria_values).toEqual({ '1': 5 });
    expect(payload.hive_weight_kg).toBe(38.2);
  });

  it('should create a follow-up task when the toggle is set', () => {
    const fixture = TestBed.createComponent(HiveInspectComponent);
    const component = fixture.componentInstance as unknown as {
      save: () => void;
      createTodo: { set: (value: boolean) => void };
      todoTitle: { set: (value: string) => void };
    };

    component.createTodo.set(true);
    component.todoTitle.set('Futter kontrollieren');
    component.save();

    expect(beekeepingServiceMock.createTask).toHaveBeenCalledWith(
      expect.objectContaining({ hive_id: 7, title: 'Futter kontrollieren' })
    );
  });

  it('should not create a task without the toggle', () => {
    const fixture = TestBed.createComponent(HiveInspectComponent);
    const component = fixture.componentInstance as unknown as { save: () => void };

    component.save();

    expect(beekeepingServiceMock.createTask).not.toHaveBeenCalled();
  });

  it('should toggle a star value off when clicked twice', () => {
    const fixture = TestBed.createComponent(HiveInspectComponent);
    const component = fixture.componentInstance as unknown as {
      toggleStar: (criterion: { id: number }, value: number) => void;
      criterionValue: (id: number) => unknown;
    };

    component.toggleStar({ id: 1 }, 4);
    expect(component.criterionValue(1)).toBe(4);

    component.toggleStar({ id: 1 }, 4);
    expect(component.criterionValue(1)).toBeUndefined();
  });
});
