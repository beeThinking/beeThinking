import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { toSignal } from '@angular/core/rxjs-interop';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { Batch, BottleItem, Harvest, InventoryItem } from '../../core/models/beekeeping.models';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { localDateString } from '../../core/utils/date.utils';

let bottlingRowId = 0;

interface BottlingRow {
  id: number;
  articleId: number | null;
  quantity: number | null;
  price: number | null;
  bestBefore: string;
}

function createBottlingRow(articleId: number | null): BottlingRow {
  return { id: ++bottlingRowId, articleId, quantity: null, price: null, bestBefore: '' };
}

function addMonths(dateStr: string, months: number): string {
  const [year, month, day] = dateStr.split('-').map(Number);
  const monthIndex = month - 1 + months;
  const targetYear = year + Math.floor(monthIndex / 12);
  const targetMonth = ((monthIndex % 12) + 12) % 12;
  const lastDay = new Date(targetYear, targetMonth + 1, 0).getDate();
  const targetDay = Math.min(day, lastDay);
  return `${targetYear}-${String(targetMonth + 1).padStart(2, '0')}-${String(targetDay).padStart(2, '0')}`;
}

@Component({
  selector: 'app-batches',
  standalone: true,
  imports: [DatePipe, DecimalPipe, FormsModule, TranslatePipe],
  templateUrl: './batches.component.html',
  styleUrl: './batches.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class BatchesComponent {
  private readonly beekeeping = inject(BeekeepingService);
  protected readonly translation = inject(TranslationService);

  private readonly remoteBatches = toSignal(this.beekeeping.getBatches(), { initialValue: [] });
  private readonly localBatches = signal<Batch[] | null>(null);
  protected readonly batches = computed(() => this.localBatches() ?? this.remoteBatches());

  private readonly remoteHarvests = toSignal(this.beekeeping.getHarvests(), { initialValue: [] });
  private readonly localHarvests = signal<Harvest[] | null>(null);
  protected readonly harvests = computed(() => this.localHarvests() ?? this.remoteHarvests());
  protected readonly unbatchedHarvests = computed(() => this.harvests().filter(h => h.batch_id === null));

  protected readonly showForm = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly selectedHarvestIds = signal<number[]>([]);
  protected readonly bestBefore = signal('');
  protected readonly notes = signal('');
  protected readonly expandedBatchId = signal<number | null>(null);
  protected readonly attachHarvestId = signal<number | null>(null);
  protected readonly editingBestBefore = signal('');
  protected readonly editingNotes = signal('');

  private readonly remoteArticles = toSignal(this.beekeeping.getArticles(), { initialValue: [] });
  protected readonly articles = computed(() => this.remoteArticles());

  protected readonly bottlingRows = signal<BottlingRow[]>([]);
  protected readonly bottlingError = signal('');
  protected readonly bottlingResult = signal<InventoryItem[] | null>(null);

  protected readonly suggestedBestBefore = computed(() => {
    const ids = this.selectedHarvestIds();
    const dates = this.harvests().filter(h => ids.includes(h.id)).map(h => h.harvest_date);
    if (!dates.length) return '';
    const earliest = dates.reduce((min, current) => (current < min ? current : min));
    return addMonths(earliest, 24);
  });

  protected toggleHarvestSelection(id: number, checked: boolean): void {
    this.selectedHarvestIds.update(ids => checked ? [...new Set([...ids, id])] : ids.filter(existing => existing !== id));
    if (!this.bestBefore()) {
      this.bestBefore.set(this.suggestedBestBefore());
    }
  }

  protected openForm(): void {
    this.showForm.set(true);
    this.selectedHarvestIds.set([]);
    this.bestBefore.set('');
    this.notes.set('');
    this.errorMessage.set('');
  }

  protected closeForm(): void {
    this.showForm.set(false);
  }

  protected createBatch(): void {
    const harvestIds = this.selectedHarvestIds();
    const bestBefore = this.bestBefore() || this.suggestedBestBefore() || undefined;
    const payload = {
      harvest_ids: harvestIds,
      best_before: bestBefore,
      notes: this.notes().trim() || undefined
    };
    this.beekeeping.createBatch(payload).subscribe({
      next: batch => {
        this.localBatches.update(list => [batch, ...(list ?? this.remoteBatches())]);
        this.localHarvests.update(list => {
          const source = list ?? this.remoteHarvests();
          return source.map(h => harvestIds.includes(h.id) ? { ...h, batch_id: batch.id } : h);
        });
        this.showForm.set(false);
      },
      error: () => this.errorMessage.set(this.translation.t('batches.error.save'))
    });
  }

  protected toggleExpand(batch: Batch): void {
    if (this.expandedBatchId() === batch.id) {
      this.expandedBatchId.set(null);
      return;
    }
    this.expandedBatchId.set(batch.id);
    this.editingBestBefore.set(batch.best_before ?? '');
    this.editingNotes.set(batch.notes ?? '');
    this.attachHarvestId.set(null);
    this.bottlingRows.set([]);
    this.bottlingError.set('');
    this.bottlingResult.set(null);
  }

  protected saveBatch(batch: Batch): void {
    const payload = {
      best_before: this.editingBestBefore() || null,
      notes: this.editingNotes().trim() || undefined
    };
    this.beekeeping.updateBatch(batch.id, payload).subscribe({
      next: updated => this.replaceBatch(updated),
      error: () => this.errorMessage.set(this.translation.t('batches.error.save'))
    });
  }

  protected deleteBatch(batch: Batch): void {
    if (!confirm(this.translation.t('batches.delete.confirm'))) return;
    this.beekeeping.deleteBatch(batch.id).subscribe({
      next: () => {
        this.localBatches.update(list => (list ?? this.remoteBatches()).filter(b => b.id !== batch.id));
        this.localHarvests.update(list => {
          const source = list ?? this.remoteHarvests();
          return source.map(h => h.batch_id === batch.id ? { ...h, batch_id: null } : h);
        });
        if (this.expandedBatchId() === batch.id) this.expandedBatchId.set(null);
      },
      error: () => this.errorMessage.set(this.translation.t('batches.error.delete'))
    });
  }

  protected attachHarvest(batch: Batch): void {
    const harvestId = this.attachHarvestId();
    if (!harvestId) return;
    this.beekeeping.attachHarvestToBatch(batch.id, harvestId).subscribe({
      next: updated => {
        this.replaceBatch(updated);
        this.localHarvests.update(list => {
          const source = list ?? this.remoteHarvests();
          return source.map(h => h.id === harvestId ? { ...h, batch_id: batch.id } : h);
        });
        this.attachHarvestId.set(null);
      },
      error: () => this.errorMessage.set(this.translation.t('batches.error.attach'))
    });
  }

  protected detachHarvest(batch: Batch, harvestId: number): void {
    this.beekeeping.detachHarvestFromBatch(batch.id, harvestId).subscribe({
      next: updated => {
        this.replaceBatch(updated);
        this.localHarvests.update(list => {
          const source = list ?? this.remoteHarvests();
          return source.map(h => h.id === harvestId ? { ...h, batch_id: null } : h);
        });
      },
      error: () => this.errorMessage.set(this.translation.t('batches.error.detach'))
    });
  }

  private replaceBatch(updated: Batch): void {
    this.localBatches.update(list => (list ?? this.remoteBatches()).map((b: Batch) => b.id === updated.id ? updated : b));
  }

  protected today(): string {
    return localDateString();
  }

  protected addBottlingRow(): void {
    const defaultArticleId = this.articles()[0]?.id ?? null;
    this.bottlingRows.update(rows => [...rows, createBottlingRow(defaultArticleId)]);
  }

  protected removeBottlingRow(rowId: number): void {
    this.bottlingRows.update(rows => rows.filter(row => row.id !== rowId));
  }

  protected updateBottlingRow(rowId: number, changes: Partial<BottlingRow>): void {
    this.bottlingRows.update(rows => rows.map(row => row.id === rowId ? { ...row, ...changes } : row));
  }

  protected submitBottling(batch: Batch): void {
    const rows = this.bottlingRows().filter(row => row.articleId !== null && row.quantity && row.quantity > 0);
    if (!rows.length) return;
    const items: BottleItem[] = rows.map(row => ({
      article_id: row.articleId as number,
      quantity: row.quantity as number,
      price: row.price ?? undefined,
      best_before: row.bestBefore || undefined
    }));
    this.bottlingError.set('');
    this.beekeeping.bottleBatch(batch.id, { items }).subscribe({
      next: response => {
        this.replaceBatch(response.batch);
        this.bottlingResult.set(response.inventory_items);
        this.bottlingRows.set([]);
      },
      error: (error: unknown) => {
        if (error instanceof HttpErrorResponse && error.status === 409) {
          this.bottlingError.set(this.translation.t('batches.bottling.error.exceeds'));
        } else {
          this.bottlingError.set(this.translation.t('batches.bottling.error.save'));
        }
      }
    });
  }
}
