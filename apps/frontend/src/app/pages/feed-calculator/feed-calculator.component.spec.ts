import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { CalculatorsService } from '../../core/services/calculators.service';
import { FeedCalculatorComponent } from './feed-calculator.component';

describe('FeedCalculatorComponent', () => {
  const response = { kg_sugar_per_colony: 12, total_kg_sugar: 24, formula_note: 'rule of thumb' };
  const calculatorsServiceMock = {
    calculateFeed: vi.fn().mockReturnValue(of(response))
  };

  beforeEach(async () => {
    vi.clearAllMocks();
    calculatorsServiceMock.calculateFeed.mockReturnValue(of(response));

    await TestBed.configureTestingModule({
      imports: [FeedCalculatorComponent],
      providers: [{ provide: CalculatorsService, useValue: calculatorsServiceMock }]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(FeedCalculatorComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should calculate feed quantity from the form values', () => {
    const fixture = TestBed.createComponent(FeedCalculatorComponent);
    const component = fixture.componentInstance as unknown as {
      form: { patchValue: (v: Record<string, unknown>) => void };
      calculate: () => void;
      result: () => { total_kg_sugar: number } | null;
    };
    component.form.patchValue({ colony_count: 2, colony_strength: 'strong', season: 'spring_buildup' });
    component.calculate();

    expect(calculatorsServiceMock.calculateFeed).toHaveBeenCalledWith({
      colony_count: 2,
      colony_strength: 'strong',
      season: 'spring_buildup'
    });
    expect(component.result()?.total_kg_sugar).toBe(24);
  });
});
