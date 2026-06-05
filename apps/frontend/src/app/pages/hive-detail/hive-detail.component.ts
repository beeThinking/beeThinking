import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { switchMap } from 'rxjs';
import { HiveService } from '../../core/services/hive.service';

@Component({
  selector: 'app-hive-detail',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './hive-detail.component.html',
  styleUrl: './hive-detail.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HiveDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly hiveService = inject(HiveService);
  private readonly hiveId = computed(() => Number(this.route.snapshot.paramMap.get('id')));

  protected readonly hive = toSignal(this.route.paramMap.pipe(
    switchMap(params => this.hiveService.getHive(Number(params.get('id'))))
  ));
  protected readonly timeline = toSignal(this.route.paramMap.pipe(
    switchMap(params => this.hiveService.getHiveTimeline(Number(params.get('id'))))
  ), { initialValue: [] });

  protected readonly inspectLink = computed(() => ['/beehives', this.hiveId(), 'inspect']);

  protected formatDate(value: string): string {
    return new Date(value).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
  }
}
