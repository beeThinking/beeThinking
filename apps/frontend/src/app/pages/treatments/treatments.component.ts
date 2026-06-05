import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { toSignal } from '@angular/core/rxjs-interop';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HiveService } from '../../core/services/hive.service';
import { Treatment, VarroaTreatmentType, VarroaWeatherWindow } from '../../core/models/beekeeping.models';

@Component({
  selector: 'app-treatments',
  standalone: true,
  imports: [DatePipe, ReactiveFormsModule],
  templateUrl: './treatments.component.html',
  styleUrl: './treatments.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class TreatmentsComponent {
  private readonly beekeeping = inject(BeekeepingService);
  private readonly hiveService = inject(HiveService);
  private readonly fb = inject(FormBuilder);

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
    started_at: [new Date().toISOString().slice(0, 10), Validators.required],
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
    this.beekeeping.createTreatment({
      hive_id: Number(value.hive_id),
      started_at: value.started_at!,
      ended_at: value.ended_at || undefined,
      product: value.product!,
      method: value.method || undefined,
      dosage: value.dosage || undefined,
      reason: value.reason || undefined,
      weather_window_id: value.weather_window_id ?? undefined,
      notes: value.notes || undefined
    }).subscribe({
      next: treatment => {
        this.localTreatments.update(list => [treatment, ...(list ?? this.remoteTreatments())]);
        this.showForm.set(false);
        this.form.reset({ started_at: new Date().toISOString().slice(0, 10) });
      },
      error: () => this.errorMessage.set('Behandlung konnte nicht gespeichert werden.')
    });
  }

  protected deleteTreatment(treatment: Treatment): void {
    if (!confirm('Behandlung löschen?')) return;
    this.beekeeping.deleteTreatment(treatment.id).subscribe({
      next: () => this.localTreatments.update(list => (list ?? this.remoteTreatments()).filter(t => t.id !== treatment.id)),
      error: () => this.errorMessage.set('Behandlung konnte nicht gelöscht werden.')
    });
  }

  protected hiveName(id: number): string {
    return this.hives().find(h => h.id === id)?.name ?? `Volk #${id}`;
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
        this.weatherNote.set('Wetterfenster nicht verfügbar.');
      }
    });
  }

  protected ratingLabel(rating: string): string {
    return ({ suitable: 'geeignet', caution: 'kritisch', unsuitable: 'ungeeignet', unknown: 'keine Daten' } as Record<string, string>)[rating] ?? rating;
  }
}
