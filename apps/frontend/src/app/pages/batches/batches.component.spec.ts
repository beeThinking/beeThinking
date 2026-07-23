import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { Batch, Harvest } from '../../core/models/beekeeping.models';
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
      notes: null,
      created_at: '2026-06-10T10:00:00Z',
      updated_at: null,
      harvests: [
        { id: 11, harvest_date: '2026-06-10', apiary_id: null, hive_id: null, crop_type: 'Frühtracht', amount_kg: 3 }
      ]
    }
  ];

  const beekeepingServiceMock = {
    getBatches: vi.fn().mockReturnValue(of(batches)),
    getHarvests: vi.fn().mockReturnValue(of(harvests)),
    createBatch: vi.fn(),
    updateBatch: vi.fn(),
    deleteBatch: vi.fn(),
    attachHarvestToBatch: vi.fn(),
    detachHarvestFromBatch: vi.fn()
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BatchesComponent],
      providers: [{ provide: BeekeepingService, useValue: beekeepingServiceMock }]
    }).compileComponents();

    vi.clearAllMocks();
    beekeepingServiceMock.getBatches.mockReturnValue(of(batches));
    beekeepingServiceMock.getHarvests.mockReturnValue(of(harvests));
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
});
