import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { HiveStatus } from '../../core/models/hive.models';
import { HiveService } from '../../core/services/hive.service';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { TranslationKey } from '../../core/i18n/en';

@Component({
  selector: 'app-hive-archive',
  standalone: true,
  imports: [FormsModule, RouterLink, TranslatePipe],
  templateUrl: './hive-archive.component.html',
  styleUrl: './hive-archive.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HiveArchiveComponent {
  private readonly hiveService = inject(HiveService);
  private readonly translation = inject(TranslationService);

  protected readonly archivedHives = toSignal(this.hiveService.getHives('archived'), { initialValue: [] });
  protected readonly statusFilter = signal<HiveStatus | 'all'>('all');
  protected readonly filterOptions: (HiveStatus | 'all')[] = ['all', 'archived', 'dissolved', 'merged', 'sold', 'dead', 'lost'];
  protected readonly grouped = computed(() => {
    const filter = this.statusFilter();
    const hives = this.archivedHives();
    return filter === 'all' ? hives : hives.filter(hive => hive.status === filter);
  });

  protected filterLabel(status: HiveStatus | 'all'): string {
    return status === 'all' ? this.translation.t('archive.filter.all') : this.statusLabel(status);
  }

  protected statusLabel(status: HiveStatus): string {
    const key = ({
      active: 'beehives.status.active',
      archived: 'beehives.status.archived',
      dissolved: 'beehives.status.dissolved',
      merged: 'beehives.status.merged',
      sold: 'beehives.status.sold',
      dead: 'beehives.status.dead',
      inactive: 'beehives.status.inactive',
      lost: 'beehives.status.lost',
      created_by_mistake: 'beehives.status.created_by_mistake'
    } satisfies Record<HiveStatus, TranslationKey>)[status];
    return this.translation.t(key);
  }
}
