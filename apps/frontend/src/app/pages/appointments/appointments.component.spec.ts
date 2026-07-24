import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { Task } from '../../core/models/beekeeping.models';
import { ApiaryService } from '../../core/services/apiary.service';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HiveService } from '../../core/services/hive.service';
import { TranslationService } from '../../core/services/translation.service';
import { GoogleCalendarService } from '../../core/services/google-calendar.service';
import { AppointmentsComponent } from './appointments.component';

describe('AppointmentsComponent', () => {
  const appointment: Task = {
    id: 1,
    owner_id: 2,
    hive_id: null,
    apiary_id: null,
    assignee_id: null,
    title: 'Summer inspection',
    description: 'Bring smoker',
    due_date: '2099-07-20',
    start_at: '2099-07-20T08:00:00Z',
    end_at: '2099-07-20T09:00:00Z',
    kind: 'appointment',
    priority: 'high',
    status: 'open',
    source: 'manual',
    recurrence_rule: null,
    delegated_at: null,
    delegation_seen_at: null,
    created_at: '2026-07-13T10:00:00Z',
    updated_at: null,
    completed_at: null
  };

  const beekeeping = {
    getTasks: vi.fn(() => of([appointment])),
    createTask: vi.fn((payload) => of({ ...appointment, ...payload, id: 2 })),
    updateTask: vi.fn((id, payload) => of({ ...appointment, ...payload, id })),
    completeTask: vi.fn(() => of({ ...appointment, status: 'done' })),
    deleteTask: vi.fn(() => of(undefined))
  };

  beforeEach(() => {
    vi.clearAllMocks();
    TestBed.configureTestingModule({
      imports: [AppointmentsComponent],
      providers: [
        { provide: BeekeepingService, useValue: beekeeping },
        { provide: HiveService, useValue: { getHives: vi.fn(() => of([])) } },
        { provide: ApiaryService, useValue: { getApiaries: vi.fn(() => of([])) } },
        {
          provide: GoogleCalendarService,
          useValue: {
            getStatus: vi.fn(() => of({ enabled: false, connected: false, calendar_name: null, last_sync_at: null, last_error: null })),
            startConnection: vi.fn(),
            sync: vi.fn(),
            disconnect: vi.fn()
          }
        },
        { provide: TranslationService, useValue: { t: (key: string) => key } }
      ]
    });
  });

  it('shows upcoming appointments in agenda view', () => {
    const fixture = TestBed.createComponent(AppointmentsComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.querySelector('.appointment-card h2')?.textContent).toContain('Summer inspection');
    expect(element.querySelector('.location')?.textContent).toContain('appointments.noLocation');
  });

  it('creates an appointment with ISO timestamps', () => {
    const fixture = TestBed.createComponent(AppointmentsComponent);
    const component = fixture.componentInstance as unknown as {
      openCreate(): void;
      save(): void;
      form: { setValue(value: Record<string, unknown>): void };
    };
    component.openCreate();
    component.form.setValue({
      title: 'Spring check',
      start_at: '2099-04-10T10:30',
      end_at: '2099-04-10T11:15',
      description: 'Check stores',
      priority: 'medium',
      apiary_id: null,
      hive_id: null
    });

    component.save();

    expect(beekeeping.createTask).toHaveBeenCalledWith(expect.objectContaining({
      title: 'Spring check',
      kind: 'appointment',
      due_date: '2099-04-10',
      start_at: new Date('2099-04-10T10:30').toISOString(),
      end_at: new Date('2099-04-10T11:15').toISOString()
    }));
  });

  it('updates an existing appointment', () => {
    const fixture = TestBed.createComponent(AppointmentsComponent);
    const component = fixture.componentInstance as unknown as {
      openEdit(task: Task): void;
      save(): void;
      form: { patchValue(value: Record<string, unknown>): void };
    };
    component.openEdit(appointment);
    component.form.patchValue({ title: 'Updated inspection' });

    component.save();

    expect(beekeeping.updateTask).toHaveBeenCalledWith(1, expect.objectContaining({ title: 'Updated inspection' }));
  });
});
