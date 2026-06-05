import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { map, switchMap } from 'rxjs';
import { ApiaryService } from '../../core/services/apiary.service';
import { HiveService } from '../../core/services/hive.service';

@Component({
  selector: 'app-apiary-detail',
  standalone: true,
  imports: [DecimalPipe, RouterLink],
  templateUrl: './apiary-detail.component.html',
  styleUrl: './apiary-detail.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ApiaryDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly apiaryService = inject(ApiaryService);
  private readonly hiveService = inject(HiveService);

  protected readonly apiaryId = Number(this.route.snapshot.paramMap.get('id'));
  protected readonly apiary = toSignal(
    this.route.paramMap.pipe(map(params => Number(params.get('id'))), switchMap(id => this.apiaryService.getApiary(id))),
    { initialValue: null }
  );
  protected readonly hives = toSignal(this.hiveService.getHives(), { initialValue: [] });
  protected readonly apiaryHives = computed(() => this.hives().filter(hive => hive.apiary_id === this.apiaryId));
}
