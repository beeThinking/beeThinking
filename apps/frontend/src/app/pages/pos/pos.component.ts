import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { CurrencyPipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { BeekeepingService } from '../../core/services/beekeeping.service';
import { InventoryItem, OfficePartner } from '../../core/models/beekeeping.models';

interface CartLine {
  inventory_item_id: number;
  name: string;
  quantity: number;
  unit_price_gross: number;
  available: number;
}

@Component({
  selector: 'app-pos',
  standalone: true,
  imports: [CurrencyPipe, DecimalPipe, FormsModule, RouterLink],
  templateUrl: './pos.component.html',
  styleUrl: './pos.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class PosComponent {
  private readonly beekeeping = inject(BeekeepingService);

  protected readonly items = signal<InventoryItem[]>([]);
  protected readonly customers = signal<OfficePartner[]>([]);
  protected readonly cart = signal<CartLine[]>([]);
  protected readonly partnerId = signal<number | null>(null);
  protected readonly cashGiven = signal<number | null>(null);
  protected readonly errorMessage = signal('');
  protected readonly successMessage = signal('');
  protected readonly submitting = signal(false);

  protected readonly availableItems = computed(() => this.items().filter(item => !item.archived && item.quantity > 0));

  protected readonly cartTotal = computed(() =>
    this.cart().reduce((sum, line) => sum + line.quantity * line.unit_price_gross, 0)
  );

  protected readonly changeDue = computed(() => {
    const given = this.cashGiven();
    if (given === null) return null;
    return Math.round((given - this.cartTotal()) * 100) / 100;
  });

  constructor() {
    this.load();
  }

  protected load(): void {
    forkJoin({
      items: this.beekeeping.getInventoryItems(),
      customers: this.beekeeping.getOfficePartners('customer')
    }).subscribe({
      next: result => {
        this.items.set(result.items);
        this.customers.set(result.customers);
      },
      error: () => this.errorMessage.set('Artikel konnten nicht geladen werden.')
    });
  }

  protected addToCart(item: InventoryItem): void {
    this.cart.update(lines => {
      const existing = lines.find(line => line.inventory_item_id === item.id);
      if (existing) {
        return lines.map(line =>
          line.inventory_item_id === item.id ? { ...line, quantity: Math.min(line.quantity + 1, line.available) } : line
        );
      }
      return [
        ...lines,
        {
          inventory_item_id: item.id,
          name: item.article.name,
          quantity: 1,
          unit_price_gross: item.price ?? 0,
          available: item.quantity
        }
      ];
    });
  }

  protected increment(inventoryItemId: number): void {
    this.cart.update(lines =>
      lines.map(line =>
        line.inventory_item_id === inventoryItemId ? { ...line, quantity: Math.min(line.quantity + 1, line.available) } : line
      )
    );
  }

  protected decrement(inventoryItemId: number): void {
    this.cart.update(lines =>
      lines
        .map(line => (line.inventory_item_id === inventoryItemId ? { ...line, quantity: line.quantity - 1 } : line))
        .filter(line => line.quantity > 0)
    );
  }

  protected removeLine(inventoryItemId: number): void {
    this.cart.update(lines => lines.filter(line => line.inventory_item_id !== inventoryItemId));
  }

  protected clearCart(): void {
    this.cart.set([]);
    this.cashGiven.set(null);
    this.successMessage.set('');
  }

  protected submit(): void {
    const cart = this.cart();
    if (cart.length === 0) return;
    this.submitting.set(true);
    this.errorMessage.set('');
    this.successMessage.set('');
    this.beekeeping.createSale({
      partner_id: this.partnerId(),
      items: cart.map(line => ({
        inventory_item_id: line.inventory_item_id,
        quantity: line.quantity,
        unit_price_gross: line.unit_price_gross
      }))
    }).subscribe({
      next: () => {
        this.submitting.set(false);
        this.successMessage.set('Verkauf gebucht.');
        this.cart.set([]);
        this.cashGiven.set(null);
        this.partnerId.set(null);
        this.load();
      },
      error: () => {
        this.submitting.set(false);
        this.errorMessage.set('Verkauf konnte nicht gebucht werden.');
      }
    });
  }
}
