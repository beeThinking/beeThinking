import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ApiaryService } from '../../core/services/apiary.service';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HiveService } from '../../core/services/hive.service';
import { Task, TaskCreate, TaskPriority, TaskUpdate } from '../../core/models/beekeeping.models';
import { Apiary } from '../../core/models/apiary.models';
import { Hive } from '../../core/models/hive.models';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { TranslationKey } from '../../core/i18n/en';
import { createICalendar } from '../../core/utils/calendar.utils';

type AppointmentView = 'upcoming' | 'past' | 'done';

@Component({
  selector: 'app-appointments',
  standalone: true,
  imports: [DatePipe, ReactiveFormsModule, TranslatePipe],
  templateUrl: './appointments.component.html',
  styleUrl: './appointments.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AppointmentsComponent {
  private readonly beekeeping = inject(BeekeepingService);
  private readonly hiveService = inject(HiveService);
  private readonly apiaryService = inject(ApiaryService);
  private readonly translation = inject(TranslationService);
  private readonly fb = inject(FormBuilder);

  protected readonly appointments = signal<Task[]>([]);
  protected readonly hives = signal<Hive[]>([]);
  protected readonly apiaries = signal<Apiary[]>([]);
  protected readonly view = signal<AppointmentView>('upcoming');
  protected readonly editorOpen = signal(false);
  protected readonly editingId = signal<number | null>(null);
  protected readonly saving = signal(false);
  protected readonly message = signal('');
  protected readonly priorities: TaskPriority[] = ['low', 'medium', 'high', 'urgent'];
  protected readonly views: { id: AppointmentView; labelKey: TranslationKey }[] = [
    { id: 'upcoming', labelKey: 'appointments.view.upcoming' },
    { id: 'past', labelKey: 'appointments.view.past' },
    { id: 'done', labelKey: 'appointments.view.done' }
  ];

  protected readonly form = this.fb.group({
    title: ['', [Validators.required, Validators.maxLength(200)]],
    start_at: ['', Validators.required],
    end_at: [''],
    description: [''],
    priority: ['medium' as TaskPriority],
    apiary_id: [null as number | null],
    hive_id: [null as number | null]
  });

  protected readonly upcomingCount = computed(() => this.appointments().filter(task => task.status === 'open' && !this.isPast(task)).length);
  protected readonly visibleAppointments = computed(() => {
    const items = this.appointments().filter(task => {
      if (this.view() === 'done') return task.status === 'done';
      if (task.status !== 'open') return false;
      return this.view() === 'past' ? this.isPast(task) : !this.isPast(task);
    });
    return [...items].sort((a, b) => this.appointmentTime(a) - this.appointmentTime(b));
  });

  constructor() {
    this.load();
    this.hiveService.getHives().subscribe(hives => this.hives.set(hives));
    this.apiaryService.getApiaries().subscribe(apiaries => this.apiaries.set(apiaries));
  }

  protected load(): void {
    this.beekeeping.getTasks().subscribe({
      next: tasks => this.appointments.set(tasks.filter(task => task.kind === 'appointment')),
      error: () => this.message.set(this.translation.t('appointments.error.load'))
    });
  }

  protected setView(view: AppointmentView): void {
    this.view.set(view);
  }

  protected openCreate(): void {
    this.editingId.set(null);
    this.form.reset({ priority: 'medium', apiary_id: null, hive_id: null });
    this.message.set('');
    this.editorOpen.set(true);
  }

  protected openEdit(appointment: Task): void {
    this.editingId.set(appointment.id);
    this.form.reset({
      title: appointment.title,
      start_at: this.localDateTime(appointment.start_at),
      end_at: this.localDateTime(appointment.end_at),
      description: appointment.description ?? '',
      priority: appointment.priority,
      apiary_id: appointment.apiary_id,
      hive_id: appointment.hive_id
    });
    this.message.set('');
    this.editorOpen.set(true);
  }

  protected closeEditor(): void {
    this.editorOpen.set(false);
    this.editingId.set(null);
  }

  protected save(): void {
    if (this.form.invalid || this.saving()) return;
    const value = this.form.getRawValue();
    const start = new Date(value.start_at!);
    const end = value.end_at ? new Date(value.end_at) : null;
    if (end && end <= start) {
      this.message.set(this.translation.t('appointments.error.endBeforeStart'));
      return;
    }

    const payload: TaskUpdate = {
      title: value.title!.trim(),
      description: value.description?.trim() || null,
      due_date: value.start_at!.slice(0, 10),
      start_at: start.toISOString(),
      end_at: end?.toISOString() ?? null,
      priority: value.priority ?? 'medium',
      apiary_id: value.apiary_id ? Number(value.apiary_id) : null,
      hive_id: value.hive_id ? Number(value.hive_id) : null,
      kind: 'appointment'
    };

    this.saving.set(true);
    const editingId = this.editingId();
    const createPayload: TaskCreate = {
      ...payload,
      title: payload.title!,
      description: payload.description ?? undefined,
      due_date: payload.due_date ?? undefined,
      start_at: payload.start_at ?? undefined,
      end_at: payload.end_at ?? undefined
    };
    const request = editingId === null
      ? this.beekeeping.createTask(createPayload)
      : this.beekeeping.updateTask(editingId, payload);
    request.subscribe({
      next: appointment => {
        this.appointments.update(items => editingId === null
          ? [...items, appointment]
          : items.map(item => item.id === appointment.id ? appointment : item));
        this.message.set(this.translation.t(editingId === null ? 'appointments.created' : 'appointments.updated'));
        this.saving.set(false);
        this.closeEditor();
      },
      error: () => {
        this.message.set(this.translation.t('appointments.error.save'));
        this.saving.set(false);
      }
    });
  }

  protected complete(appointment: Task): void {
    this.beekeeping.completeTask(appointment.id).subscribe({
      next: updated => this.replace(updated),
      error: () => this.message.set(this.translation.t('appointments.error.complete'))
    });
  }

  protected reopen(appointment: Task): void {
    this.beekeeping.updateTask(appointment.id, { status: 'open' }).subscribe({
      next: updated => this.replace(updated),
      error: () => this.message.set(this.translation.t('appointments.error.reopen'))
    });
  }

  protected remove(appointment: Task): void {
    if (!confirm(this.translation.t('appointments.delete.confirm', { title: appointment.title }))) return;
    this.beekeeping.deleteTask(appointment.id).subscribe({
      next: () => this.appointments.update(items => items.filter(item => item.id !== appointment.id)),
      error: () => this.message.set(this.translation.t('appointments.error.delete'))
    });
  }

  protected exportUpcoming(): void {
    const appointments = this.appointments().filter(item =>
      item.status === 'open' && !this.isPast(item) && !!(item.start_at ?? item.due_date)
    );
    if (!appointments.length) {
      this.message.set(this.translation.t('appointments.export.empty'));
      return;
    }
    const calendar = createICalendar(appointments.map(item => ({
      uid: `appointment-${item.id}@beethinking`,
      title: item.title,
      description: item.description,
      location: this.locationLabel(item),
      start: item.start_at ?? item.due_date!,
      end: item.end_at
    })));
    const url = URL.createObjectURL(new Blob([calendar], { type: 'text/calendar;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'beethinking-appointments.ics';
    link.click();
    URL.revokeObjectURL(url);
  }

  protected priorityLabel(priority: TaskPriority): string {
    return this.translation.t(`tasks.priority.${priority}` as TranslationKey);
  }

  protected locationLabel(appointment: Task): string {
    const hive = appointment.hive_id ? this.hives().find(item => item.id === appointment.hive_id) : null;
    if (hive) return hive.name;
    const apiary = appointment.apiary_id ? this.apiaries().find(item => item.id === appointment.apiary_id) : null;
    return apiary ? apiary.name?.trim() || apiary.stock_number : this.translation.t('appointments.noLocation');
  }

  private replace(updated: Task): void {
    this.appointments.update(items => items.map(item => item.id === updated.id ? updated : item));
  }

  private isPast(appointment: Task): boolean {
    const end = appointment.end_at ?? appointment.start_at ?? appointment.due_date;
    return end ? new Date(end).getTime() < Date.now() : false;
  }

  private appointmentTime(appointment: Task): number {
    const value = appointment.start_at ?? appointment.due_date;
    return value ? new Date(value).getTime() : Number.MAX_SAFE_INTEGER;
  }

  private localDateTime(value: string | null): string {
    if (!value) return '';
    const date = new Date(value);
    const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
    return local.toISOString().slice(0, 16);
  }
}
