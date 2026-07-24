import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HiveService } from '../../core/services/hive.service';
import { ApiaryService } from '../../core/services/apiary.service';
import { AuthService } from '../../core/services/auth.service';
import { TasksComponent } from './tasks.component';

describe('TasksComponent', () => {
  const task = {
    id: 1,
    owner_id: 1,
    hive_id: null,
    apiary_id: null,
    assignee_id: 2,
    title: 'Futter prüfen',
    description: null,
    due_date: '2026-07-24',
    start_at: null,
    end_at: null,
    kind: 'todo' as const,
    priority: 'medium' as const,
    status: 'open' as const,
    source: 'manual' as const,
    recurrence_rule: null,
    delegated_at: '2026-07-20T00:00:00Z',
    delegation_seen_at: null,
    created_at: '2026-07-01T00:00:00Z',
    updated_at: null,
    completed_at: null
  };

  const beekeepingServiceMock = {
    getTasks: vi.fn().mockReturnValue(of([task])),
    createTask: vi.fn().mockReturnValue(of(task)),
    completeTask: vi.fn().mockReturnValue(of({ ...task, status: 'done' })),
    updateTask: vi.fn().mockReturnValue(of(task)),
    deleteTask: vi.fn().mockReturnValue(of(undefined)),
    acknowledgeTaskDelegation: vi.fn().mockReturnValue(of({ ...task, delegation_seen_at: '2026-07-24T00:00:00Z' }))
  };
  const hiveServiceMock = { getHives: vi.fn().mockReturnValue(of([])) };
  const apiaryServiceMock = {
    getApiaries: vi.fn().mockReturnValue(of([])),
    getMembers: vi.fn().mockReturnValue(of([]))
  };
  const authServiceMock = { currentUser: () => ({ id: 2, username: 'helper', email: 'h@x.de', is_active: true, is_verified: true, is_admin: false, created_at: '' }) };

  beforeEach(async () => {
    vi.clearAllMocks();
    beekeepingServiceMock.getTasks.mockReturnValue(of([task]));
    beekeepingServiceMock.acknowledgeTaskDelegation.mockReturnValue(of({ ...task, delegation_seen_at: '2026-07-24T00:00:00Z' }));
    apiaryServiceMock.getApiaries.mockReturnValue(of([]));

    await TestBed.configureTestingModule({
      imports: [TasksComponent],
      providers: [
        { provide: BeekeepingService, useValue: beekeepingServiceMock },
        { provide: HiveService, useValue: hiveServiceMock },
        { provide: ApiaryService, useValue: apiaryServiceMock },
        { provide: AuthService, useValue: authServiceMock }
      ]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(TasksComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should list tasks delegated to the current user', () => {
    const fixture = TestBed.createComponent(TasksComponent);
    const component = fixture.componentInstance as unknown as { delegatedToMe: () => { id: number }[] };
    expect(component.delegatedToMe().map(t => t.id)).toEqual([1]);
  });

  it('should acknowledge a delegated task', () => {
    const fixture = TestBed.createComponent(TasksComponent);
    const component = fixture.componentInstance as unknown as { acknowledgeDelegation: (t: typeof task) => void };
    component.acknowledgeDelegation(task);
    expect(beekeepingServiceMock.acknowledgeTaskDelegation).toHaveBeenCalledWith(1);
  });

  it('should compose an RRULE string when creating a recurring task', () => {
    const fixture = TestBed.createComponent(TasksComponent);
    const component = fixture.componentInstance as unknown as {
      form: { patchValue: (v: Record<string, unknown>) => void };
      createTask: () => void;
    };
    component.form.patchValue({ title: 'Wöchentliche Kontrolle', recurrence: 'weekly' });
    component.createTask();
    expect(beekeepingServiceMock.createTask).toHaveBeenCalledWith(expect.objectContaining({ recurrence_rule: 'FREQ=WEEKLY' }));
  });
});
