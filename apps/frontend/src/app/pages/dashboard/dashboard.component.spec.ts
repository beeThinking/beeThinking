import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiaryService } from '../../core/services/apiary.service';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { DashboardComponent } from './dashboard.component';

describe('DashboardComponent', () => {
  const summary = {
    apiary_count: 2,
    hive_count: 5,
    open_task_count: 3,
    overdue_task_count: 1,
    tasks_due_this_week: 2,
    treatment_count: 4,
    harvest_kg_total: 42.5,
    inventory_item_count: 7,
    latest_inspection_date: '2026-07-01',
    hives: [],
    apiaries: [],
    open_tasks: [],
    upcoming_appointments: [],
    low_inventory: []
  };

  const beekeepingServiceMock = {
    getDashboardSummary: vi.fn().mockReturnValue(of(summary))
  };

  const apiaryServiceMock = {
    getInvitations: vi.fn().mockReturnValue(of([])),
    acceptInvitation: vi.fn(),
    declineInvitation: vi.fn()
  };

  const routerMock = {
    navigate: vi.fn(),
    createUrlTree: vi.fn().mockReturnValue({}),
    serializeUrl: vi.fn().mockReturnValue('/'),
    events: of({})
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardComponent],
      providers: [
        { provide: BeekeepingService, useValue: beekeepingServiceMock },
        { provide: ApiaryService, useValue: apiaryServiceMock },
        { provide: Router, useValue: routerMock },
        { provide: ActivatedRoute, useValue: { snapshot: { queryParams: {} } } }
      ]
    }).compileComponents();

    vi.clearAllMocks();
    beekeepingServiceMock.getDashboardSummary.mockReturnValue(of(summary));
    apiaryServiceMock.getInvitations.mockReturnValue(of([]));
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(DashboardComponent);

    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should load summary and invitations on init', () => {
    TestBed.createComponent(DashboardComponent);

    expect(beekeepingServiceMock.getDashboardSummary).toHaveBeenCalledTimes(1);
    expect(apiaryServiceMock.getInvitations).toHaveBeenCalledTimes(1);
  });

  it('should render summary counts', () => {
    const fixture = TestBed.createComponent(DashboardComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('5');
    expect(element.textContent).toContain('42.5');
  });
});
