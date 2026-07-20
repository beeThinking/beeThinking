import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiaryService } from '../../core/services/apiary.service';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HiveService } from '../../core/services/hive.service';
import { ScanComponent } from './scan.component';

describe('ScanComponent', () => {
  const hives = [
    { id: 1, name: 'Volk 1', apiary_id: 10 },
    { id: 2, name: 'Volk 2', apiary_id: 10 },
    { id: 3, name: 'Volk 3', apiary_id: 20 }
  ];

  const hiveServiceMock = {
    getHives: vi.fn().mockReturnValue(of(hives))
  };

  const apiaryServiceMock = {
    getApiaries: vi.fn().mockReturnValue(of([
      { id: 10, stock_number: 'S-10', name: 'Stand 10' },
      { id: 20, stock_number: 'S-20', name: 'Stand 20' }
    ]))
  };

  const beekeepingServiceMock = {
    createBatchAction: vi.fn().mockReturnValue(of({ action_type: 'feeding', created: 2, hive_ids: [1, 2] }))
  };

  const routerMock = {
    navigate: vi.fn(),
    createUrlTree: vi.fn().mockReturnValue({}),
    serializeUrl: vi.fn().mockReturnValue('/'),
    events: of({})
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ScanComponent],
      providers: [
        { provide: HiveService, useValue: hiveServiceMock },
        { provide: ApiaryService, useValue: apiaryServiceMock },
        { provide: BeekeepingService, useValue: beekeepingServiceMock },
        { provide: Router, useValue: routerMock },
        { provide: ActivatedRoute, useValue: { snapshot: { queryParams: {} } } }
      ]
    }).compileComponents();

    vi.clearAllMocks();
    hiveServiceMock.getHives.mockReturnValue(of(hives));
    beekeepingServiceMock.createBatchAction.mockReturnValue(of({ action_type: 'feeding', created: 2, hive_ids: [1, 2] }));
  });

  it('should create and show fallback hints without NFC/BarcodeDetector', () => {
    const fixture = TestBed.createComponent(ScanComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(fixture.componentInstance).toBeTruthy();
    expect(element.textContent).toContain('Web NFC');
  });

  it('should navigate to the stock card for a scanned URL in single mode', () => {
    const fixture = TestBed.createComponent(ScanComponent);
    const component = fixture.componentInstance as unknown as {
      handleScannedUrl: (url: string) => void;
    };

    component.handleScannedUrl('https://beethinking.example/stock-card/2');

    expect(routerMock.navigate).toHaveBeenCalledWith(['/stock-card', 2]);
  });

  it('should collect scanned hives in multi-scan mode', () => {
    const fixture = TestBed.createComponent(ScanComponent);
    const component = fixture.componentInstance as unknown as {
      handleScannedUrl: (url: string) => void;
      multiScan: { set: (value: boolean) => void };
      selectedHives: () => { id: number }[];
    };

    component.multiScan.set(true);
    component.handleScannedUrl('https://beethinking.example/stock-card/1');
    component.handleScannedUrl('https://beethinking.example/stock-card/1');
    component.handleScannedUrl('https://beethinking.example/stock-card/3');

    expect(component.selectedHives().map(hive => hive.id)).toEqual([1, 3]);
    expect(routerMock.navigate).not.toHaveBeenCalled();
  });

  it('should reject unknown codes', () => {
    const fixture = TestBed.createComponent(ScanComponent);
    const component = fixture.componentInstance as unknown as {
      handleScannedUrl: (url: string) => void;
      errorMessage: () => string;
    };

    component.handleScannedUrl('https://example.com/nothing');

    expect(component.errorMessage()).toBeTruthy();
    expect(routerMock.navigate).not.toHaveBeenCalled();
  });

  it('should run one batch call per apiary', () => {
    const fixture = TestBed.createComponent(ScanComponent);
    const component = fixture.componentInstance as unknown as {
      handleScannedUrl: (url: string) => void;
      multiScan: { set: (value: boolean) => void };
      batchAmount: { set: (value: number) => void };
      runBatchAction: () => void;
      selectedHives: () => unknown[];
    };

    component.multiScan.set(true);
    component.handleScannedUrl('https://beethinking.example/stock-card/1');
    component.handleScannedUrl('https://beethinking.example/stock-card/2');
    component.handleScannedUrl('https://beethinking.example/stock-card/3');
    component.batchAmount.set(2.5);
    component.runBatchAction();

    expect(beekeepingServiceMock.createBatchAction).toHaveBeenCalledTimes(2);
    expect(beekeepingServiceMock.createBatchAction).toHaveBeenCalledWith(10, 'feeding', expect.objectContaining({ hive_ids: [1, 2] }));
    expect(beekeepingServiceMock.createBatchAction).toHaveBeenCalledWith(20, 'feeding', expect.objectContaining({ hive_ids: [3] }));
    expect(component.selectedHives().length).toBe(0);
  });

  it('should require an amount for feeding batches', () => {
    const fixture = TestBed.createComponent(ScanComponent);
    const component = fixture.componentInstance as unknown as {
      handleScannedUrl: (url: string) => void;
      multiScan: { set: (value: boolean) => void };
      runBatchAction: () => void;
    };

    component.multiScan.set(true);
    component.handleScannedUrl('https://beethinking.example/stock-card/1');
    component.runBatchAction();

    expect(beekeepingServiceMock.createBatchAction).not.toHaveBeenCalled();
  });
});
