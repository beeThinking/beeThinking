import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { toSignal } from '@angular/core/rxjs-interop';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HiveService } from '../../core/services/hive.service';
import { ApiaryService } from '../../core/services/apiary.service';
import { Task, TaskPriority, TaskStatus } from '../../core/models/beekeeping.models';

type TaskView = 'today' | 'overdue' | 'week' | 'open' | 'done';

@Component({
  selector: 'app-tasks',
  standalone: true,
  imports: [DatePipe, ReactiveFormsModule],
  templateUrl: './tasks.component.html',
  styleUrl: './tasks.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class TasksComponent {
  private readonly beekeeping = inject(BeekeepingService);
  private readonly hiveService = inject(HiveService);
  private readonly apiaryService = inject(ApiaryService);
  private readonly fb = inject(FormBuilder);

  private readonly remoteTasks = toSignal(this.beekeeping.getTasks(), { initialValue: [] });
  private readonly localTasks = signal<Task[] | null>(null);
  protected readonly tasks = computed(() => this.localTasks() ?? this.remoteTasks());
  protected readonly hives = toSignal(this.hiveService.getHives(), { initialValue: [] });
  protected readonly apiaries = toSignal(this.apiaryService.getApiaries(), { initialValue: [] });
  protected readonly view = signal<TaskView>('today');
  protected readonly showForm = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly priorities: TaskPriority[] = ['low', 'medium', 'high', 'urgent'];
  protected readonly views: { id: TaskView; label: string }[] = [
    { id: 'today', label: 'Heute' },
    { id: 'overdue', label: 'Überfällig' },
    { id: 'week', label: 'Woche' },
    { id: 'open', label: 'Offen' },
    { id: 'done', label: 'Erledigt' }
  ];

  protected readonly form = this.fb.group({
    title: ['', [Validators.required, Validators.maxLength(200)]],
    description: [''],
    due_date: [''],
    priority: ['medium' as TaskPriority],
    hive_id: [null as number | null],
    apiary_id: [null as number | null]
  });

  protected readonly visibleTasks = computed(() => {
    const today = this.startOfDay(new Date());
    const weekEnd = new Date(today);
    weekEnd.setDate(today.getDate() + 7);
    return this.tasks().filter(task => {
      const due = task.due_date ? this.startOfDay(new Date(task.due_date)) : null;
      if (this.view() === 'done') return task.status === 'done';
      if (task.status !== 'open') return false;
      if (this.view() === 'overdue') return !!due && due < today;
      if (this.view() === 'today') return !!due && due.getTime() === today.getTime();
      if (this.view() === 'week') return !!due && due >= today && due <= weekEnd;
      return true;
    });
  });

  protected setView(view: TaskView): void {
    this.view.set(view);
  }

  protected openForm(): void {
    this.form.reset({ priority: 'medium' as TaskPriority });
    this.showForm.set(true);
  }

  protected closeForm(): void {
    this.showForm.set(false);
    this.form.reset({ priority: 'medium' as TaskPriority });
  }

  protected createTask(): void {
    if (this.form.invalid) return;
    const value = this.form.value;
    this.beekeeping.createTask({
      title: value.title!,
      description: value.description || undefined,
      due_date: value.due_date || undefined,
      priority: value.priority as TaskPriority,
      hive_id: value.hive_id ? Number(value.hive_id) : null,
      apiary_id: value.apiary_id ? Number(value.apiary_id) : null
    }).subscribe({
      next: task => {
        this.localTasks.update(list => [task, ...(list ?? this.remoteTasks())]);
        this.closeForm();
      },
      error: () => this.errorMessage.set('Aufgabe konnte nicht erstellt werden.')
    });
  }

  protected complete(task: Task): void {
    this.beekeeping.completeTask(task.id).subscribe({
      next: updated => this.replaceTask(updated),
      error: () => this.errorMessage.set('Aufgabe konnte nicht erledigt werden.')
    });
  }

  protected cancel(task: Task): void {
    this.beekeeping.updateTask(task.id, { status: 'cancelled' as TaskStatus }).subscribe({
      next: updated => this.replaceTask(updated),
      error: () => this.errorMessage.set('Aufgabe konnte nicht aktualisiert werden.')
    });
  }

  protected deleteTask(task: Task): void {
    if (!confirm(`Aufgabe "${task.title}" löschen?`)) return;
    this.beekeeping.deleteTask(task.id).subscribe({
      next: () => this.localTasks.update(list => (list ?? this.remoteTasks()).filter(t => t.id !== task.id)),
      error: () => this.errorMessage.set('Aufgabe konnte nicht gelöscht werden.')
    });
  }

  protected hiveName(id: number | null): string {
    if (!id) return 'Ohne Volk';
    return this.hives().find(h => h.id === id)?.name ?? `Volk #${id}`;
  }

  protected priorityLabel(priority: TaskPriority): string {
    return { low: 'Niedrig', medium: 'Normal', high: 'Hoch', urgent: 'Dringend' }[priority];
  }

  private replaceTask(updated: Task): void {
    this.localTasks.update(list => (list ?? this.remoteTasks()).map(task => task.id === updated.id ? updated : task));
  }

  private startOfDay(value: Date): Date {
    return new Date(value.getFullYear(), value.getMonth(), value.getDate());
  }
}
