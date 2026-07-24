import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { DatePipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { BeekeepingService } from '../../core/services/beekeeping.service';
import { InspectionService } from '../../core/services/inspection.service';
import { InspectionCriterion } from '../../core/models/inspection.models';
import { CriterionWeight } from '../../core/models/breeding.models';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';

@Component({
  selector: 'app-zucht-selektion',
  standalone: true,
  imports: [DatePipe, DecimalPipe, FormsModule, TranslatePipe],
  templateUrl: './zucht-selektion.component.html',
  styleUrl: './zucht-selektion.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ZuchtSelektionComponent {
  private readonly beekeeping = inject(BeekeepingService);
  private readonly inspectionService = inject(InspectionService);
  private readonly translation = inject(TranslationService);

  private readonly candidatesData = toSignal(this.beekeeping.getBreedingCandidates(), { initialValue: [] });
  protected readonly candidates = computed(() =>
    [...this.candidatesData()].sort((a, b) => b.score - a.score)
  );
  protected readonly errorMessage = signal('');

  protected readonly showWeights = signal(false);
  private readonly criteriaData = toSignal(this.inspectionService.getCriteria(), { initialValue: [] });
  protected readonly localCriteria = signal<InspectionCriterion[] | null>(null);
  protected readonly criteria = computed(() => this.localCriteria() ?? this.criteriaData());
  protected readonly scorableCriteria = computed(() =>
    this.criteria().filter(criterion => criterion.value_type !== 'text')
  );
  private readonly weightsData = toSignal(this.beekeeping.getCriterionWeights(), { initialValue: [] });
  protected readonly localWeights = signal<CriterionWeight[] | null>(null);
  protected readonly weights = computed(() => this.localWeights() ?? this.weightsData());

  protected weightFor(criterionId: number): number {
    return this.weights().find(w => w.criterion_id === criterionId)?.weight ?? 1;
  }

  protected setWeight(criterion: InspectionCriterion, value: number): void {
    this.beekeeping.upsertCriterionWeight({ criterion_id: criterion.id, weight: value }).subscribe({
      next: updated => {
        this.localWeights.update(list => {
          const source = list ?? this.weightsData();
          const exists = source.some(w => w.criterion_id === updated.criterion_id);
          return exists
            ? source.map(w => w.criterion_id === updated.criterion_id ? updated : w)
            : [...source, updated];
        });
      },
      error: () => this.errorMessage.set(this.translation.t('zuchtSelektion.error.weight'))
    });
  }

  protected optionScore(criterion: InspectionCriterion, option: string): number {
    return criterion.option_scores?.[option] ?? 0;
  }

  protected setOptionScore(criterion: InspectionCriterion, option: string, value: number): void {
    const optionScores = { ...(criterion.option_scores ?? {}), [option]: value };
    this.inspectionService.updateCriterion(criterion.id, { option_scores: optionScores }).subscribe({
      next: updated => {
        this.localCriteria.update(list => (list ?? this.criteriaData()).map(c => c.id === updated.id ? updated : c));
      },
      error: () => this.errorMessage.set(this.translation.t('zuchtSelektion.error.optionScore'))
    });
  }
}
