import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { CurrencyPipe, DatePipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { BeekeepingService } from '../../core/services/beekeeping.service';
import { InventoryItem, OfficePartner, Sale, SaleItemCreate } from '../../core/models/beekeeping.models';

interface DraftLine {
  inventory_item_id: number | null;
  quantity: number;
  unit_price_gross: number;
}

@Component({
  selector: 'app-sales',
  standalone: true,
  imports: [CurrencyPipe, DatePipe, DecimalPipe, FormsModule, RouterLink],
  templateUrl: './sales.component.html',
  styleUrl: './sales.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class SalesComponent {
  private readonly beekeeping = inject(BeekeepingService);

  protected readonly sales = signal<Sale[]>([]);
  protected readonly items = signal<InventoryItem[]>([]);
  protected readonly customers = signal<OfficePartner[]>([]);
  protected readonly errorMessage = signal('');
  protected readonly saving = signal(false);
  protected readonly downloadPending = signal(false);

  protected readonly saleDate = signal(this.localDate(new Date()));
  protected readonly partnerId = signal<number | null>(null);
  protected readonly vatRateOverride = signal<number | null>(null);
  protected readonly notes = signal('');
  protected readonly lines = signal<DraftLine[]>([{ inventory_item_id: null, quantity: 1, unit_price_gross: 0 }]);

  protected readonly total = computed(() =>
    this.lines().reduce((sum, line) => sum + (line.quantity || 0) * (line.unit_price_gross || 0), 0)
  );

  constructor() {
    this.load();
  }

  protected load(): void {
    forkJoin({
      sales: this.beekeeping.getSales(),
      items: this.beekeeping.getInventoryItems(),
      customers: this.beekeeping.getOfficePartners('customer')
    }).subscribe({
      next: result => {
        this.sales.set(result.sales);
        this.items.set(result.items);
        this.customers.set(result.customers);
      },
      error: () => this.errorMessage.set('Verkäufe konnten nicht geladen werden.')
    });
  }

  protected addLine(): void {
    this.lines.update(lines => [...lines, { inventory_item_id: null, quantity: 1, unit_price_gross: 0 }]);
  }

  protected removeLine(index: number): void {
    this.lines.update(lines => lines.filter((_, i) => i !== index));
  }

  protected updateLine(index: number, patch: Partial<DraftLine>): void {
    this.lines.update(lines => lines.map((line, i) => (i === index ? { ...line, ...patch } : line)));
  }

  protected onItemSelected(index: number, itemId: number): void {
    const item = this.items().find(candidate => candidate.id === itemId);
    this.updateLine(index, { inventory_item_id: itemId, unit_price_gross: item?.price ?? 0 });
  }

  protected submit(): void {
    const items: SaleItemCreate[] = this.lines()
      .filter(line => line.inventory_item_id && line.quantity > 0)
      .map(line => ({
        inventory_item_id: line.inventory_item_id!,
        quantity: line.quantity,
        unit_price_gross: line.unit_price_gross
      }));
    if (items.length === 0) {
      this.errorMessage.set('Bitte mindestens eine Position auswählen.');
      return;
    }
    this.saving.set(true);
    this.errorMessage.set('');
    this.beekeeping.createSale({
      partner_id: this.partnerId(),
      sale_date: this.saleDate(),
      vat_rate: this.vatRateOverride() != null ? this.vatRateOverride()! / 100 : undefined,
      notes: this.notes() || undefined,
      items
    }).subscribe({
      next: () => {
        this.saving.set(false);
        this.resetForm();
        this.load();
      },
      error: () => {
        this.saving.set(false);
        this.errorMessage.set('Verkauf konnte nicht angelegt werden.');
      }
    });
  }

  protected voidSale(sale: Sale): void {
    if (!confirm('Diesen Verkauf stornieren? Der Bestand wird wieder eingebucht.')) return;
    this.beekeeping.deleteSale(sale.id).subscribe({
      next: () => this.load(),
      error: () => this.errorMessage.set('Verkauf konnte nicht storniert werden.')
    });
  }

  protected downloadCustomerListPdf(): void {
    if (this.downloadPending()) return;
    this.downloadPending.set(true);
    this.errorMessage.set('');
    this.beekeeping.downloadCustomerListPdf().subscribe({
      next: blob => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'kundenliste-qr.pdf';
        document.body.appendChild(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 0);
        this.downloadPending.set(false);
      },
      error: () => {
        this.errorMessage.set('Kundenliste konnte nicht heruntergeladen werden.');
        this.downloadPending.set(false);
      }
    });
  }

  protected itemName(inventoryItemId: number): string {
    return this.items().find(item => item.id === inventoryItemId)?.article.name ?? `Artikel #${inventoryItemId}`;
  }

  protected partnerName(id: number | null): string {
    if (!id) return 'Ohne Kunde';
    return this.customers().find(partner => partner.id === id)?.name ?? `Kunde #${id}`;
  }

  private resetForm(): void {
    this.saleDate.set(this.localDate(new Date()));
    this.partnerId.set(null);
    this.vatRateOverride.set(null);
    this.notes.set('');
    this.lines.set([{ inventory_item_id: null, quantity: 1, unit_price_gross: 0 }]);
  }

  private localDate(value: Date): string {
    const year = value.getFullYear();
    const month = String(value.getMonth() + 1).padStart(2, '0');
    const day = String(value.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
}
