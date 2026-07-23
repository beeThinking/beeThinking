import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { TraceabilityResponse } from '../../core/models/beekeeping.models';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';

@Component({
  selector: 'app-traceability',
  standalone: true,
  imports: [DatePipe, DecimalPipe, FormsModule, TranslatePipe],
  templateUrl: './traceability.component.html',
  styleUrl: './traceability.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class TraceabilityComponent {
  private readonly beekeeping = inject(BeekeepingService);
  protected readonly translation = inject(TranslationService);

  protected readonly lotNumber = signal('');
  protected readonly loading = signal(false);
  protected readonly notFound = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly result = signal<TraceabilityResponse | null>(null);

  protected search(): void {
    const lot = this.lotNumber().trim();
    if (!lot) return;

    this.loading.set(true);
    this.notFound.set(false);
    this.errorMessage.set('');
    this.result.set(null);

    this.beekeeping.getTraceability(lot).subscribe({
      next: response => {
        this.loading.set(false);
        if (response === null) {
          this.notFound.set(true);
        } else {
          this.result.set(response);
        }
      },
      error: () => {
        this.loading.set(false);
        this.errorMessage.set(this.translation.t('traceability.error.load'));
      }
    });
  }
}
