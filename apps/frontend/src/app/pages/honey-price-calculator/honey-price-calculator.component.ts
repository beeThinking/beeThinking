import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { CalculatorsService } from '../../core/services/calculators.service';
import { ApiaryService } from '../../core/services/apiary.service';
import { HoneyPriceCalculatorResponse } from '../../core/models/calculators.models';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';

@Component({
  selector: 'app-honey-price-calculator',
  standalone: true,
  imports: [ReactiveFormsModule, TranslatePipe],
  templateUrl: './honey-price-calculator.component.html',
  styleUrl: './honey-price-calculator.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HoneyPriceCalculatorComponent {
  private readonly calculators = inject(CalculatorsService);
  private readonly apiaryService = inject(ApiaryService);
  private readonly fb = inject(FormBuilder);
  private readonly translation = inject(TranslationService);

  protected readonly apiaries = toSignal(this.apiaryService.getApiaries(), { initialValue: [] });
  protected readonly result = signal<HoneyPriceCalculatorResponse | null>(null);
  protected readonly errorMessage = signal('');
  protected readonly loading = signal(false);

  protected readonly form = this.fb.group({
    apiary_id: [null as number | null, Validators.required],
    from_date: [''],
    to_date: [''],
    target_margin_percent: [0, [Validators.min(0), Validators.max(500)]]
  });

  protected apiaryTitle(apiary: { stock_number: string; name: string | null }): string {
    return apiary.name?.trim() || apiary.stock_number;
  }

  protected calculate(): void {
    if (this.form.invalid) return;
    const value = this.form.getRawValue();
    this.loading.set(true);
    this.errorMessage.set('');
    this.calculators.calculateHoneyPrice({
      apiary_id: Number(value.apiary_id),
      from_date: value.from_date || undefined,
      to_date: value.to_date || undefined,
      target_margin_percent: Number(value.target_margin_percent ?? 0)
    }).subscribe({
      next: response => {
        this.result.set(response);
        this.loading.set(false);
      },
      error: () => {
        this.errorMessage.set(this.translation.t('honeyPriceCalculator.error'));
        this.loading.set(false);
      }
    });
  }
}
