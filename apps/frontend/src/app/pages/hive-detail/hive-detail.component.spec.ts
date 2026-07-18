import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router, convertToParamMap } from '@angular/router';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiaryService } from '../../core/services/apiary.service';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HiveService } from '../../core/services/hive.service';
import { HiveDetailComponent } from './hive-detail.component';

describe('HiveDetailComponent', () => {
  const hive = {
    id: 7,
    name: 'Volk 7',
    stock_number: '7',
    type: 'zander',
    colony_kind: 'ableger',
    status: 'active',
    is_active: true,
    archived_at: null,
    established_at: '2026-05-15',
    tags: ['sanft'],
    merged_into_hive_id: null,
    notes: 'Sanftmütiges Volk',
    owner_id: 1,
    apiary_id: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: null
  };

  const queen = {
    id: 3,
    owner_id: 1,
    hive_id: 7,
    name: null,
    year: 2026,
    origin: null,
    marking_color: 'grün',
    is_active: true,
    notes: null,
    created_at: '2026-05-15T00:00:00Z',
    updated_at: null
  };

  const hiveServiceMock = {
    getHive: vi.fn().mockReturnValue(of(hive)),
    getHiveTimeline: vi.fn().mockReturnValue(of([])),
    getHiveHistory: vi.fn().mockReturnValue(of([])),
    getQueens: vi.fn().mockReturnValue(of([queen])),
    getVarroaChecks: vi.fn().mockReturnValue(of([])),
    createVarroaCheck: vi.fn().mockReturnValue(of({})),
    moveHive: vi.fn().mockReturnValue(of(hive)),
    copyHive: vi.fn().mockReturnValue(of({ ...hive, id: 8 })),
    requeenHive: vi.fn().mockReturnValue(of(queen)),
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

  const apiaryServiceMock = {
    getApiaries: vi.fn().mockReturnValue(of([
      { id: 1, stock_number: 'S-1', name: 'Stand 1' },
      { id: 2, stock_number: 'S-2', name: 'Stand 2' }
    ]))
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
        { provide: ApiaryService, useValue: apiaryServiceMock },
        { provide: ActivatedRoute, useValue: activatedRouteMock },
        { provide: Router, useValue: routerMock }
      ]
    }).compileComponents();

    vi.clearAllMocks();
    hiveServiceMock.getHive.mockReturnValue(of(hive));
    hiveServiceMock.getHiveTimeline.mockReturnValue(of([]));
    hiveServiceMock.getHiveHistory.mockReturnValue(of([]));
    hiveServiceMock.getQueens.mockReturnValue(of([queen]));
    hiveServiceMock.moveHive.mockReturnValue(of(hive));
    hiveServiceMock.copyHive.mockReturnValue(of({ ...hive, id: 8 }));
    hiveServiceMock.requeenHive.mockReturnValue(of(queen));
    hiveServiceMock.createVarroaCheck.mockReturnValue(of({}));
    beekeepingServiceMock.getPhotos.mockReturnValue(of([]));
    apiaryServiceMock.getApiaries.mockReturnValue(of([
      { id: 1, stock_number: 'S-1', name: 'Stand 1' },
      { id: 2, stock_number: 'S-2', name: 'Stand 2' }
    ]));
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(HiveDetailComponent);

    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should load hive, timeline, history and queens for the route id', () => {
    TestBed.createComponent(HiveDetailComponent);

    expect(hiveServiceMock.getHive).toHaveBeenCalledWith(7);
    expect(hiveServiceMock.getHiveTimeline).toHaveBeenCalledWith(7);
    expect(hiveServiceMock.getHiveHistory).toHaveBeenCalledWith(7);
    expect(hiveServiceMock.getQueens).toHaveBeenCalledWith(7);
  });

  it('should render hive name, notes and active queen', () => {
    const fixture = TestBed.createComponent(HiveDetailComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('Volk 7');
    expect(element.textContent).toContain('Sanftmütiges Volk');
    expect(element.textContent).toContain('2026');
    expect(element.textContent).toContain('grün');
  });

  it('should not move without a target apiary', () => {
    const fixture = TestBed.createComponent(HiveDetailComponent);
    const component = fixture.componentInstance as unknown as { moveHive: () => void };

    component.moveHive();

    expect(hiveServiceMock.moveHive).not.toHaveBeenCalled();
  });

  it('should move to the selected apiary', () => {
    const fixture = TestBed.createComponent(HiveDetailComponent);
    const component = fixture.componentInstance as unknown as {
      moveHive: () => void;
      moveTargetApiaryId: { set: (value: number) => void };
    };

    component.moveTargetApiaryId.set(2);
    component.moveHive();

    expect(hiveServiceMock.moveHive).toHaveBeenCalledWith(7, expect.objectContaining({ target_apiary_id: 2 }));
  });

  it('should copy the hive and navigate to the copy', () => {
    const fixture = TestBed.createComponent(HiveDetailComponent);
    const component = fixture.componentInstance as unknown as { copyHive: () => void };

    component.copyHive();

    expect(hiveServiceMock.copyHive).toHaveBeenCalledWith(7, expect.anything());
    expect(routerMock.navigate).toHaveBeenCalledWith(['/hives', 8]);
  });

  it('should not save an empty varroa check', () => {
    const fixture = TestBed.createComponent(HiveDetailComponent);
    const component = fixture.componentInstance as unknown as { addVarroaCheck: () => void };

    component.addVarroaCheck();

    expect(hiveServiceMock.createVarroaCheck).not.toHaveBeenCalled();
  });
});
