import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Observable } from 'rxjs';

import { BeekeepingService } from '../../core/services/beekeeping.service';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';

type Row = Record<string, string | number | null>;

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [DecimalPipe, FormsModule, TranslatePipe],
  templateUrl: './reports.component.html',
  styleUrl: './reports.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ReportsComponent {
  private readonly beekeeping = inject(BeekeepingService);
  protected readonly translation = inject(TranslationService);
  protected readonly fromDate = signal(this.localDate(new Date(new Date().getFullYear(), 0, 1)));
  protected readonly toDate = signal(this.localDate(new Date()));
  protected readonly harvestByCrop = signal<Row[]>([]);
  protected readonly harvestByApiary = signal<Row[]>([]);
  protected readonly varroa = signal<Row[]>([]);
  protected readonly feedings = signal<Row[]>([]);
  protected readonly errorMessage = signal('');
  protected readonly exportPending = signal<'material' | 'finished-goods' | 'feedings' | null>(null);

  constructor() { this.load(); }

  private localDate(value: Date): string {
    const year = value.getFullYear();
    const month = String(value.getMonth() + 1).padStart(2, '0');
    const day = String(value.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  protected load(): void {
    const from = this.fromDate();
    const to = this.toDate();
    this.beekeeping.getReport<Row>('harvest-by-crop', from, to).subscribe(rows => this.harvestByCrop.set(rows));
    this.beekeeping.getReport<Row>('harvest-by-apiary', from, to).subscribe(rows => this.harvestByApiary.set(rows));
    this.beekeeping.getReport<Row>('varroa', from, to).subscribe(rows => this.varroa.set(rows));
    this.beekeeping.getReport<Row>('feedings', from, to).subscribe(rows => this.feedings.set(rows));
  }

  protected downloadInventoryMaterialPdf(): void {
    this.download('material', () => this.beekeeping.downloadInventoryMaterialPdf(), 'bestand-materiallager.pdf');
  }

  protected downloadInventoryFinishedGoodsPdf(): void {
    this.download('finished-goods', () => this.beekeeping.downloadInventoryFinishedGoodsPdf(), 'bestand-fertigprodukte.pdf');
  }

  protected downloadFeedingsPdf(): void {
    this.download(
      'feedings',
      () => this.beekeeping.downloadFeedingsPdf(this.fromDate(), this.toDate()),
      'fuetterungs-report.pdf'
    );
  }

  private download(kind: 'material' | 'finished-goods' | 'feedings', request: () => Observable<Blob>, filename: string): void {
    if (this.exportPending()) return;
    this.exportPending.set(kind);
    this.errorMessage.set('');
    request().subscribe({
      next: blob => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 0);
        this.exportPending.set(null);
      },
      error: () => {
        this.errorMessage.set(this.translation.t('reports.error.download'));
        this.exportPending.set(null);
      }
    });
  }
}
