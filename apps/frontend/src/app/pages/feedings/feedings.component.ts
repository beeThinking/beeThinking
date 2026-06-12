import { DatePipe, DecimalPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { ApiaryService } from '../../core/services/apiary.service';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HiveService } from '../../core/services/hive.service';
import { Feeding } from '../../core/models/beekeeping.models';

@Component({
  selector: 'app-feedings',
  standalone: true,
  imports: [DatePipe, DecimalPipe, ReactiveFormsModule],
  templateUrl: './feedings.component.html',
  styleUrl: './feedings.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class FeedingsComponent {
  private readonly beekeeping = inject(BeekeepingService);
  private readonly hiveService = inject(HiveService);
  private readonly apiaryService = inject(ApiaryService);
  private readonly fb = inject(FormBuilder);

  private readonly remoteFeedings = toSignal(this.beekeeping.getFeedings(), { initialValue: [] });
  private readonly localFeedings = signal<Feeding[] | null>(null);

  protected readonly feedings = computed(() => this.localFeedings() ?? this.remoteFeedings());
  protected readonly hives = toSignal(this.hiveService.getHives(), { initialValue: [] });
  protected readonly apiaries = toSignal(this.apiaryService.getApiaries(), { initialValue: [] });
  protected readonly showForm = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly totalAmount = computed(() =>
    this.feedings().reduce((sum, feeding) => sum + feeding.amount_kg_or_l, 0)
  );

  protected readonly form = this.fb.group({
    date: [new Date().toISOString().slice(0, 10), Validators.required],
    feed_type: ['', [Validators.required, Validators.maxLength(120)]],
    amount_kg_or_l: [0, [Validators.required, Validators.min(0)]],
    hive_id: [null as number | null],
    apiary_id: [null as number | null],
    notes: ['']
  });

  protected createFeeding(): void {
    if (this.form.invalid) return;

    const value = this.form.value;
    this.beekeeping.createFeeding({
      date: value.date!,
      feed_type: value.feed_type!,
      amount_kg_or_l: Number(value.amount_kg_or_l ?? 0),
      hive_id: value.hive_id ? Number(value.hive_id) : null,
      apiary_id: value.apiary_id ? Number(value.apiary_id) : null,
      notes: value.notes || undefined
    }).subscribe({
      next: feeding => {
        this.localFeedings.update(list => [feeding, ...(list ?? this.remoteFeedings())]);
        this.showForm.set(false);
        this.form.reset({ date: new Date().toISOString().slice(0, 10), amount_kg_or_l: 0 });
      },
      error: () => this.errorMessage.set('Fütterung konnte nicht gespeichert werden.')
    });
  }

  protected deleteFeeding(feeding: Feeding): void {
    if (!confirm('Diese Fütterung löschen?')) return;
    this.beekeeping.deleteFeeding(feeding.id).subscribe({
      next: () => this.localFeedings.update(list =>
        (list ?? this.remoteFeedings()).filter(item => item.id !== feeding.id)
      ),
      error: () => this.errorMessage.set('Fütterung konnte nicht gelöscht werden.')
    });
  }

  protected hiveName(id: number | null): string {
    if (!id) return 'Alle Völker';
    return this.hives().find(hive => hive.id === id)?.name ?? `Volk #${id}`;
  }

  protected apiaryName(id: number | null): string {
    if (!id) return 'Kein Stand';
    const apiary = this.apiaries().find(item => item.id === id);
    return apiary ? this.apiaryTitle(apiary) : `Stand #${id}`;
  }

  protected apiaryTitle(apiary: { stock_number: string; name: string | null }): string {
    return apiary.name?.trim() || apiary.stock_number;
  }
}
