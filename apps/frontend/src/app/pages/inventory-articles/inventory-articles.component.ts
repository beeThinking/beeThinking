import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { Article, ArticleCategory } from '../../core/models/beekeeping.models';
import { BeekeepingService } from '../../core/services/beekeeping.service';

@Component({
  selector: 'app-inventory-articles',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './inventory-articles.component.html',
  styleUrl: '../inventory-shared.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class InventoryArticlesComponent {
  private readonly beekeeping = inject(BeekeepingService);
  protected readonly articles = signal<Article[]>([]);
  protected readonly categories: ArticleCategory[] = ['honey', 'finished_product', 'feed', 'material'];
  protected readonly name = signal('');
  protected readonly category = signal<ArticleCategory>('honey');
  protected readonly sku = signal('');
  protected readonly unit = signal('piece');
  protected readonly weightKg = signal<number | null>(null);
  protected readonly message = signal('');

  constructor() { this.load(); }

  protected load(): void {
    this.beekeeping.getArticles().subscribe(articles => this.articles.set(articles));
  }

  protected create(): void {
    if (!this.name().trim()) return;
    this.beekeeping.createArticle({
      name: this.name().trim(),
      category: this.category(),
      sku: this.sku() || undefined,
      unit: this.unit() || 'piece',
      weight_kg: this.weightKg()
    }).subscribe({
      next: () => {
        this.name.set('');
        this.sku.set('');
        this.weightKg.set(null);
        this.message.set('Artikel angelegt.');
        this.load();
      },
      error: () => this.message.set('Artikel konnte nicht angelegt werden.')
    });
  }

  protected delete(article: Article): void {
    this.beekeeping.deleteArticle(article.id).subscribe(() => this.load());
  }
}
