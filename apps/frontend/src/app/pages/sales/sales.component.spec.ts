import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { BeekeepingService } from '../../core/services/beekeeping.service';
import { SalesComponent } from './sales.component';

describe('SalesComponent', () => {
  const sale = {
    id: 1,
    owner_id: 1,
    partner_id: null,
    sale_date: '2026-07-24',
    vat_rate: 0.19,
    amount_gross: 11.9,
    amount_net: 10,
    notes: null,
    cashbook_entry_id: 5,
    created_at: '2026-07-24T10:00:00Z',
    updated_at: null,
    items: [{ id: 1, inventory_item_id: 1, quantity: 2, unit_price_gross: 5.95, line_total_gross: 11.9 }]
  };

  const item = {
    id: 1,
    owner_id: 1,
    article_id: 1,
    batch_id: null,
    article: { id: 1, owner_id: 1, category: 'honey', name: 'Honig 500g', sku: null, weight_kg: 0.5, unit: 'piece', notes: null, created_at: '', updated_at: null },
    quantity: 10,
    unit: 'piece',
    price: 5.95,
    best_before: null,
    batch_code: null,
    archived: false,
    notes: null,
    created_at: '',
    updated_at: null
  };

  const beekeepingServiceMock = {
    getSales: vi.fn().mockReturnValue(of([sale])),
    getInventoryItems: vi.fn().mockReturnValue(of([item])),
    getOfficePartners: vi.fn().mockReturnValue(of([])),
    createSale: vi.fn().mockReturnValue(of(sale)),
    deleteSale: vi.fn().mockReturnValue(of(undefined)),
    downloadCustomerListPdf: vi.fn().mockReturnValue(of(new Blob()))
  };

  beforeEach(async () => {
    vi.clearAllMocks();
    beekeepingServiceMock.getSales.mockReturnValue(of([sale]));
    beekeepingServiceMock.getInventoryItems.mockReturnValue(of([item]));
    beekeepingServiceMock.getOfficePartners.mockReturnValue(of([]));
    beekeepingServiceMock.createSale.mockReturnValue(of(sale));
    beekeepingServiceMock.deleteSale.mockReturnValue(of(undefined));
    beekeepingServiceMock.downloadCustomerListPdf.mockReturnValue(of(new Blob()));

    await TestBed.configureTestingModule({
      imports: [SalesComponent],
      providers: [{ provide: BeekeepingService, useValue: beekeepingServiceMock }, provideRouter([])]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(SalesComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should load sales, inventory items and customers on init', () => {
    TestBed.createComponent(SalesComponent);
    expect(beekeepingServiceMock.getSales).toHaveBeenCalledTimes(1);
    expect(beekeepingServiceMock.getInventoryItems).toHaveBeenCalledTimes(1);
    expect(beekeepingServiceMock.getOfficePartners).toHaveBeenCalledWith('customer');
  });

  it('should submit a sale with the drafted line items', () => {
    const fixture = TestBed.createComponent(SalesComponent);
    const component = fixture.componentInstance as unknown as {
      updateLine: (index: number, patch: Partial<{ inventory_item_id: number | null; quantity: number; unit_price_gross: number }>) => void;
      submit: () => void;
    };

    component.updateLine(0, { inventory_item_id: 1, quantity: 2, unit_price_gross: 5.95 });
    component.submit();

    expect(beekeepingServiceMock.createSale).toHaveBeenCalledWith(
      expect.objectContaining({
        items: [{ inventory_item_id: 1, quantity: 2, unit_price_gross: 5.95 }]
      })
    );
  });

  it('should convert the percentage VAT override to a fraction when submitting', () => {
    const fixture = TestBed.createComponent(SalesComponent);
    const component = fixture.componentInstance as unknown as {
      updateLine: (index: number, patch: Partial<{ inventory_item_id: number | null; quantity: number; unit_price_gross: number }>) => void;
      vatRateOverride: { set: (value: number | null) => void };
      submit: () => void;
    };

    component.updateLine(0, { inventory_item_id: 1, quantity: 2, unit_price_gross: 5.95 });
    component.vatRateOverride.set(19);
    component.submit();

    expect(beekeepingServiceMock.createSale).toHaveBeenCalledWith(
      expect.objectContaining({ vat_rate: 0.19 })
    );
  });

  it('should void a sale after confirmation', () => {
    vi.stubGlobal('confirm', vi.fn().mockReturnValue(true));
    const fixture = TestBed.createComponent(SalesComponent);
    const component = fixture.componentInstance as unknown as { voidSale: (saleRecord: typeof sale) => void };

    component.voidSale(sale);

    expect(beekeepingServiceMock.deleteSale).toHaveBeenCalledWith(sale.id);
    vi.unstubAllGlobals();
  });

  it('should download the customer list pdf', () => {
    const fixture = TestBed.createComponent(SalesComponent);
    const component = fixture.componentInstance as unknown as { downloadCustomerListPdf: () => void };

    component.downloadCustomerListPdf();

    expect(beekeepingServiceMock.downloadCustomerListPdf).toHaveBeenCalledTimes(1);
  });
});
