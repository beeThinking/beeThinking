import { Component, ChangeDetectionStrategy, inject, computed } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { DecimalPipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { BeekeepingService } from '../../core/services/beekeeping.service';

@Component({
  selector: 'app-dashboard',
  imports: [DecimalPipe, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DashboardComponent {
  private readonly beekeepingService = inject(BeekeepingService);

  protected readonly summary = toSignal(this.beekeepingService.getDashboardSummary(), {
    initialValue: {
      apiary_count: 0,
      hive_count: 0,
      open_task_count: 0,
      overdue_task_count: 0,
      tasks_due_this_week: 0,
      treatment_count: 0,
      harvest_kg_total: 0,
      latest_inspection_date: null,
      hives: []
    }
  });

  protected readonly attentionHives = computed(() =>
    this.summary().hives.filter(h => h.status !== 'active' || h.swarm_risk !== 'low').slice(0, 6)
  );

  protected formatDate(value: string | null): string {
    if (!value) return 'Noch keine';
    return new Date(value).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' });
  }
}
