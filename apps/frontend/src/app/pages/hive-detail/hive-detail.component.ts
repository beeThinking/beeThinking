import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { catchError, combineLatest, forkJoin, map, of, startWith, Subject, switchMap } from 'rxjs';
import { PhotoWithPreview } from '../../core/models/beekeeping.models';
import { ColonyKind, HiveEvent, Queen } from '../../core/models/hive.models';
import { HiveStatus, HiveType } from '../../core/models/hive.models';
import { ApiaryService } from '../../core/services/apiary.service';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { PhotoQueueService } from '../../core/services/photo-queue.service';
import { HiveService } from '../../core/services/hive.service';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { TranslationKey } from '../../core/i18n/en';
import { localDateString } from '../../core/utils/date.utils';

@Component({
  selector: 'app-hive-detail',
  standalone: true,
  imports: [FormsModule, RouterLink, TranslatePipe],
  templateUrl: './hive-detail.component.html',
  styleUrl: './hive-detail.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HiveDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly beekeepingService = inject(BeekeepingService);
  private readonly hiveService = inject(HiveService);
  private readonly apiaryService = inject(ApiaryService);
  private readonly translation = inject(TranslationService);
  private readonly photoQueue = inject(PhotoQueueService);
  private readonly hiveId = computed(() => Number(this.route.snapshot.paramMap.get('id')));
  private readonly photoRefresh$ = new Subject<void>();
  private readonly queenRefresh$ = new Subject<void>();

  protected readonly hive = toSignal(this.route.paramMap.pipe(
    switchMap(params => this.hiveService.getHive(Number(params.get('id'))))
  ));
  protected readonly timeline = toSignal(this.route.paramMap.pipe(
    switchMap(params => this.hiveService.getHiveTimeline(Number(params.get('id'))))
  ), { initialValue: [] });
  protected readonly history = toSignal(this.route.paramMap.pipe(
    switchMap(params => this.hiveService.getHiveHistory(Number(params.get('id'))))
  ), { initialValue: [] as HiveEvent[] });
  protected readonly queens = toSignal(combineLatest([
    this.route.paramMap,
    this.queenRefresh$.pipe(startWith(undefined))
  ]).pipe(
    switchMap(([params]) => this.hiveService.getQueens(Number(params.get('id'))))
  ), { initialValue: [] as Queen[] });
  protected readonly apiaries = toSignal(this.apiaryService.getApiaries(), { initialValue: [] });
  protected readonly photos = toSignal(combineLatest([
    this.route.paramMap,
    this.photoRefresh$.pipe(startWith(undefined))
  ]).pipe(
    switchMap(([params]) => {
      const hiveId = Number(params.get('id'));
      return this.beekeepingService.getPhotos().pipe(
        map(photos => photos.filter(photo => photo.hive_id === hiveId)),
        switchMap(photos => photos.length
          ? forkJoin(photos.map(photo => this.beekeepingService.getPhotoPreview(photo.id).pipe(
              map(preview => ({ ...photo, preview_url: preview.url })),
              catchError(() => of({ ...photo, preview_url: null }))
            )))
          : of([] as PhotoWithPreview[])
        )
      );
    })
  ), { initialValue: [] });

  protected readonly activeQueen = computed(() => this.queens().find(queen => queen.is_active) ?? null);
  protected readonly moveTargets = computed(() =>
    this.apiaries().filter(apiary => apiary.id !== this.hive()?.apiary_id)
  );

  protected readonly inspectLink = computed(() => ['/hives', this.hiveId(), 'inspect']);
  protected readonly caption = signal('');
  protected readonly selectedFile = signal<File | null>(null);
  protected readonly uploadError = signal('');
  protected readonly uploadPending = signal(false);
  protected readonly lifecycleError = signal('');
  protected readonly lifecycleDate = signal(localDateString());
  protected readonly lifecycleNote = signal('');
  protected readonly mergeTargetId = signal<number | null>(null);
  protected readonly actionError = signal('');
  protected readonly moveTargetApiaryId = signal<number | null>(null);
  protected readonly copyName = signal('');
  protected readonly requeenYear = signal(new Date().getFullYear());
  protected readonly requeenColor = signal('');
  protected readonly requeenMarking = signal('');
  protected readonly requeenIntroducedAt = signal(localDateString());
  protected readonly requeenReason = signal('');
  protected readonly varroaMethod = signal('');
  protected readonly varroaMiteCount = signal<number | null>(null);
  protected readonly varroaPerDay = signal<number | null>(null);

  protected formatDate(value: string): string {
    return new Date(value).toLocaleDateString(this.translation.currentLang() === 'de' ? 'de-DE' : 'en-US', { day: '2-digit', month: '2-digit', year: 'numeric' });
  }

  protected formatBytes(value: number): string {
    if (value < 1024) {
      return `${value} B`;
    }
    if (value < 1024 * 1024) {
      return `${(value / 1024).toFixed(1)} KB`;
    }
    return `${(value / 1024 / 1024).toFixed(1)} MB`;
  }

  protected selectPhoto(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedFile.set(input.files?.[0] ?? null);
    this.uploadError.set('');
  }

  protected uploadPhoto(): void {
    const file = this.selectedFile();
    if (!file || this.uploadPending()) {
      return;
    }

    this.uploadPending.set(true);
    this.uploadError.set('');
    this.beekeepingService.uploadPhoto({
      file,
      hive_id: this.hiveId(),
      caption: this.caption()
    }).subscribe({
      next: () => {
        this.caption.set('');
        this.selectedFile.set(null);
        this.photoRefresh$.next();
        this.uploadPending.set(false);
      },
      error: () => {
        if (typeof navigator !== 'undefined' && !navigator.onLine) {
          this.photoQueue.enqueue(file, this.hiveId(), this.caption());
          this.caption.set('');
          this.selectedFile.set(null);
          this.uploadError.set(this.translation.t('offline.photoQueued'));
          this.uploadPending.set(false);
          return;
        }
        this.uploadError.set(this.translation.t('hiveDetail.error.upload'));
        this.uploadPending.set(false);
      }
    });
  }

  protected deletePhoto(photo: PhotoWithPreview): void {
    this.beekeepingService.deletePhoto(photo.id).subscribe({
      next: () => this.photoRefresh$.next(),
      error: () => this.uploadError.set(this.translation.t('hiveDetail.error.deletePhoto'))
    });
  }

  protected archiveHive(): void {
    this.hiveService.archiveHive(this.hiveId(), {
      reason: 'archived',
      date: this.lifecycleDate(),
      note: this.lifecycleNote() || undefined
    }).subscribe({
      next: () => window.location.reload(),
      error: () => this.lifecycleError.set(this.translation.t('hiveDetail.error.archive'))
    });
  }

  protected dissolveHive(reason: string): void {
    this.hiveService.dissolveHive(this.hiveId(), {
      reason,
      date: this.lifecycleDate(),
      note: this.lifecycleNote() || undefined
    }).subscribe({
      next: () => window.location.reload(),
      error: () => this.lifecycleError.set(this.translation.t('hiveDetail.error.dissolve'))
    });
  }

  protected mergeHive(): void {
    const target = this.mergeTargetId();
    if (!target) {
      this.lifecycleError.set(this.translation.t('hiveDetail.error.targetMissing'));
      return;
    }
    this.hiveService.mergeHive(this.hiveId(), {
      reason: 'merged',
      date: this.lifecycleDate(),
      note: this.lifecycleNote() || undefined,
      target_hive_id: target
    }).subscribe({
      next: () => window.location.reload(),
      error: () => this.lifecycleError.set(this.translation.t('hiveDetail.error.merge'))
    });
  }

  protected moveHive(): void {
    const target = this.moveTargetApiaryId();
    if (!target) {
      this.actionError.set(this.translation.t('hiveDetail.error.moveTargetMissing'));
      return;
    }
    this.hiveService.moveHive(this.hiveId(), {
      target_apiary_id: target,
      date: this.lifecycleDate(),
      note: this.lifecycleNote() || undefined
    }).subscribe({
      next: () => window.location.reload(),
      error: () => this.actionError.set(this.translation.t('hiveDetail.error.move'))
    });
  }

  protected copyHive(): void {
    this.hiveService.copyHive(this.hiveId(), {
      date: this.lifecycleDate(),
      name: this.copyName() || undefined,
      note: this.lifecycleNote() || undefined
    }).subscribe({
      next: copy => this.router.navigate(['/hives', copy.id]),
      error: () => this.actionError.set(this.translation.t('hiveDetail.error.copy'))
    });
  }

  protected requeenHive(): void {
    this.hiveService.requeenHive(this.hiveId(), {
      date: this.lifecycleDate(),
      year: this.requeenYear(),
      marking_color: this.requeenColor() || undefined,
      marking_code: this.requeenMarking() || undefined,
      introduced_at: this.requeenIntroducedAt(),
      reason: this.requeenReason() || undefined,
      note: this.lifecycleNote() || undefined
    }).subscribe({
      next: () => {
        this.requeenReason.set('');
        this.queenRefresh$.next();
        window.location.reload();
      },
      error: () => this.actionError.set(this.translation.t('hiveDetail.error.requeen'))
    });
  }

  protected addVarroaCheck(): void {
    if (this.varroaMiteCount() === null && this.varroaPerDay() === null) {
      this.actionError.set(this.translation.t('hiveDetail.error.varroaCheckEmpty'));
      return;
    }
    this.hiveService.createVarroaCheck({
      hive_id: this.hiveId(),
      date: this.lifecycleDate(),
      method: this.varroaMethod() || undefined,
      mite_count: this.varroaMiteCount(),
      mites_per_day: this.varroaPerDay(),
      notes: this.lifecycleNote() || undefined
    }).subscribe({
      next: () => window.location.reload(),
      error: () => this.actionError.set(this.translation.t('hiveDetail.error.varroaCheck'))
    });
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

  protected typeLabel(type: HiveType): string {
    const key = ({
      langstroth: 'beehives.type.langstroth',
      dadant: 'beehives.type.dadant',
      zander: 'beehives.type.zander',
      other: 'beehives.type.other'
    } satisfies Record<HiveType, TranslationKey>)[type];
    return this.translation.t(key);
  }

  protected colonyKindLabel(kind: ColonyKind): string {
    const key = ({
      wirtschaftsvolk: 'colonyKind.wirtschaftsvolk',
      ableger: 'colonyKind.ableger',
      schwarm: 'colonyKind.schwarm',
      kunstschwarm: 'colonyKind.kunstschwarm',
      other: 'colonyKind.other'
    } satisfies Record<ColonyKind, TranslationKey>)[kind];
    return this.translation.t(key);
  }
}
