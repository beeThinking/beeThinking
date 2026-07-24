import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { BeekeepingService } from '../../core/services/beekeeping.service';
import { SalesReportComponent } from './sales-report.component';

describe('SalesReportComponent', () => {
  const rows = [
    { article_id: 1, article_name: 'Honig 500g', quantity: 4, amount_gross: 23.8, amount_net: 20 }
  ];

  const beekeepingServiceMock = {
    getSalesReport: vi.fn().mockReturnValue(of(rows))
  };

  beforeEach(async () => {
    vi.clearAllMocks();
    beekeepingServiceMock.getSalesReport.mockReturnValue(of(rows));

    await TestBed.configureTestingModule({
      imports: [SalesReportComponent],
      providers: [{ provide: BeekeepingService, useValue: beekeepingServiceMock }, provideRouter([])]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(SalesReportComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should load the report on init with the default date range', () => {
    TestBed.createComponent(SalesReportComponent);
    expect(beekeepingServiceMock.getSalesReport).toHaveBeenCalledTimes(1);
  });

  it('should compute totals from the rows', () => {
    const fixture = TestBed.createComponent(SalesReportComponent);
    const component = fixture.componentInstance as unknown as { totals: () => { quantity: number; amount_gross: number; amount_net: number } };

    expect(component.totals()).toEqual({ quantity: 4, amount_gross: 23.8, amount_net: 20 });
  });

  it('should render the article name', () => {
    const fixture = TestBed.createComponent(SalesReportComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('Honig 500g');
  });
});
