import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { map, switchMap } from 'rxjs';
import { VarroaTreatmentType, VarroaWeatherWindow } from '../../core/models/beekeeping.models';
import { ApiaryService } from '../../core/services/apiary.service';
import { HiveService } from '../../core/services/hive.service';

@Component({
  selector: 'app-apiary-detail',
  standalone: true,
  imports: [DecimalPipe, RouterLink],
  templateUrl: './apiary-detail.component.html',
  styleUrl: './apiary-detail.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ApiaryDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly apiaryService = inject(ApiaryService);
  private readonly hiveService = inject(HiveService);

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

  protected readonly treatmentOptions: { value: VarroaTreatmentType; label: string }[] = [
    { value: 'formic_acid_short', label: 'Ameisensäure kurz' },
    { value: 'formic_acid_long', label: 'Ameisensäure lang' },
    { value: 'thymol', label: 'Thymol' },
    { value: 'oxalic_acid_dribble', label: 'Oxalsäure träufeln' },
    { value: 'oxalic_acid_sublimation', label: 'Oxalsäure sublimieren' },
    { value: 'lactic_acid', label: 'Milchsäure' },
    { value: 'biotechnical', label: 'Biotechnisch' }
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
        this.weatherError.set('Wetterfenster konnten nicht geladen werden.');
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
        this.weatherError.set('Wetterdaten konnten nicht aktualisiert werden.');
        this.weatherLoading.set(false);
      }
    });
  }

  protected formatDate(value: string): string {
    return new Date(value).toLocaleDateString('de-DE', { weekday: 'short', day: '2-digit', month: '2-digit' });
  }

  protected ratingLabel(rating: string): string {
    return ({ suitable: 'geeignet', caution: 'kritisch', unsuitable: 'ungeeignet', unknown: 'keine Daten' } as Record<string, string>)[rating] ?? rating;
  }
}
