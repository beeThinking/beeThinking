import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { Task } from '../../core/models/beekeeping.models';
import { BeekeepingService } from '../../core/services/beekeeping.service';

@Component({
  selector: 'app-appointments',
  standalone: true,
  imports: [DatePipe, FormsModule],
  templateUrl: './appointments.component.html',
  styleUrl: './appointments.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AppointmentsComponent {
  private readonly beekeeping = inject(BeekeepingService);
  protected readonly appointments = signal<Task[]>([]);
  protected readonly title = signal('');
  protected readonly startAt = signal('');
  protected readonly description = signal('');
  protected readonly message = signal('');

  constructor() { this.load(); }

  protected load(): void {
    this.beekeeping.getTasks('open').subscribe(tasks =>
      this.appointments.set(tasks.filter(task => task.kind === 'appointment'))
    );
  }

  protected create(): void {
    if (!this.title().trim()) return;
    const startAt = this.startAt();
    this.beekeeping.createTask({
      title: this.title().trim(),
      description: this.description() || undefined,
      due_date: startAt ? startAt.slice(0, 10) : undefined,
      start_at: startAt ? new Date(startAt).toISOString() : undefined,
      kind: 'appointment'
    }).subscribe({
      next: () => {
        this.title.set('');
        this.startAt.set('');
        this.description.set('');
        this.message.set('Termin angelegt.');
        this.load();
      },
      error: () => this.message.set('Termin konnte nicht angelegt werden.')
    });
  }

  protected complete(task: Task): void {
    this.beekeeping.completeTask(task.id).subscribe(() => this.load());
  }
}
