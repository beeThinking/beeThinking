import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { ReportsComponent } from './reports.component';

describe('ReportsComponent', () => {
  const beekeepingServiceMock = {
    getReport: vi.fn().mockReturnValue(of([])),
    downloadInventoryMaterialPdf: vi.fn(),
    downloadInventoryFinishedGoodsPdf: vi.fn(),
    downloadFeedingsPdf: vi.fn()
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReportsComponent],
      providers: [{ provide: BeekeepingService, useValue: beekeepingServiceMock }]
    }).compileComponents();

    vi.clearAllMocks();
    beekeepingServiceMock.getReport.mockReturnValue(of([]));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(ReportsComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should trigger the inventory material pdf download', () => {
    beekeepingServiceMock.downloadInventoryMaterialPdf.mockReturnValue(of(new Blob(['pdf'])));
    const createObjectURLSpy = vi.fn().mockReturnValue('blob:mock');
    const revokeObjectURLSpy = vi.fn();
    vi.stubGlobal('URL', { createObjectURL: createObjectURLSpy, revokeObjectURL: revokeObjectURLSpy });

    const fixture = TestBed.createComponent(ReportsComponent);
    const component = fixture.componentInstance as unknown as { downloadInventoryMaterialPdf: () => void };
    fixture.detectChanges();

    component.downloadInventoryMaterialPdf();

    expect(beekeepingServiceMock.downloadInventoryMaterialPdf).toHaveBeenCalled();
    expect(createObjectURLSpy).toHaveBeenCalled();
  });

  it('should trigger the inventory finished goods pdf download', () => {
    beekeepingServiceMock.downloadInventoryFinishedGoodsPdf.mockReturnValue(of(new Blob(['pdf'])));
    const createObjectURLSpy = vi.fn().mockReturnValue('blob:mock');
    const revokeObjectURLSpy = vi.fn();
    vi.stubGlobal('URL', { createObjectURL: createObjectURLSpy, revokeObjectURL: revokeObjectURLSpy });

    const fixture = TestBed.createComponent(ReportsComponent);
    const component = fixture.componentInstance as unknown as { downloadInventoryFinishedGoodsPdf: () => void };
    fixture.detectChanges();

    component.downloadInventoryFinishedGoodsPdf();

    expect(beekeepingServiceMock.downloadInventoryFinishedGoodsPdf).toHaveBeenCalled();
    expect(createObjectURLSpy).toHaveBeenCalled();
  });

  it('should trigger the feedings pdf download with the selected date range', () => {
    beekeepingServiceMock.downloadFeedingsPdf.mockReturnValue(of(new Blob(['pdf'])));
    const createObjectURLSpy = vi.fn().mockReturnValue('blob:mock');
    const revokeObjectURLSpy = vi.fn();
    vi.stubGlobal('URL', { createObjectURL: createObjectURLSpy, revokeObjectURL: revokeObjectURLSpy });

    const fixture = TestBed.createComponent(ReportsComponent);
    const component = fixture.componentInstance as unknown as { downloadFeedingsPdf: () => void; fromDate: () => string; toDate: () => string };
    fixture.detectChanges();

    component.downloadFeedingsPdf();

    expect(beekeepingServiceMock.downloadFeedingsPdf).toHaveBeenCalledWith(component.fromDate(), component.toDate());
    expect(createObjectURLSpy).toHaveBeenCalled();
  });
});
