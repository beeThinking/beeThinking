import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { CalculatorsService } from '../../core/services/calculators.service';
import { FeedCalculatorColonyStrength, FeedCalculatorResponse, FeedCalculatorSeason } from '../../core/models/calculators.models';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { TranslationKey } from '../../core/i18n/en';

@Component({
  selector: 'app-feed-calculator',
  standalone: true,
  imports: [ReactiveFormsModule, TranslatePipe],
  templateUrl: './feed-calculator.component.html',
  styleUrl: './feed-calculator.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class FeedCalculatorComponent {
  private readonly calculators = inject(CalculatorsService);
  private readonly fb = inject(FormBuilder);
  private readonly translation = inject(TranslationService);

  protected readonly strengths: FeedCalculatorColonyStrength[] = ['weak', 'medium', 'strong'];
  protected readonly seasons: FeedCalculatorSeason[] = ['winter', 'spring_buildup', 'summer_gap'];

  protected readonly result = signal<FeedCalculatorResponse | null>(null);
  protected readonly errorMessage = signal('');
  protected readonly loading = signal(false);

  protected readonly form = this.fb.group({
    colony_count: [1, [Validators.required, Validators.min(1), Validators.max(1000)]],
    colony_strength: ['medium' as FeedCalculatorColonyStrength],
    season: ['winter' as FeedCalculatorSeason]
  });

  protected calculate(): void {
    if (this.form.invalid) return;
    const value = this.form.getRawValue();
    this.loading.set(true);
    this.errorMessage.set('');
    this.calculators.calculateFeed({
      colony_count: Number(value.colony_count),
      colony_strength: value.colony_strength as FeedCalculatorColonyStrength,
      season: value.season as FeedCalculatorSeason
    }).subscribe({
      next: response => {
        this.result.set(response);
        this.loading.set(false);
      },
      error: () => {
        this.errorMessage.set(this.translation.t('feedCalculator.error'));
        this.loading.set(false);
      }
    });
  }

  protected strengthLabel(strength: FeedCalculatorColonyStrength): string {
    const key = ({
      weak: 'feedCalculator.strength.weak',
      medium: 'feedCalculator.strength.medium',
      strong: 'feedCalculator.strength.strong'
    } satisfies Record<FeedCalculatorColonyStrength, TranslationKey>)[strength];
    return this.translation.t(key);
  }

  protected seasonLabel(season: FeedCalculatorSeason): string {
    const key = ({
      winter: 'feedCalculator.season.winter',
      spring_buildup: 'feedCalculator.season.spring_buildup',
      summer_gap: 'feedCalculator.season.summer_gap'
    } satisfies Record<FeedCalculatorSeason, TranslationKey>)[season];
    return this.translation.t(key);
  }
}
