import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { BeekeepingService } from '../../core/services/beekeeping.service';
import { PosComponent } from './pos.component';

describe('PosComponent', () => {
  const item = {
    id: 1,
    owner_id: 1,
    article_id: 1,
    batch_id: null,
    article: { id: 1, owner_id: 1, category: 'honey', name: 'Honig 500g', sku: null, weight_kg: 0.5, unit: 'piece', notes: null, created_at: '', updated_at: null },
    quantity: 10,
    unit: 'piece',
    price: 5,
    best_before: null,
    batch_code: null,
    archived: false,
    notes: null,
    created_at: '',
    updated_at: null
  };

  const sale = {
    id: 1,
    owner_id: 1,
    partner_id: null,
    sale_date: '2026-07-24',
    vat_rate: 0.19,
    amount_gross: 10,
    amount_net: 8.4,
    notes: null,
    cashbook_entry_id: 1,
    created_at: '',
    updated_at: null,
    items: []
  };

  const beekeepingServiceMock = {
    getInventoryItems: vi.fn().mockReturnValue(of([item])),
    getOfficePartners: vi.fn().mockReturnValue(of([])),
    createSale: vi.fn().mockReturnValue(of(sale))
  };

  beforeEach(async () => {
    vi.clearAllMocks();
    beekeepingServiceMock.getInventoryItems.mockReturnValue(of([item]));
    beekeepingServiceMock.getOfficePartners.mockReturnValue(of([]));
    beekeepingServiceMock.createSale.mockReturnValue(of(sale));

    await TestBed.configureTestingModule({
      imports: [PosComponent],
      providers: [{ provide: BeekeepingService, useValue: beekeepingServiceMock }, provideRouter([])]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(PosComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should load available inventory items and customers on init', () => {
    TestBed.createComponent(PosComponent);
    expect(beekeepingServiceMock.getInventoryItems).toHaveBeenCalledTimes(1);
    expect(beekeepingServiceMock.getOfficePartners).toHaveBeenCalledWith('customer');
  });

  it('should add an item to the cart and compute the total', () => {
    const fixture = TestBed.createComponent(PosComponent);
    const component = fixture.componentInstance as unknown as {
      addToCart: (inventoryItem: typeof item) => void;
      cartTotal: () => number;
    };

    component.addToCart(item);
    component.addToCart(item);

    expect(component.cartTotal()).toBe(10);
  });

  it('should compute change due from cash given', () => {
    const fixture = TestBed.createComponent(PosComponent);
    const component = fixture.componentInstance as unknown as {
      addToCart: (inventoryItem: typeof item) => void;
      cashGiven: { set: (value: number | null) => void };
      changeDue: () => number | null;
    };

    component.addToCart(item);
    component.cashGiven.set(10);

    expect(component.changeDue()).toBe(5);
  });

  it('should submit the cart as a single sale', () => {
    const fixture = TestBed.createComponent(PosComponent);
    const component = fixture.componentInstance as unknown as {
      addToCart: (inventoryItem: typeof item) => void;
      submit: () => void;
    };

    component.addToCart(item);
    component.submit();

    expect(beekeepingServiceMock.createSale).toHaveBeenCalledWith(
      expect.objectContaining({
        items: [{ inventory_item_id: 1, quantity: 1, unit_price_gross: 5 }]
      })
    );
  });

  it('should not increase quantity past available stock', () => {
    const fixture = TestBed.createComponent(PosComponent);
    const component = fixture.componentInstance as unknown as {
      addToCart: (inventoryItem: typeof item) => void;
      increment: (id: number) => void;
      cart: () => { quantity: number }[];
    };

    component.addToCart({ ...item, quantity: 1 });
    for (let i = 0; i < 5; i++) component.increment(1);

    expect(component.cart()[0].quantity).toBe(1);
  });
});
