import { TestBed } from '@angular/core/testing';
import { HttpErrorResponse } from '@angular/common/http';
import { of, throwError } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { Article, Batch, Harvest, InventoryItem } from '../../core/models/beekeeping.models';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { BatchesComponent } from './batches.component';

describe('BatchesComponent', () => {
  const harvests: Harvest[] = [
    {
      id: 10,
      owner_id: 1,
      apiary_id: null,
      hive_id: null,
      harvest_date: '2026-06-01',
      crop_type: 'Frühtracht',
      amount_kg: 5,
      water_content_percent: null,
      batch_code: null,
      batch_id: null,
      notes: null,
      created_at: '2026-06-01T10:00:00Z',
      updated_at: null
    },
    {
      id: 11,
      owner_id: 1,
      apiary_id: null,
      hive_id: null,
      harvest_date: '2026-06-10',
      crop_type: 'Frühtracht',
      amount_kg: 3,
      water_content_percent: null,
      batch_code: null,
      batch_id: 1,
      notes: null,
      created_at: '2026-06-10T10:00:00Z',
      updated_at: null
    }
  ];

  const batches: Batch[] = [
    {
      id: 1,
      owner_id: 1,
      lot_number: '2026-001',
      best_before: '2028-06-10',
      total_amount_kg: 3,
      remaining_kg: 3,
      notes: null,
      created_at: '2026-06-10T10:00:00Z',
      updated_at: null,
      harvests: [
        { id: 11, harvest_date: '2026-06-10', apiary_id: null, hive_id: null, crop_type: 'Frühtracht', amount_kg: 3 }
      ]
    }
  ];

  const articles: Article[] = [
    {
      id: 5,
      owner_id: 1,
      category: 'finished_product',
      name: 'Honigglas 500g',
      sku: null,
      weight_kg: 0.5,
      unit: 'piece',
      notes: null,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: null
    }
  ];

  const beekeepingServiceMock = {
    getBatches: vi.fn().mockReturnValue(of(batches)),
    getHarvests: vi.fn().mockReturnValue(of(harvests)),
    getArticles: vi.fn().mockReturnValue(of(articles)),
    createBatch: vi.fn(),
    updateBatch: vi.fn(),
    deleteBatch: vi.fn(),
    attachHarvestToBatch: vi.fn(),
    detachHarvestFromBatch: vi.fn(),
    bottleBatch: vi.fn()
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BatchesComponent],
      providers: [{ provide: BeekeepingService, useValue: beekeepingServiceMock }]
    }).compileComponents();

    vi.clearAllMocks();
    beekeepingServiceMock.getBatches.mockReturnValue(of(batches));
    beekeepingServiceMock.getHarvests.mockReturnValue(of(harvests));
    beekeepingServiceMock.getArticles.mockReturnValue(of(articles));
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(BatchesComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should render loaded batches', () => {
    const fixture = TestBed.createComponent(BatchesComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('2026-001');
  });

  it('should only offer unbatched harvests for selection', () => {
    const fixture = TestBed.createComponent(BatchesComponent);
    const component = fixture.componentInstance as unknown as { unbatchedHarvests: () => Harvest[] };

    expect(component.unbatchedHarvests()).toEqual([harvests[0]]);
  });

  it('should suggest a best-before date 24 months after the earliest selected harvest', () => {
    const fixture = TestBed.createComponent(BatchesComponent);
    const component = fixture.componentInstance as unknown as {
      toggleHarvestSelection: (id: number, checked: boolean) => void;
      suggestedBestBefore: () => string;
    };

    component.toggleHarvestSelection(10, true);

    expect(component.suggestedBestBefore()).toBe('2028-06-01');
  });

  it('should create a batch with the selected harvest ids', () => {
    beekeepingServiceMock.createBatch.mockReturnValue(of({ ...batches[0], id: 2, lot_number: '2026-002' }));
    const fixture = TestBed.createComponent(BatchesComponent);
    const component = fixture.componentInstance as unknown as {
      toggleHarvestSelection: (id: number, checked: boolean) => void;
      createBatch: () => void;
    };

    component.toggleHarvestSelection(10, true);
    component.createBatch();

    expect(beekeepingServiceMock.createBatch).toHaveBeenCalledWith(
      expect.objectContaining({ harvest_ids: [10] })
    );
  });

  it('should delete a batch after confirmation', () => {
    vi.stubGlobal('confirm', vi.fn().mockReturnValue(true));
    beekeepingServiceMock.deleteBatch.mockReturnValue(of(void 0));
    const fixture = TestBed.createComponent(BatchesComponent);
    const component = fixture.componentInstance as unknown as { deleteBatch: (batch: Batch) => void };

    component.deleteBatch(batches[0]);

    expect(beekeepingServiceMock.deleteBatch).toHaveBeenCalledWith(1);
  });

  it('should add and remove bottling rows', () => {
    const fixture = TestBed.createComponent(BatchesComponent);
    const component = fixture.componentInstance as unknown as {
      addBottlingRow: () => void;
      removeBottlingRow: (id: number) => void;
      bottlingRows: () => { id: number; articleId: number | null }[];
    };

    component.addBottlingRow();
    expect(component.bottlingRows().length).toBe(1);
    expect(component.bottlingRows()[0].articleId).toBe(5);

    const rowId = component.bottlingRows()[0].id;
    component.removeBottlingRow(rowId);
    expect(component.bottlingRows().length).toBe(0);
  });

  it('should submit bottling and update batch remaining_kg with returned inventory items', () => {
    const updatedBatch: Batch = { ...batches[0], remaining_kg: 1 };
    const inventoryItems: InventoryItem[] = [
      {
        id: 20,
        owner_id: 1,
        article_id: 5,
        batch_id: 1,
        article: articles[0],
        quantity: 4,
        unit: 'piece',
        price: 9.9,
        best_before: '2028-01-01',
        batch_code: null,
        archived: false,
        notes: null,
        created_at: '2026-06-11T10:00:00Z',
        updated_at: null
      }
    ];
    beekeepingServiceMock.bottleBatch.mockReturnValue(of({ batch: updatedBatch, inventory_items: inventoryItems }));
    const fixture = TestBed.createComponent(BatchesComponent);
    const component = fixture.componentInstance as unknown as {
      addBottlingRow: () => void;
      updateBottlingRow: (id: number, changes: Record<string, unknown>) => void;
      submitBottling: (batch: Batch) => void;
      bottlingRows: () => { id: number }[];
      bottlingResult: () => InventoryItem[] | null;
      batches: () => Batch[];
    };

    component.addBottlingRow();
    const rowId = component.bottlingRows()[0].id;
    component.updateBottlingRow(rowId, { quantity: 4, price: 9.9, bestBefore: '2028-01-01' });
    component.submitBottling(batches[0]);

    expect(beekeepingServiceMock.bottleBatch).toHaveBeenCalledWith(1, {
      items: [{ article_id: 5, quantity: 4, price: 9.9, best_before: '2028-01-01' }]
    });
    expect(component.bottlingResult()).toEqual(inventoryItems);
    expect(component.batches().find(b => b.id === 1)?.remaining_kg).toBe(1);
  });

  it('should show a conflict message when bottling exceeds remaining_kg', () => {
    beekeepingServiceMock.bottleBatch.mockReturnValue(throwError(() => new HttpErrorResponse({ status: 409 })));
    const fixture = TestBed.createComponent(BatchesComponent);
    const component = fixture.componentInstance as unknown as {
      addBottlingRow: () => void;
      updateBottlingRow: (id: number, changes: Record<string, unknown>) => void;
      submitBottling: (batch: Batch) => void;
      bottlingRows: () => { id: number }[];
      bottlingError: () => string;
    };

    component.addBottlingRow();
    const rowId = component.bottlingRows()[0].id;
    component.updateBottlingRow(rowId, { quantity: 100 });
    component.submitBottling(batches[0]);

    expect(component.bottlingError()).toContain('übersteigt die verbleibende');
  });
});
