import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { Apiary } from '../../core/models/apiary.models';
import { ApiaryService } from '../../core/services/apiary.service';
import { ApiariesComponent } from './apiaries.component';

describe('ApiariesComponent', () => {
  const apiaries: Partial<Apiary>[] = [
    { id: 1, stock_number: 'S-001', name: 'Stand Nord', hive_count: 3 },
    { id: 2, stock_number: 'S-002', name: 'Stand Süd', hive_count: 1 }
  ];

  const apiaryServiceMock = {
    getApiaries: vi.fn().mockReturnValue(of(apiaries)),
    createApiary: vi.fn(),
    updateApiary: vi.fn(),
    deleteApiary: vi.fn()
  };

  const routerMock = {
    navigate: vi.fn(),
    createUrlTree: vi.fn().mockReturnValue({}),
    serializeUrl: vi.fn().mockReturnValue('/'),
    events: of({})
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ApiariesComponent],
      providers: [
        { provide: ApiaryService, useValue: apiaryServiceMock },
        { provide: Router, useValue: routerMock },
        { provide: ActivatedRoute, useValue: { snapshot: { queryParams: {} } } }
      ]
    }).compileComponents();

    vi.clearAllMocks();
    apiaryServiceMock.getApiaries.mockReturnValue(of(apiaries));
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(ApiariesComponent);

    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should load apiaries on init', () => {
    TestBed.createComponent(ApiariesComponent);

    expect(apiaryServiceMock.getApiaries).toHaveBeenCalledTimes(1);
  });

  it('should render apiary names', () => {
    const fixture = TestBed.createComponent(ApiariesComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('Stand Nord');
    expect(element.textContent).toContain('Stand Süd');
  });

  it('should open the create form', () => {
    const fixture = TestBed.createComponent(ApiariesComponent);
    const component = fixture.componentInstance as unknown as {
      openCreateForm: () => void;
      showForm: () => boolean;
    };

    component.openCreateForm();

    expect(component.showForm()).toBe(true);
  });
});
