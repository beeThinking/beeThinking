import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { CurrencyPipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { BeekeepingService } from '../../core/services/beekeeping.service';
import { SaleReportRow } from '../../core/models/beekeeping.models';

@Component({
  selector: 'app-sales-report',
  standalone: true,
  imports: [CurrencyPipe, DecimalPipe, FormsModule, RouterLink],
  templateUrl: './sales-report.component.html',
  styleUrl: './sales-report.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class SalesReportComponent {
  private readonly beekeeping = inject(BeekeepingService);

  protected readonly fromDate = signal(this.localDate(new Date(new Date().getFullYear(), 0, 1)));
  protected readonly toDate = signal(this.localDate(new Date()));
  protected readonly rows = signal<SaleReportRow[]>([]);
  protected readonly errorMessage = signal('');

  protected readonly totals = computed(() =>
    this.rows().reduce(
      (acc, row) => ({
        quantity: acc.quantity + row.quantity,
        amount_gross: acc.amount_gross + row.amount_gross,
        amount_net: acc.amount_net + row.amount_net
      }),
      { quantity: 0, amount_gross: 0, amount_net: 0 }
    )
  );

  constructor() {
    this.load();
  }

  protected load(): void {
    this.errorMessage.set('');
    this.beekeeping.getSalesReport(this.fromDate(), this.toDate()).subscribe({
      next: rows => this.rows.set(rows),
      error: () => this.errorMessage.set('Report konnte nicht geladen werden.')
    });
  }

  private localDate(value: Date): string {
    const year = value.getFullYear();
    const month = String(value.getMonth() + 1).padStart(2, '0');
    const day = String(value.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
}
