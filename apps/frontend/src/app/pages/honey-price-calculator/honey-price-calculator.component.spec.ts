import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { CalculatorsService } from '../../core/services/calculators.service';
import { ApiaryService } from '../../core/services/apiary.service';
import { HoneyPriceCalculatorComponent } from './honey-price-calculator.component';

describe('HoneyPriceCalculatorComponent', () => {
  const apiary = { id: 1, stock_number: 'ST-1', name: 'Garten', address: null, latitude: null, longitude: null, notes: null, owner_id: 1, hive_count: 3, created_at: '', updated_at: null };
  const response = {
    apiary_id: 1,
    total_relevant_costs: 100,
    total_harvested_kg: 20,
    colony_count: 4,
    cost_per_kg: 5,
    cost_per_colony: 25,
    suggested_price_per_kg: 6,
    simplification_note: 'simplified'
  };
  const calculatorsServiceMock = { calculateHoneyPrice: vi.fn().mockReturnValue(of(response)) };
  const apiaryServiceMock = { getApiaries: vi.fn().mockReturnValue(of([apiary])) };

  beforeEach(async () => {
    vi.clearAllMocks();
    calculatorsServiceMock.calculateHoneyPrice.mockReturnValue(of(response));
    apiaryServiceMock.getApiaries.mockReturnValue(of([apiary]));

    await TestBed.configureTestingModule({
      imports: [HoneyPriceCalculatorComponent],
      providers: [
        { provide: CalculatorsService, useValue: calculatorsServiceMock },
        { provide: ApiaryService, useValue: apiaryServiceMock }
      ]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(HoneyPriceCalculatorComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should calculate honey price for the selected apiary', () => {
    const fixture = TestBed.createComponent(HoneyPriceCalculatorComponent);
    const component = fixture.componentInstance as unknown as {
      form: { patchValue: (v: Record<string, unknown>) => void };
      calculate: () => void;
      result: () => { cost_per_kg: number | null } | null;
    };
    component.form.patchValue({ apiary_id: 1, target_margin_percent: 20 });
    component.calculate();

    expect(calculatorsServiceMock.calculateHoneyPrice).toHaveBeenCalledWith(expect.objectContaining({
      apiary_id: 1,
      target_margin_percent: 20
    }));
    expect(component.result()?.cost_per_kg).toBe(5);
  });
});
