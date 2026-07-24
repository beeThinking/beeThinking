import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  Input,
  OnChanges,
  OnDestroy,
  SimpleChanges,
  ViewChild,
  inject
} from '@angular/core';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { TranslationService } from '../../core/services/translation.service';
import { HiveAnalyticsChartPoint } from '../../core/models/hive-analytics.models';

import type { Chart, ChartConfiguration } from 'chart.js';

@Component({
  selector: 'app-hive-analytics-chart',
  imports: [TranslatePipe],
  templateUrl: './hive-analytics-chart.component.html',
  styleUrl: './hive-analytics-chart.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HiveAnalyticsChartComponent implements AfterViewInit, OnChanges, OnDestroy {
  private readonly translation = inject(TranslationService);

  @Input() points: HiveAnalyticsChartPoint[] = [];

  @ViewChild('canvas', { static: true }) private canvasRef?: ElementRef<HTMLCanvasElement>;

  private chart?: Chart;
  private isReady = false;
  protected loadError = '';

  async ngAfterViewInit(): Promise<void> {
    try {
      const chartModule = await import('chart.js/auto');
      const ChartCtor = chartModule.default;
      const config = this.buildConfig();
      this.chart = new ChartCtor(this.canvasRef!.nativeElement, config);
      this.isReady = true;
    } catch {
      this.loadError = this.translation.t('hiveAnalytics.chartLoadError');
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (!this.isReady || !this.chart || !changes['points']) return;
    const config = this.buildConfig();
    this.chart.data = config.data;
    this.chart.update();
  }

  ngOnDestroy(): void {
    this.chart?.destroy();
  }

  private buildConfig(): ChartConfiguration {
    return {
      type: 'bar',
      data: {
        labels: this.points.map(point => point.period_key),
        datasets: [
          {
            label: this.translation.t('hiveAnalytics.harvestKg'),
            data: this.points.map(point => point.harvest_kg),
            backgroundColor: '#c9822b'
          },
          {
            label: this.translation.t('hiveAnalytics.feedingLabel'),
            data: this.points.map(point => point.feeding_kg_or_l),
            backgroundColor: '#3977ad'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { beginAtZero: true } }
      }
    };
  }
}
