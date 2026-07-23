import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { toSignal } from '@angular/core/rxjs-interop';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HiveService } from '../../core/services/hive.service';
import { ApiaryService } from '../../core/services/apiary.service';
import { Harvest } from '../../core/models/beekeeping.models';
import { OfflineQueueService } from '../../core/services/offline-queue.service';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { localDateString } from '../../core/utils/date.utils';

@Component({
  selector: 'app-harvests',
  standalone: true,
  imports: [DatePipe, DecimalPipe, ReactiveFormsModule, TranslatePipe],
  templateUrl: './harvests.component.html',
  styleUrl: './harvests.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HarvestsComponent {
  private readonly beekeeping = inject(BeekeepingService);
  private readonly hiveService = inject(HiveService);
  private readonly apiaryService = inject(ApiaryService);
  private readonly fb = inject(FormBuilder);
  private readonly offlineQueue = inject(OfflineQueueService);
  private readonly translation = inject(TranslationService);

  private readonly remoteHarvests = toSignal(this.beekeeping.getHarvests(), { initialValue: [] });
  private readonly localHarvests = signal<Harvest[] | null>(null);
  protected readonly harvests = computed(() => this.localHarvests() ?? this.remoteHarvests());
  protected readonly hives = toSignal(this.hiveService.getHives(), { initialValue: [] });
  protected readonly apiaries = toSignal(this.apiaryService.getApiaries(), { initialValue: [] });
  protected readonly showForm = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly totalKg = computed(() => this.harvests().reduce((sum, harvest) => sum + harvest.amount_kg, 0));

  protected readonly form = this.fb.group({
    harvest_date: [localDateString(), Validators.required],
    amount_kg: [0, [Validators.required, Validators.min(0)]],
    crop_type: [''],
    water_content_percent: [null as number | null, [Validators.min(0), Validators.max(100)]],
    batch_code: [''],
    hive_id: [null as number | null],
    apiary_id: [null as number | null],
    notes: ['']
  });

  protected createHarvest(): void {
    if (this.form.invalid) return;
    const value = this.form.value;
    const payload = {
      harvest_date: value.harvest_date!,
      amount_kg: Number(value.amount_kg ?? 0),
      crop_type: value.crop_type || undefined,
      water_content_percent: value.water_content_percent !== null && value.water_content_percent !== undefined
        ? Number(value.water_content_percent)
        : undefined,
      batch_code: value.batch_code || undefined,
      hive_id: value.hive_id ? Number(value.hive_id) : null,
      apiary_id: value.apiary_id ? Number(value.apiary_id) : null,
      notes: value.notes || undefined
    };
    this.beekeeping.createHarvest(payload).subscribe({
      next: harvest => {
        this.localHarvests.update(list => [harvest, ...(list ?? this.remoteHarvests())]);
        this.showForm.set(false);
        this.form.reset({ harvest_date: localDateString(), amount_kg: 0 });
      },
      error: () => {
        if (typeof navigator !== 'undefined' && !navigator.onLine) {
          this.offlineQueue.enqueue('/api/harvests', payload, 'Ernte');
          this.showForm.set(false);
          this.errorMessage.set(this.translation.t('offline.queued'));
          return;
        }
        this.errorMessage.set(this.translation.t('harvests.error.save'));
      }
    });
  }

  protected deleteHarvest(harvest: Harvest): void {
    if (!confirm(this.translation.t('harvests.delete.confirm'))) return;
    this.beekeeping.deleteHarvest(harvest.id).subscribe({
      next: () => this.localHarvests.update(list => (list ?? this.remoteHarvests()).filter(h => h.id !== harvest.id)),
      error: () => this.errorMessage.set(this.translation.t('harvests.error.delete'))
    });
  }

  protected hiveName(id: number | null): string {
    if (!id) return this.translation.t('harvests.form.allHives');
    return this.hives().find(h => h.id === id)?.name ?? this.translation.t('common.hiveRef', { id });
  }

  protected apiaryName(id: number | null): string {
    if (!id) return this.translation.t('harvests.form.noApiary');
    const apiary = this.apiaries().find(a => a.id === id);
    return apiary ? this.apiaryTitle(apiary) : this.translation.t('common.apiaryRef', { id });
  }

  protected apiaryTitle(apiary: { stock_number: string; name: string | null }): string {
    return apiary.name?.trim() || apiary.stock_number;
  }
}
