import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { BeekeepingService } from '../../core/services/beekeeping.service';
import { ApiaryService } from '../../core/services/apiary.service';
import { HiveService } from '../../core/services/hive.service';
import { BreedingStep, BreedingStepName, Zuchtreihe } from '../../core/models/breeding.models';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { TranslationKey } from '../../core/i18n/en';

const STEP_LABEL_KEYS: Record<BreedingStepName, TranslationKey> = {
  pflegevolk_vorbereiten: 'zuchtreiheDetail.step.pflegevolk_vorbereiten',
  umlarven: 'zuchtreiheDetail.step.umlarven',
  annahmekontrolle: 'zuchtreiheDetail.step.annahmekontrolle',
  kaefigen_1: 'zuchtreiheDetail.step.kaefigen_1',
  kaefigen_2: 'zuchtreiheDetail.step.kaefigen_2',
  schlupf: 'zuchtreiheDetail.step.schlupf',
  voelkchen_bilden: 'zuchtreiheDetail.step.voelkchen_bilden',
  belegstelle: 'zuchtreiheDetail.step.belegstelle',
  abholen: 'zuchtreiheDetail.step.abholen'
};

@Component({
  selector: 'app-zuchtreihe-detail',
  standalone: true,
  imports: [FormsModule, RouterLink, TranslatePipe],
  templateUrl: './zuchtreihe-detail.component.html',
  styleUrl: './zuchtreihe-detail.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ZuchtreiheDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly beekeeping = inject(BeekeepingService);
  private readonly apiaryService = inject(ApiaryService);
  private readonly hiveService = inject(HiveService);
  private readonly translation = inject(TranslationService);

  protected readonly zuchtreiheId = Number(this.route.snapshot.paramMap.get('id'));
  protected readonly apiaries = toSignal(this.apiaryService.getApiaries(), { initialValue: [] });
  protected readonly hives = toSignal(this.hiveService.getHives(), { initialValue: [] });
  protected readonly zuchtreihe = signal<Zuchtreihe | null>(null);
  protected readonly errorMessage = signal('');
  protected readonly generating = signal(false);
  protected readonly umlarvenDate = signal('');
  protected readonly editingStepId = signal<number | null>(null);
  protected readonly editDate = signal('');
  protected readonly editNotes = signal('');

  protected readonly sortedSteps = computed(() => {
    const steps = this.zuchtreihe()?.steps ?? [];
    return [...steps].sort((a, b) => a.date.localeCompare(b.date));
  });

  constructor() {
    this.load();
  }

  private load(): void {
    this.beekeeping.getZuchtreihe(this.zuchtreiheId).subscribe({
      next: zuchtreihe => this.zuchtreihe.set(zuchtreihe),
      error: () => this.errorMessage.set(this.translation.t('zuchtreiheDetail.error.load'))
    });
  }

  protected stepLabel(name: BreedingStepName): string {
    return this.translation.t(STEP_LABEL_KEYS[name]);
  }

  protected apiaryName(apiaryId: number): string {
    const apiary = this.apiaries().find(a => a.id === apiaryId);
    return apiary ? (apiary.name?.trim() || apiary.stock_number) : this.translation.t('zuchtreihen.apiaryRef', { id: apiaryId });
  }

  protected hiveName(hiveId: number | null): string {
    if (!hiveId) return '–';
    return this.hives().find(h => h.id === hiveId)?.name ?? this.translation.t('zuchtreihen.hiveRef', { id: hiveId });
  }

  protected successRate(value: number | null): string {
    return value !== null ? `${value.toFixed(0)}%` : '–';
  }

  protected generateSteps(): void {
    if (!this.umlarvenDate() || this.generating()) return;
    this.generating.set(true);
    this.errorMessage.set('');
    this.beekeeping.generateBreedingSteps(this.zuchtreiheId, this.umlarvenDate()).subscribe({
      next: steps => {
        this.zuchtreihe.update(z => z ? { ...z, steps } : z);
        this.generating.set(false);
      },
      error: () => {
        this.errorMessage.set(this.translation.t('zuchtreiheDetail.error.generate'));
        this.generating.set(false);
      }
    });
  }

  protected openStepEdit(step: BreedingStep): void {
    this.editingStepId.set(step.id);
    this.editDate.set(step.date);
    this.editNotes.set(step.notes ?? '');
  }

  protected closeStepEdit(): void {
    this.editingStepId.set(null);
  }

  protected saveStep(): void {
    const stepId = this.editingStepId();
    if (!stepId) return;
    this.beekeeping.updateBreedingStep(this.zuchtreiheId, stepId, {
      date: this.editDate(),
      notes: this.editNotes() || null
    }).subscribe({
      next: updated => {
        this.zuchtreihe.update(z => z ? { ...z, steps: z.steps.map(s => s.id === updated.id ? updated : s) } : z);
        this.editingStepId.set(null);
      },
      error: () => this.errorMessage.set(this.translation.t('zuchtreiheDetail.error.updateStep'))
    });
  }
}
