import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
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
  imports: [DecimalPipe, RouterLink, ApiaryMapPickerComponent, TranslatePipe],
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
}
