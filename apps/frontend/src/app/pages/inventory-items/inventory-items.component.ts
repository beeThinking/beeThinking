import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { Article, InventoryItem } from '../../core/models/beekeeping.models';
import { BeekeepingService } from '../../core/services/beekeeping.service';

@Component({
  selector: 'app-inventory-items',
  standalone: true,
  imports: [DecimalPipe, FormsModule],
  templateUrl: './inventory-items.component.html',
  styleUrl: '../inventory-shared.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class InventoryItemsComponent {
  private readonly beekeeping = inject(BeekeepingService);
  protected readonly articles = signal<Article[]>([]);
  protected readonly items = signal<InventoryItem[]>([]);
  protected readonly articleId = signal<number | null>(null);
  protected readonly quantity = signal(0);
  protected readonly unit = signal('piece');
  protected readonly price = signal<number | null>(null);
  protected readonly bestBefore = signal('');
  protected readonly batchCode = signal('');
  protected readonly message = signal('');
  protected readonly honeyTotal = computed(() =>
    this.items().filter(item => item.article.category === 'honey').reduce((sum, item) => sum + item.quantity, 0)
  );

  constructor() { this.load(); }

  protected load(): void {
    this.beekeeping.getArticles().subscribe(articles => {
      this.articles.set(articles);
      if (!this.articleId() && articles[0]) this.articleId.set(articles[0].id);
    });
    this.beekeeping.getInventoryItems().subscribe(items => this.items.set(items));
  }

  protected create(): void {
    const articleId = this.articleId();
    if (!articleId) return;
    this.beekeeping.createInventoryItem({
      article_id: articleId,
      quantity: this.quantity(),
      unit: this.unit(),
      price: this.price(),
      best_before: this.bestBefore() || null,
      batch_code: this.batchCode() || undefined
    }).subscribe({
      next: () => {
        this.message.set('Bestand angelegt.');
        this.load();
      },
      error: () => this.message.set('Bestand konnte nicht angelegt werden.')
    });
  }

  protected delete(item: InventoryItem): void {
    this.beekeeping.deleteInventoryItem(item.id).subscribe(() => this.load());
  }
}
