import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
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
  imports: [RouterLink, TranslatePipe],
  templateUrl: './hive-archive.component.html',
  styleUrl: './hive-archive.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HiveArchiveComponent {
  private readonly hiveService = inject(HiveService);
  private readonly translation = inject(TranslationService);

  protected readonly archivedHives = toSignal(this.hiveService.getHives('archived'), { initialValue: [] });
  protected readonly grouped = computed(() => this.archivedHives());

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
