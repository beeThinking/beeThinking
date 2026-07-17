import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router, convertToParamMap } from '@angular/router';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HiveService } from '../../core/services/hive.service';
import { HiveDetailComponent } from './hive-detail.component';

describe('HiveDetailComponent', () => {
  const hive = {
    id: 7,
    name: 'Volk 7',
    type: 'economy',
    status: 'active',
    is_active: true,
    archived_at: null,
    merged_into_hive_id: null,
    notes: 'Sanftmütiges Volk',
    owner_id: 1,
    apiary_id: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: null
  };

  const hiveServiceMock = {
    getHive: vi.fn().mockReturnValue(of(hive)),
    getHiveTimeline: vi.fn().mockReturnValue(of([])),
    getHiveHistory: vi.fn().mockReturnValue(of([])),
    archiveHive: vi.fn(),
    dissolveHive: vi.fn(),
    mergeHive: vi.fn()
  };

  const beekeepingServiceMock = {
    getPhotos: vi.fn().mockReturnValue(of([])),
    getPhotoPreview: vi.fn().mockReturnValue(of({ url: '' })),
    uploadPhoto: vi.fn(),
    deletePhoto: vi.fn()
  };

  const paramMap = convertToParamMap({ id: '7' });

  const activatedRouteMock = {
    paramMap: of(paramMap),
    snapshot: { paramMap, queryParams: {} }
  };

  const routerMock = {
    navigate: vi.fn(),
    createUrlTree: vi.fn().mockReturnValue({}),
    serializeUrl: vi.fn().mockReturnValue('/'),
    events: of({})
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HiveDetailComponent],
      providers: [
        { provide: HiveService, useValue: hiveServiceMock },
        { provide: BeekeepingService, useValue: beekeepingServiceMock },
        { provide: ActivatedRoute, useValue: activatedRouteMock },
        { provide: Router, useValue: routerMock }
      ]
    }).compileComponents();

    vi.clearAllMocks();
    hiveServiceMock.getHive.mockReturnValue(of(hive));
    hiveServiceMock.getHiveTimeline.mockReturnValue(of([]));
    hiveServiceMock.getHiveHistory.mockReturnValue(of([]));
    beekeepingServiceMock.getPhotos.mockReturnValue(of([]));
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(HiveDetailComponent);

    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should load hive, timeline and history for the route id', () => {
    TestBed.createComponent(HiveDetailComponent);

    expect(hiveServiceMock.getHive).toHaveBeenCalledWith(7);
    expect(hiveServiceMock.getHiveTimeline).toHaveBeenCalledWith(7);
    expect(hiveServiceMock.getHiveHistory).toHaveBeenCalledWith(7);
  });

  it('should render hive name and notes', () => {
    const fixture = TestBed.createComponent(HiveDetailComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('Volk 7');
    expect(element.textContent).toContain('Sanftmütiges Volk');
  });
});
