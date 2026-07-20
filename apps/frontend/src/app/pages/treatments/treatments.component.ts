import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { toSignal } from '@angular/core/rxjs-interop';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HiveService } from '../../core/services/hive.service';
import { Treatment, VarroaTreatmentType, VarroaWeatherWindow } from '../../core/models/beekeeping.models';
import { OfflineQueueService } from '../../core/services/offline-queue.service';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { localDateString } from '../../core/utils/date.utils';

@Component({
  selector: 'app-treatments',
  standalone: true,
  imports: [DatePipe, ReactiveFormsModule, TranslatePipe],
  templateUrl: './treatments.component.html',
  styleUrl: './treatments.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class TreatmentsComponent {
  private readonly beekeeping = inject(BeekeepingService);
  private readonly hiveService = inject(HiveService);
  private readonly fb = inject(FormBuilder);
  private readonly offlineQueue = inject(OfflineQueueService);
  private readonly translation = inject(TranslationService);

  private readonly remoteTreatments = toSignal(this.beekeeping.getTreatments(), { initialValue: [] });
  private readonly localTreatments = signal<Treatment[] | null>(null);
  protected readonly treatments = computed(() => this.localTreatments() ?? this.remoteTreatments());
  protected readonly hives = toSignal(this.hiveService.getHives(), { initialValue: [] });
  protected readonly showForm = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly weatherWindows = signal<VarroaWeatherWindow[]>([]);
  protected readonly weatherNote = signal('');
  protected readonly selectedTreatmentType = signal<VarroaTreatmentType>('formic_acid_short');

  protected readonly form = this.fb.group({
    hive_id: [null as number | null, Validators.required],
    started_at: [localDateString(), Validators.required],
    ended_at: [''],
    product: ['', [Validators.required, Validators.maxLength(200)]],
    method: [''],
    dosage: [''],
    reason: [''],
    weather_window_id: [null as number | null],
    notes: ['']
  });

  constructor() {
    this.form.controls.hive_id.valueChanges.subscribe(hiveId => {
      if (hiveId) {
        this.loadWeather(Number(hiveId), this.selectedTreatmentType());
      } else {
        this.weatherWindows.set([]);
      }
    });
  }

  protected createTreatment(): void {
    if (this.form.invalid) return;
    const value = this.form.value;
    const payload = {
      hive_id: Number(value.hive_id),
      started_at: value.started_at!,
      ended_at: value.ended_at || undefined,
      product: value.product!,
      method: value.method || undefined,
      dosage: value.dosage || undefined,
      reason: value.reason || undefined,
      weather_window_id: value.weather_window_id ?? undefined,
      notes: value.notes || undefined
    };
    this.beekeeping.createTreatment(payload).subscribe({
      next: treatment => {
        this.localTreatments.update(list => [treatment, ...(list ?? this.remoteTreatments())]);
        this.showForm.set(false);
        this.form.reset({ started_at: localDateString() });
      },
      error: () => {
        if (typeof navigator !== 'undefined' && !navigator.onLine) {
          this.offlineQueue.enqueue('/api/treatments', payload, 'Behandlung');
          this.showForm.set(false);
          this.errorMessage.set(this.translation.t('offline.queued'));
          return;
        }
        this.errorMessage.set(this.translation.t('treatments.error.save'));
      }
    });
  }

  protected deleteTreatment(treatment: Treatment): void {
    if (!confirm(this.translation.t('treatments.delete.confirm'))) return;
    this.beekeeping.deleteTreatment(treatment.id).subscribe({
      next: () => this.localTreatments.update(list => (list ?? this.remoteTreatments()).filter(t => t.id !== treatment.id)),
      error: () => this.errorMessage.set(this.translation.t('treatments.error.delete'))
    });
  }

  protected hiveName(id: number): string {
    return this.hives().find(h => h.id === id)?.name ?? this.translation.t('common.hiveRef', { id });
  }

  protected loadWeather(hiveId: number, treatmentType: VarroaTreatmentType): void {
    this.selectedTreatmentType.set(treatmentType);
    this.weatherNote.set('');
    this.form.patchValue({ weather_window_id: null }, { emitEvent: false });
    this.hiveService.getVarroaAssistant(hiveId, treatmentType).subscribe({
      next: assistant => {
        this.weatherWindows.set(assistant.windows);
        this.weatherNote.set(assistant.source_note);
      },
      error: () => {
        this.weatherWindows.set([]);
        this.weatherNote.set(this.translation.t('treatments.weather.unavailable'));
      }
    });
  }

  protected ratingLabel(rating: string): string {
    return ({
      suitable: this.translation.t('treatments.rating.suitable'),
      caution: this.translation.t('treatments.rating.caution'),
      unsuitable: this.translation.t('treatments.rating.unsuitable'),
      unknown: this.translation.t('treatments.rating.unknown')
    } as Record<string, string>)[rating] ?? rating;
  }
}
