import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { HiveSelectionService } from '../../core/services/hive-selection.service';
import { InspectionService } from '../../core/services/inspection.service';
import { InspectionCriterion } from '../../core/models/inspection.models';
import { CriterionAverageFilter, HiveSelectionCandidate } from '../../core/models/hive-selection.models';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';

@Component({
  selector: 'app-hive-selection',
  standalone: true,
  imports: [DecimalPipe, FormsModule, TranslatePipe],
  templateUrl: './hive-selection.component.html',
  styleUrl: './hive-selection.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HiveSelectionComponent {
  private readonly hiveSelection = inject(HiveSelectionService);
  private readonly inspectionService = inject(InspectionService);
  private readonly translation = inject(TranslationService);

  private readonly allCriteria = toSignal(this.inspectionService.getCriteria(), { initialValue: [] });
  protected readonly averagedCriteria = computed<InspectionCriterion[]>(() =>
    this.allCriteria().filter(criterion => criterion.value_type === 'stars' || criterion.value_type === 'number')
  );

  protected readonly criterionMin = signal<Record<number, number | null>>({});
  protected readonly criterionMax = signal<Record<number, number | null>>({});
  protected readonly tagsInput = signal('');
  protected readonly matchAllTags = signal(false);

  protected readonly candidates = signal<HiveSelectionCandidate[]>([]);
  protected readonly loading = signal(false);
  protected readonly message = signal('');

  protected readonly selectedHiveIds = signal<Set<number>>(new Set());
  protected readonly batchTitle = signal('');
  protected readonly batchDescription = signal('');
  protected readonly batchDueDate = signal('');
  protected readonly showBatchForm = signal(false);

  protected setMin(criterionId: number, value: string): void {
    this.criterionMin.update(map => ({ ...map, [criterionId]: value === '' ? null : Number(value) }));
  }

  protected setMax(criterionId: number, value: string): void {
    this.criterionMax.update(map => ({ ...map, [criterionId]: value === '' ? null : Number(value) }));
  }

  protected search(): void {
    const criteria: CriterionAverageFilter[] = this.averagedCriteria()
      .map(criterion => ({
        criterion_id: criterion.id,
        min_average: this.criterionMin()[criterion.id] ?? null,
        max_average: this.criterionMax()[criterion.id] ?? null
      }))
      .filter(filter => filter.min_average !== null || filter.max_average !== null);

    const tags = this.tagsInput().split(',').map(tag => tag.trim()).filter(Boolean);

    this.loading.set(true);
    this.message.set('');
    this.hiveSelection.filterHives({ criteria, tags, match_all_tags: this.matchAllTags() }).subscribe({
      next: results => {
        this.candidates.set(results);
        this.selectedHiveIds.set(new Set());
        this.loading.set(false);
        if (!results.length) {
          this.message.set(this.translation.t('hiveSelection.empty'));
        }
      },
      error: () => {
        this.loading.set(false);
        this.message.set(this.translation.t('hiveSelection.error.search'));
      }
    });
  }

  protected toggleSelection(hiveId: number): void {
    this.selectedHiveIds.update(set => {
      const next = new Set(set);
      if (next.has(hiveId)) {
        next.delete(hiveId);
      } else {
        next.add(hiveId);
      }
      return next;
    });
  }

  protected isSelected(hiveId: number): boolean {
    return this.selectedHiveIds().has(hiveId);
  }

  protected selectAll(): void {
    this.selectedHiveIds.set(new Set(this.candidates().map(candidate => candidate.hive_id)));
  }

  protected clearSelection(): void {
    this.selectedHiveIds.set(new Set());
  }

  protected openBatchForm(): void {
    if (!this.selectedHiveIds().size) return;
    this.batchTitle.set('');
    this.batchDescription.set('');
    this.batchDueDate.set('');
    this.showBatchForm.set(true);
  }

  protected closeBatchForm(): void {
    this.showBatchForm.set(false);
  }

  protected createBatchTasks(): void {
    const hiveIds = Array.from(this.selectedHiveIds());
    if (!hiveIds.length || !this.batchTitle().trim()) return;
    this.hiveSelection.batchCreateTasks({
      hive_ids: hiveIds,
      title: this.batchTitle().trim(),
      description: this.batchDescription().trim() || undefined,
      due_date: this.batchDueDate() || undefined
    }).subscribe({
      next: result => {
        this.message.set(this.translation.t('hiveSelection.batch.success', { count: result.created_task_ids.length }));
        this.showBatchForm.set(false);
        this.selectedHiveIds.set(new Set());
      },
      error: () => this.message.set(this.translation.t('hiveSelection.batch.error'))
    });
  }

  protected criterionName(criterionId: number): string {
    return this.allCriteria().find(c => c.id === criterionId)?.name ?? String(criterionId);
  }

  protected averageEntries(candidate: HiveSelectionCandidate): { criterionId: number; average: number }[] {
    return Object.entries(candidate.criterion_averages).map(([id, average]) => ({ criterionId: Number(id), average }));
  }
}
