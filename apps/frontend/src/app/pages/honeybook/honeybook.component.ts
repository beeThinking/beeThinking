import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { toSignal } from '@angular/core/rxjs-interop';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HoneybookEntry } from '../../core/models/beekeeping.models';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';

@Component({
  selector: 'app-honeybook',
  standalone: true,
  imports: [DatePipe, DecimalPipe, FormsModule, TranslatePipe],
  templateUrl: './honeybook.component.html',
  styleUrl: './honeybook.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HoneybookComponent {
  private readonly beekeeping = inject(BeekeepingService);
  protected readonly translation = inject(TranslationService);

  protected readonly years = computed(() => {
    const current = new Date().getFullYear();
    return Array.from({ length: 8 }, (_, index) => current - index);
  });

  protected readonly year = signal(new Date().getFullYear());
  protected readonly errorMessage = signal('');
  protected readonly exportPending = signal(false);

  private readonly remoteEntries = toSignal(this.beekeeping.getHoneybookRegister(this.year()), {
    initialValue: [] as HoneybookEntry[]
  });
  private readonly localEntries = signal<HoneybookEntry[] | null>(null);
  protected readonly entries = computed(() => this.localEntries() ?? this.remoteEntries());

  protected setYear(value: string): void {
    this.year.set(Number(value));
    this.load();
  }

  protected load(): void {
    this.errorMessage.set('');
    this.beekeeping.getHoneybookRegister(this.year()).subscribe({
      next: entries => this.localEntries.set(entries),
      error: () => this.errorMessage.set(this.translation.t('honeybook.error.load'))
    });
  }

  protected downloadPdf(): void {
    if (this.exportPending()) return;
    this.exportPending.set(true);
    this.errorMessage.set('');
    this.beekeeping.downloadHoneybookPdf(this.year()).subscribe({
      next: blob => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `honigbuch-${this.year()}.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 0);
        this.exportPending.set(false);
      },
      error: () => {
        this.errorMessage.set(this.translation.t('honeybook.error.download'));
        this.exportPending.set(false);
      }
    });
  }
}
