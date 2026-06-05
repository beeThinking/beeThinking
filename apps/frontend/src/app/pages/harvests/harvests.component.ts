import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { toSignal } from '@angular/core/rxjs-interop';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HiveService } from '../../core/services/hive.service';
import { ApiaryService } from '../../core/services/apiary.service';
import { Harvest } from '../../core/models/beekeeping.models';

@Component({
  selector: 'app-harvests',
  standalone: true,
  imports: [DatePipe, DecimalPipe, ReactiveFormsModule],
  templateUrl: './harvests.component.html',
  styleUrl: './harvests.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HarvestsComponent {
  private readonly beekeeping = inject(BeekeepingService);
  private readonly hiveService = inject(HiveService);
  private readonly apiaryService = inject(ApiaryService);
  private readonly fb = inject(FormBuilder);

  private readonly remoteHarvests = toSignal(this.beekeeping.getHarvests(), { initialValue: [] });
  private readonly localHarvests = signal<Harvest[] | null>(null);
  protected readonly harvests = computed(() => this.localHarvests() ?? this.remoteHarvests());
  protected readonly hives = toSignal(this.hiveService.getHives(), { initialValue: [] });
  protected readonly apiaries = toSignal(this.apiaryService.getApiaries(), { initialValue: [] });
  protected readonly showForm = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly totalKg = computed(() => this.harvests().reduce((sum, harvest) => sum + harvest.amount_kg, 0));

  protected readonly form = this.fb.group({
    harvest_date: [new Date().toISOString().slice(0, 10), Validators.required],
    amount_kg: [0, [Validators.required, Validators.min(0)]],
    crop_type: [''],
    batch_code: [''],
    hive_id: [null as number | null],
    apiary_id: [null as number | null],
    notes: ['']
  });

  protected createHarvest(): void {
    if (this.form.invalid) return;
    const value = this.form.value;
    this.beekeeping.createHarvest({
      harvest_date: value.harvest_date!,
      amount_kg: Number(value.amount_kg ?? 0),
      crop_type: value.crop_type || undefined,
      batch_code: value.batch_code || undefined,
      hive_id: value.hive_id ? Number(value.hive_id) : null,
      apiary_id: value.apiary_id ? Number(value.apiary_id) : null,
      notes: value.notes || undefined
    }).subscribe({
      next: harvest => {
        this.localHarvests.update(list => [harvest, ...(list ?? this.remoteHarvests())]);
        this.showForm.set(false);
        this.form.reset({ harvest_date: new Date().toISOString().slice(0, 10), amount_kg: 0 });
      },
      error: () => this.errorMessage.set('Ernte konnte nicht gespeichert werden.')
    });
  }

  protected deleteHarvest(harvest: Harvest): void {
    if (!confirm('Ernte löschen?')) return;
    this.beekeeping.deleteHarvest(harvest.id).subscribe({
      next: () => this.localHarvests.update(list => (list ?? this.remoteHarvests()).filter(h => h.id !== harvest.id)),
      error: () => this.errorMessage.set('Ernte konnte nicht gelöscht werden.')
    });
  }

  protected hiveName(id: number | null): string {
    if (!id) return 'Alle Völker';
    return this.hives().find(h => h.id === id)?.name ?? `Volk #${id}`;
  }

  protected apiaryName(id: number | null): string {
    if (!id) return 'Ohne Standort';
    return this.apiaries().find(a => a.id === id)?.name ?? `Stand #${id}`;
  }
}
