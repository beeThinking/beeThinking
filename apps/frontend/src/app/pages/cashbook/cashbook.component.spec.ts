import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiaryService } from '../../core/services/apiary.service';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { CashbookComponent } from './cashbook.component';

describe('CashbookComponent', () => {
  const entry = {
    id: 1,
    apiary_id: null,
    owner_id: 1,
    performed_by_user_id: 1,
    booking_date: '2026-06-11',
    direction: 'income',
    category: 'honey',
    title: 'Honigverkauf',
    invoice_number: null,
    partner_id: null,
    amount_gross: 119,
    tax_rate: 19,
    tax_amount: 19,
    amount_net: 100,
    counterparty: null,
    description: null,
    payment_method: null,
    receipt_id: null
  };

  const dashboard = {
    year: 2026,
    month: null,
    income: 100,
    expenses: 50,
    balance: 50,
    monthly: [],
    categories: []
  };

  const beekeepingServiceMock = {
    getCashbookEntries: vi.fn().mockReturnValue(of([entry])),
    getOfficeDashboard: vi.fn().mockReturnValue(of(dashboard)),
    getOfficePartners: vi.fn().mockReturnValue(of([])),
    getOfficeDocuments: vi.fn().mockReturnValue(of([]))
  };

  const apiaryServiceMock = {
    getApiaries: vi.fn().mockReturnValue(of([]))
  };

  const resetMocks = () => {
    beekeepingServiceMock.getCashbookEntries.mockReturnValue(of([entry]));
    beekeepingServiceMock.getOfficeDashboard.mockReturnValue(of(dashboard));
    beekeepingServiceMock.getOfficePartners.mockReturnValue(of([]));
    beekeepingServiceMock.getOfficeDocuments.mockReturnValue(of([]));
    apiaryServiceMock.getApiaries.mockReturnValue(of([]));
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CashbookComponent],
      providers: [
        { provide: BeekeepingService, useValue: beekeepingServiceMock },
        { provide: ApiaryService, useValue: apiaryServiceMock }
      ]
    }).compileComponents();

    vi.clearAllMocks();
    resetMocks();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(CashbookComponent);

    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should load entries, dashboard, partners and documents on init', () => {
    TestBed.createComponent(CashbookComponent);

    expect(beekeepingServiceMock.getCashbookEntries).toHaveBeenCalledTimes(1);
    expect(beekeepingServiceMock.getOfficeDashboard).toHaveBeenCalledTimes(1);
    expect(beekeepingServiceMock.getOfficePartners).toHaveBeenCalledTimes(1);
    expect(beekeepingServiceMock.getOfficeDocuments).toHaveBeenCalledTimes(1);
  });

  it('should reload when the year changes', () => {
    const fixture = TestBed.createComponent(CashbookComponent);
    const component = fixture.componentInstance as unknown as { setYear: (value: string) => void };

    component.setYear('2025');

    expect(beekeepingServiceMock.getCashbookEntries).toHaveBeenCalledTimes(2);
  });

  it('should render the dashboard balance', () => {
    const fixture = TestBed.createComponent(CashbookComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('Kontostand');
  });
});
