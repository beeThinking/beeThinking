import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { catchError, combineLatest, forkJoin, map, of, startWith, Subject, switchMap } from 'rxjs';
import { PhotoWithPreview } from '../../core/models/beekeeping.models';
import { HiveEvent } from '../../core/models/hive.models';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HiveService } from '../../core/services/hive.service';

@Component({
  selector: 'app-hive-detail',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './hive-detail.component.html',
  styleUrl: './hive-detail.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HiveDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly beekeepingService = inject(BeekeepingService);
  private readonly hiveService = inject(HiveService);
  private readonly hiveId = computed(() => Number(this.route.snapshot.paramMap.get('id')));
  private readonly photoRefresh$ = new Subject<void>();

  protected readonly hive = toSignal(this.route.paramMap.pipe(
    switchMap(params => this.hiveService.getHive(Number(params.get('id'))))
  ));
  protected readonly timeline = toSignal(this.route.paramMap.pipe(
    switchMap(params => this.hiveService.getHiveTimeline(Number(params.get('id'))))
  ), { initialValue: [] });
  protected readonly history = toSignal(this.route.paramMap.pipe(
    switchMap(params => this.hiveService.getHiveHistory(Number(params.get('id'))))
  ), { initialValue: [] as HiveEvent[] });
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

  protected readonly inspectLink = computed(() => ['/beehives', this.hiveId(), 'inspect']);
  protected readonly caption = signal('');
  protected readonly selectedFile = signal<File | null>(null);
  protected readonly uploadError = signal('');
  protected readonly uploadPending = signal(false);
  protected readonly lifecycleError = signal('');
  protected readonly lifecycleDate = signal(new Date().toISOString().slice(0, 10));
  protected readonly lifecycleNote = signal('');
  protected readonly mergeTargetId = signal<number | null>(null);

  protected formatDate(value: string): string {
    return new Date(value).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
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
        this.uploadError.set('Foto konnte nicht hochgeladen werden.');
        this.uploadPending.set(false);
      }
    });
  }

  protected deletePhoto(photo: PhotoWithPreview): void {
    this.beekeepingService.deletePhoto(photo.id).subscribe({
      next: () => this.photoRefresh$.next(),
      error: () => this.uploadError.set('Foto konnte nicht gelöscht werden.')
    });
  }

  protected archiveHive(): void {
    this.hiveService.archiveHive(this.hiveId(), {
      reason: 'archived',
      date: this.lifecycleDate(),
      note: this.lifecycleNote() || undefined
    }).subscribe({
      next: () => window.location.reload(),
      error: () => this.lifecycleError.set('Volk konnte nicht archiviert werden.')
    });
  }

  protected dissolveHive(reason: string): void {
    this.hiveService.dissolveHive(this.hiveId(), {
      reason,
      date: this.lifecycleDate(),
      note: this.lifecycleNote() || undefined
    }).subscribe({
      next: () => window.location.reload(),
      error: () => this.lifecycleError.set('Volk konnte nicht aufgelöst werden.')
    });
  }

  protected mergeHive(): void {
    const target = this.mergeTargetId();
    if (!target) {
      this.lifecycleError.set('Zielvolk fehlt.');
      return;
    }
    this.hiveService.mergeHive(this.hiveId(), {
      reason: 'merged',
      date: this.lifecycleDate(),
      note: this.lifecycleNote() || undefined,
      target_hive_id: target
    }).subscribe({
      next: () => window.location.reload(),
      error: () => this.lifecycleError.set('Völker konnten nicht vereinigt werden.')
    });
  }
}
