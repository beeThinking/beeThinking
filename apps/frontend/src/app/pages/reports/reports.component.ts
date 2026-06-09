import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { BeekeepingService } from '../../core/services/beekeeping.service';

type Row = Record<string, string | number | null>;

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [DecimalPipe, FormsModule],
  templateUrl: './reports.component.html',
  styleUrl: './reports.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ReportsComponent {
  private readonly beekeeping = inject(BeekeepingService);
  protected readonly fromDate = signal(new Date(new Date().getFullYear(), 0, 1).toISOString().slice(0, 10));
  protected readonly toDate = signal(new Date().toISOString().slice(0, 10));
  protected readonly harvestByCrop = signal<Row[]>([]);
  protected readonly harvestByApiary = signal<Row[]>([]);
  protected readonly varroa = signal<Row[]>([]);
  protected readonly feedings = signal<Row[]>([]);

  constructor() { this.load(); }

  protected load(): void {
    const from = this.fromDate();
    const to = this.toDate();
    this.beekeeping.getReport<Row>('harvest-by-crop', from, to).subscribe(rows => this.harvestByCrop.set(rows));
    this.beekeeping.getReport<Row>('harvest-by-apiary', from, to).subscribe(rows => this.harvestByApiary.set(rows));
    this.beekeeping.getReport<Row>('varroa', from, to).subscribe(rows => this.varroa.set(rows));
    this.beekeeping.getReport<Row>('feedings', from, to).subscribe(rows => this.feedings.set(rows));
  }
}
