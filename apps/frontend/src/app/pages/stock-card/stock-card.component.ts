import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';

import { TimelineEvent } from '../../core/models/beekeeping.models';
import { Hive } from '../../core/models/hive.models';
import { HiveService } from '../../core/services/hive.service';

@Component({
  selector: 'app-stock-card',
  standalone: true,
  imports: [DatePipe, RouterLink],
  templateUrl: './stock-card.component.html',
  styleUrl: './stock-card.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class StockCardComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly hiveService = inject(HiveService);

  protected readonly hiveId = Number(this.route.snapshot.paramMap.get('hiveId'));
  protected readonly typeFilter = signal('all');
  protected readonly fromDate = signal('');
  protected readonly toDate = signal('');
  protected readonly stockCard = toSignal(this.hiveService.getStockCard(this.hiveId), { initialValue: null });
  protected readonly hive = computed(() => this.stockCard()?.hive as Hive | null);
  protected readonly qrUrl = computed(() => `${location.origin}${this.stockCard()?.qr_url ?? `/stock-card/${this.hiveId}`}`);
  protected readonly eventTypes = computed(() => {
    const types = new Set((this.stockCard()?.events ?? []).map(event => event.type));
    return ['all', ...Array.from(types)];
  });
  protected readonly events = computed(() => {
    const from = this.fromDate();
    const to = this.toDate();
    return (this.stockCard()?.events ?? []).filter(event => {
      if (this.typeFilter() !== 'all' && event.type !== this.typeFilter()) return false;
      if (from && event.date < from) return false;
      if (to && event.date > to) return false;
      return true;
    });
  });

  protected eventMeta(event: TimelineEvent): string {
    if (event.type === 'harvest') return `${event.amount_kg ?? 0} kg`;
    if (event.type === 'feeding') return `${event.amount_kg_or_l ?? 0} kg/l`;
    if (event.status) return event.status;
    return event.type;
  }
}
