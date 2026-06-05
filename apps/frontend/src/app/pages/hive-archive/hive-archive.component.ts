import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { HiveStatus } from '../../core/models/hive.models';
import { HiveService } from '../../core/services/hive.service';

@Component({
  selector: 'app-hive-archive',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './hive-archive.component.html',
  styleUrl: './hive-archive.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HiveArchiveComponent {
  private readonly hiveService = inject(HiveService);

  protected readonly archivedHives = toSignal(this.hiveService.getHives('archived'), { initialValue: [] });
  protected readonly grouped = computed(() => this.archivedHives());

  protected statusLabel(status: HiveStatus): string {
    return {
      active: 'Aktiv',
      archived: 'Archiviert',
      dissolved: 'Aufgelöst',
      merged: 'Vereinigt',
      sold: 'Verkauft',
      dead: 'Tot',
      inactive: 'Inaktiv',
      lost: 'Verloren',
      created_by_mistake: 'Fehleingabe'
    }[status];
  }
}
