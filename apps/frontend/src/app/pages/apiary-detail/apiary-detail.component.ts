import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { map, switchMap } from 'rxjs';
import { VarroaTreatmentType, VarroaWeatherWindow } from '../../core/models/beekeeping.models';
import { ApiaryService } from '../../core/services/apiary.service';
import { HiveService } from '../../core/services/hive.service';
import { ApiaryMapPickerComponent } from '../../shared/components/apiary-map-picker.component';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { TranslationKey } from '../../core/i18n/en';

@Component({
  selector: 'app-apiary-detail',
  standalone: true,
  imports: [DecimalPipe, FormsModule, RouterLink, ApiaryMapPickerComponent, TranslatePipe],
  templateUrl: './apiary-detail.component.html',
  styleUrl: './apiary-detail.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ApiaryDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly apiaryService = inject(ApiaryService);
  private readonly hiveService = inject(HiveService);
  private readonly translation = inject(TranslationService);

  protected readonly apiaryId = Number(this.route.snapshot.paramMap.get('id'));
  protected readonly apiary = toSignal(
    this.route.paramMap.pipe(map(params => Number(params.get('id'))), switchMap(id => this.apiaryService.getApiary(id))),
    { initialValue: null }
  );
  protected readonly hives = toSignal(this.hiveService.getHives(), { initialValue: [] });
  protected readonly apiaryHives = computed(() => this.hives().filter(hive => hive.apiary_id === this.apiaryId));
  protected readonly selectedTreatment = signal<VarroaTreatmentType>('formic_acid_short');
  protected readonly weatherError = signal('');
  protected readonly weatherLoading = signal(false);
  protected readonly weatherWindows = signal<VarroaWeatherWindow[]>([]);
  protected readonly batchActionType = signal<'inspection' | 'treatment' | 'feeding' | 'harvest'>('inspection');
  protected readonly selectedHiveIds = signal<number[]>([]);
  protected readonly batchDate = signal(new Date().toISOString().slice(0, 10));
  protected readonly batchNotes = signal('');
  protected readonly batchAmount = signal<number | null>(null);
  protected readonly batchLabel = signal('');
  protected readonly batchSaving = signal(false);
  protected readonly batchMessage = signal('');

  protected readonly treatmentOptions: { value: VarroaTreatmentType; labelKey: TranslationKey }[] = [
    { value: 'formic_acid_short', labelKey: 'apiaryDetail.treatment.formicShort' },
    { value: 'formic_acid_long', labelKey: 'apiaryDetail.treatment.formicLong' },
    { value: 'thymol', labelKey: 'treatments.weather.thymol' },
    { value: 'oxalic_acid_dribble', labelKey: 'apiaryDetail.treatment.oxalicDribble' },
    { value: 'oxalic_acid_sublimation', labelKey: 'apiaryDetail.treatment.oxalicSublimation' },
    { value: 'lactic_acid', labelKey: 'apiaryDetail.treatment.lactic' },
    { value: 'biotechnical', labelKey: 'apiaryDetail.treatment.biotechnical' }
  ];

  constructor() {
    this.loadTreatment(this.selectedTreatment());
  }

  protected loadTreatment(value: VarroaTreatmentType): void {
    this.selectedTreatment.set(value);
    this.weatherLoading.set(true);
    this.weatherError.set('');
    this.apiaryService.getVarroaWeather(this.apiaryId, value).subscribe({
      next: windows => {
        this.weatherWindows.set(windows);
        this.weatherLoading.set(false);
      },
      error: () => {
        this.weatherError.set(this.translation.t('apiaryDetail.error.weatherLoad'));
        this.weatherLoading.set(false);
      }
    });
  }

  protected refreshWeather(): void {
    this.weatherLoading.set(true);
    this.weatherError.set('');
    this.apiaryService.refreshVarroaWeather(this.apiaryId).subscribe({
      next: windows => {
        const selected = this.selectedTreatment();
        this.weatherWindows.set(windows.filter(window => window.treatment_type === selected));
        this.weatherLoading.set(false);
      },
      error: () => {
        this.weatherError.set(this.translation.t('apiaryDetail.error.weatherRefresh'));
        this.weatherLoading.set(false);
      }
    });
  }

  protected formatDate(value: string): string {
    return new Date(value).toLocaleDateString(this.translation.currentLang() === 'de' ? 'de-DE' : 'en-US', { weekday: 'short', day: '2-digit', month: '2-digit' });
  }

  protected ratingLabel(rating: string): string {
    return ({
      suitable: this.translation.t('treatments.rating.suitable'),
      caution: this.translation.t('treatments.rating.caution'),
      unsuitable: this.translation.t('treatments.rating.unsuitable'),
      unknown: this.translation.t('treatments.rating.unknown')
    } as Record<string, string>)[rating] ?? rating;
  }

  protected apiaryTitle(apiary: { stock_number: string; name: string | null }): string {
    return apiary.name?.trim() || apiary.stock_number;
  }

  protected toggleHive(id: number, checked: boolean): void {
    this.selectedHiveIds.update(ids => checked ? [...new Set([...ids, id])] : ids.filter(existing => existing !== id));
  }

  protected submitBatchAction(): void {
    const hiveIds = this.selectedHiveIds();
    if (hiveIds.length === 0) {
      this.batchMessage.set('Bitte mindestens ein Volk wählen.');
      return;
    }
    this.batchSaving.set(true);
    this.batchMessage.set('');
    const action = this.batchActionType();
    const label = this.batchLabel().trim();
    const amount = this.batchAmount();
    const payload = {
      hive_ids: hiveIds,
      date: this.batchDate(),
      notes: this.batchNotes() || undefined,
      queen_seen: false,
      product: action === 'treatment' ? (label || 'Varroabehandlung') : undefined,
      feed_type: action === 'feeding' ? (label || 'Futter') : undefined,
      amount_kg_or_l: action === 'feeding' ? (amount ?? 0.1) : undefined,
      crop_type: action === 'harvest' ? (label || 'Honig') : undefined,
      amount_kg: action === 'harvest' ? (amount ?? 0) : undefined
    };
    this.apiaryService.createBatchAction(this.apiaryId, action, payload).subscribe({
      next: result => {
        this.batchMessage.set(`${result.created} Einträge angelegt.`);
        this.batchSaving.set(false);
      },
      error: () => {
        this.batchMessage.set('Sammelaktion konnte nicht gespeichert werden.');
        this.batchSaving.set(false);
      }
    });
  }
}
