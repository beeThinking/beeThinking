import { CurrencyPipe, DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { forkJoin } from 'rxjs';

import { ApiaryService } from '../../core/services/apiary.service';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { CashbookEntry, CashbookSummary } from '../../core/models/beekeeping.models';

@Component({
  selector: 'app-cashbook',
  standalone: true,
  imports: [CurrencyPipe, DatePipe, ReactiveFormsModule],
  templateUrl: './cashbook.component.html',
  styleUrl: './cashbook.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class CashbookComponent {
  private readonly beekeeping = inject(BeekeepingService);
  private readonly apiaryService = inject(ApiaryService);
  private readonly fb = inject(FormBuilder);

  protected readonly entries = signal<CashbookEntry[]>([]);
  protected readonly summary = signal<CashbookSummary>({ income: 0, expenses: 0, surplus: 0 });
  protected readonly apiaries = signal<{ id: number; name: string }[]>([]);
  protected readonly showForm = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly fromDate = signal(this.localDate(new Date(new Date().getFullYear(), 0, 1)));
  protected readonly toDate = signal(this.localDate(new Date()));
  protected readonly signedEntries = computed(() =>
    this.entries().map(entry => ({
      ...entry,
      signedAmount: entry.direction === 'income' ? entry.amount_net : -entry.amount_net
    }))
  );

  protected readonly form = this.fb.group({
    booking_date: [this.localDate(new Date()), Validators.required],
    direction: ['expense' as 'income' | 'expense', Validators.required],
    category: ['', Validators.required],
    amount_gross: [0, [Validators.required, Validators.min(0)]],
    tax_rate: [0, [Validators.min(0), Validators.max(100)]],
    amount_net: [0, [Validators.required, Validators.min(0)]],
    counterparty: [''],
    description: [''],
    payment_method: [''],
    apiary_id: [null as number | null]
  });

  constructor() {
    this.load();
  }

  protected load(): void {
    const from = this.fromDate();
    const to = this.toDate();
    forkJoin({
      entries: this.beekeeping.getCashbookEntries(from, to),
      summary: this.beekeeping.getCashbookSummary(from, to),
      apiaries: this.apiaryService.getApiaries()
    }).subscribe({
      next: result => {
        this.entries.set(result.entries);
        this.summary.set(result.summary);
        this.apiaries.set(result.apiaries.map(apiary => ({ id: apiary.id, name: apiary.name })));
      },
      error: () => this.errorMessage.set('Kassenbuch konnte nicht geladen werden.')
    });
  }

  protected createEntry(): void {
    if (this.form.invalid) return;
    const value = this.form.value;
    this.beekeeping.createCashbookEntry({
      booking_date: value.booking_date!,
      direction: value.direction!,
      category: value.category!,
      amount_gross: Number(value.amount_gross ?? 0),
      tax_rate: Number(value.tax_rate ?? 0),
      amount_net: Number(value.amount_net ?? 0),
      counterparty: value.counterparty || undefined,
      description: value.description || undefined,
      payment_method: value.payment_method || undefined,
      apiary_id: value.apiary_id ? Number(value.apiary_id) : null
    }).subscribe({
      next: () => {
        this.showForm.set(false);
        this.form.reset({ booking_date: this.localDate(new Date()), direction: 'expense', amount_gross: 0, tax_rate: 0, amount_net: 0 });
        this.load();
      },
      error: () => this.errorMessage.set('Buchung konnte nicht gespeichert werden.')
    });
  }

  protected deleteEntry(entry: CashbookEntry): void {
    if (!confirm('Diese Buchung löschen?')) return;
    this.beekeeping.deleteCashbookEntry(entry.id).subscribe({
      next: () => this.load(),
      error: () => this.errorMessage.set('Buchung konnte nicht gelöscht werden.')
    });
  }

  protected apiaryName(id: number | null): string {
    if (!id) return 'Keine Imkerei';
    return this.apiaries().find(apiary => apiary.id === id)?.name ?? `Imkerei #${id}`;
  }

  private localDate(value: Date): string {
    const year = value.getFullYear();
    const month = String(value.getMonth() + 1).padStart(2, '0');
    const day = String(value.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
}
