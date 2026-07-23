import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { HoneybookEntry } from '../../core/models/beekeeping.models';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HoneybookComponent } from './honeybook.component';

describe('HoneybookComponent', () => {
  const entries: HoneybookEntry[] = [
    {
      lot_number: '2026-001',
      status: 'batched',
      harvest_date: '2026-06-01',
      apiary_name: 'Stand Nord',
      hive_name: 'Volk 1',
      crop_type: 'Frühtracht',
      amount_kg: 10,
      water_content_percent: 17.5,
      best_before: '2028-06-01',
      bottled_quantity: 5,
      bottled_articles: ['Glas 500g']
    },
    {
      lot_number: null,
      status: 'unbatched',
      harvest_date: '2026-06-10',
      apiary_name: null,
      hive_name: null,
      crop_type: null,
      amount_kg: 3,
      water_content_percent: null,
      best_before: null,
      bottled_quantity: 0,
      bottled_articles: []
    }
  ];

  const beekeepingServiceMock = {
    getHoneybookRegister: vi.fn().mockReturnValue(of(entries)),
    downloadHoneybookPdf: vi.fn()
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HoneybookComponent],
      providers: [{ provide: BeekeepingService, useValue: beekeepingServiceMock }]
    }).compileComponents();

    vi.clearAllMocks();
    beekeepingServiceMock.getHoneybookRegister.mockReturnValue(of(entries));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(HoneybookComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should render loaded register entries', () => {
    const fixture = TestBed.createComponent(HoneybookComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('2026-001');
  });

  it('should show unbatched indicator for entries without a lot number', () => {
    const fixture = TestBed.createComponent(HoneybookComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.querySelector('.unbatched-badge')).toBeTruthy();
  });

  it('should reload the register when the year changes', () => {
    const fixture = TestBed.createComponent(HoneybookComponent);
    const component = fixture.componentInstance as unknown as { setYear: (value: string) => void };
    fixture.detectChanges();

    component.setYear('2025');

    expect(beekeepingServiceMock.getHoneybookRegister).toHaveBeenCalledWith(2025);
  });

  it('should trigger the pdf download for the selected year', () => {
    beekeepingServiceMock.downloadHoneybookPdf.mockReturnValue(of(new Blob(['pdf'])));
    const createObjectURLSpy = vi.fn().mockReturnValue('blob:mock');
    const revokeObjectURLSpy = vi.fn();
    vi.stubGlobal('URL', { createObjectURL: createObjectURLSpy, revokeObjectURL: revokeObjectURLSpy });

    const fixture = TestBed.createComponent(HoneybookComponent);
    const component = fixture.componentInstance as unknown as { downloadPdf: () => void };
    fixture.detectChanges();

    component.downloadPdf();

    expect(beekeepingServiceMock.downloadHoneybookPdf).toHaveBeenCalledWith(new Date().getFullYear());
    expect(createObjectURLSpy).toHaveBeenCalled();
  });
});
