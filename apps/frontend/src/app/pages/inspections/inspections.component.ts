import { Component, inject, signal, computed, ChangeDetectionStrategy } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { catchError, forkJoin, map, of, switchMap } from 'rxjs';
import { HiveService } from '../../core/services/hive.service';
import { InspectionService } from '../../core/services/inspection.service';
import { Hive } from '../../core/models/hive.models';
import { PhotoWithPreview } from '../../core/models/beekeeping.models';
import { Inspection, InspectionCreate, InspectionUpdate } from '../../core/models/inspection.models';
import { BeekeepingService } from '../../core/services/beekeeping.service';

@Component({
  selector: 'app-inspections',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './inspections.component.html',
  styleUrl: './inspections.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class InspectionsComponent {
  private readonly beekeepingService = inject(BeekeepingService);
  private readonly hiveService = inject(HiveService);
  private readonly inspectionService = inject(InspectionService);
  private readonly fb = inject(FormBuilder);

  protected readonly hives = toSignal(this.hiveService.getHives(), { initialValue: [] });
  protected readonly selectedHiveId = signal<number | null>(null);
  protected readonly selectedHive = computed<Hive | null>(
    () => this.hives().find(h => h.id === this.selectedHiveId()) ?? null
  );

  private readonly localInspections = signal<Inspection[] | null>(null);
  private readonly remoteInspections = toSignal(
    computed(() => {
      const id = this.selectedHiveId();
      return id ? this.inspectionService.getInspections(id) : of([]);
    })(),
    { initialValue: [] as Inspection[] }
  );
  protected readonly inspections = computed<Inspection[]>(
    () => this.localInspections() ?? this.remoteInspections()
  );

  protected readonly errorMessage = signal('');
  protected readonly photoErrorMessage = signal('');
  protected readonly showForm = signal(false);
  protected readonly editingInspection = signal<Inspection | null>(null);
  protected readonly inspectionPhotos = signal<PhotoWithPreview[]>([]);
  protected readonly selectedPhotoInspectionId = signal<number | null>(null);
  protected readonly selectedPhotoFile = signal<File | null>(null);
  protected readonly photoCaption = signal('');
  protected readonly photoUploadPending = signal(false);

  protected readonly today = new Date().toISOString().split('T')[0];

  protected readonly form = this.fb.group({
    date: [this.today, Validators.required],
    queen_seen: [false],
    brood_strength: [null as number | null, [Validators.min(1), Validators.max(10)]],
    varroa_count: [null as number | null, Validators.min(0)],
    food_stores: [null as number | null, [Validators.min(1), Validators.max(10)]],
    notes: ['']
  });

  protected selectHive(hiveId: number): void {
    this.selectedHiveId.set(hiveId);
    this.localInspections.set(null);
    this.errorMessage.set('');
    this.photoErrorMessage.set('');
    this.inspectionPhotos.set([]);
    this.closeForm();

    this.inspectionService.getInspections(hiveId).subscribe({
      next: (list) => this.localInspections.set(list),
      error: () => this.errorMessage.set('Failed to load inspections.')
    });
    this.loadInspectionPhotos(hiveId);
  }

  protected openCreateForm(): void {
    this.editingInspection.set(null);
    this.form.reset({ date: this.today, queen_seen: false });
    this.showForm.set(true);
  }

  protected openEditForm(inspection: Inspection): void {
    this.editingInspection.set(inspection);
    this.form.setValue({
      date: inspection.date,
      queen_seen: inspection.queen_seen,
      brood_strength: inspection.brood_strength,
      varroa_count: inspection.varroa_count,
      food_stores: inspection.food_stores,
      notes: inspection.notes ?? ''
    });
    this.showForm.set(true);
  }

  protected closeForm(): void {
    this.showForm.set(false);
    this.editingInspection.set(null);
    this.form.reset();
  }

  protected onSubmit(): void {
    if (this.form.invalid || !this.selectedHiveId()) return;

    const hiveId = this.selectedHiveId()!;
    const v = this.form.value;
    const editing = this.editingInspection();

    if (editing) {
      const update: InspectionUpdate = {
        date: v.date ?? undefined,
        queen_seen: v.queen_seen ?? undefined,
        brood_strength: v.brood_strength ?? undefined,
        varroa_count: v.varroa_count ?? undefined,
        food_stores: v.food_stores ?? undefined,
        notes: v.notes || undefined
      };
      this.inspectionService.updateInspection(hiveId, editing.id, update).subscribe({
        next: (updated) => {
          this.localInspections.update(list =>
            (list ?? []).map(i => i.id === updated.id ? updated : i)
          );
          this.closeForm();
        },
        error: () => this.errorMessage.set('Failed to update inspection.')
      });
    } else {
      const create: InspectionCreate = {
        date: v.date!,
        queen_seen: v.queen_seen ?? false,
        brood_strength: v.brood_strength ?? undefined,
        varroa_count: v.varroa_count ?? undefined,
        food_stores: v.food_stores ?? undefined,
        notes: v.notes || undefined
      };
      this.inspectionService.createInspection(hiveId, create).subscribe({
        next: (inspection) => {
          this.localInspections.update(list => [inspection, ...(list ?? [])]);
          this.closeForm();
        },
        error: () => this.errorMessage.set('Failed to create inspection.')
      });
    }
  }

  protected deleteInspection(inspection: Inspection): void {
    if (!confirm('Delete this inspection?')) return;
    this.inspectionService.deleteInspection(this.selectedHiveId()!, inspection.id).subscribe({
      next: () => this.localInspections.update(list => (list ?? []).filter(i => i.id !== inspection.id)),
      error: () => this.errorMessage.set('Failed to delete inspection.')
    });
  }

  protected photosForInspection(inspectionId: number): PhotoWithPreview[] {
    return this.inspectionPhotos().filter(photo => photo.inspection_id === inspectionId);
  }

  protected selectPhoto(inspection: Inspection, event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedPhotoInspectionId.set(inspection.id);
    this.selectedPhotoFile.set(input.files?.[0] ?? null);
    this.photoErrorMessage.set('');
  }

  protected uploadPhoto(inspection: Inspection): void {
    const hiveId = this.selectedHiveId();
    const file = this.selectedPhotoFile();
    if (!hiveId || !file || this.photoUploadPending()) {
      return;
    }

    this.photoUploadPending.set(true);
    this.photoErrorMessage.set('');
    this.beekeepingService.uploadPhoto({
      file,
      hive_id: hiveId,
      inspection_id: inspection.id,
      caption: this.photoCaption()
    }).pipe(
      switchMap(photo => this.beekeepingService.getPhotoPreview(photo.id).pipe(
        map(preview => ({ ...photo, preview_url: preview.url })),
        catchError(() => of({ ...photo, preview_url: null }))
      ))
    ).subscribe({
      next: (photo) => {
        this.inspectionPhotos.update(photos => [photo, ...photos]);
        this.selectedPhotoInspectionId.set(null);
        this.selectedPhotoFile.set(null);
        this.photoCaption.set('');
        this.photoUploadPending.set(false);
      },
      error: () => {
        this.photoErrorMessage.set('Foto konnte nicht hochgeladen werden.');
        this.photoUploadPending.set(false);
      }
    });
  }

  protected deletePhoto(photo: PhotoWithPreview): void {
    this.beekeepingService.deletePhoto(photo.id).subscribe({
      next: () => this.inspectionPhotos.update(photos => photos.filter(item => item.id !== photo.id)),
      error: () => this.photoErrorMessage.set('Foto konnte nicht gelöscht werden.')
    });
  }

  protected formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
  }

  protected strengthLabel(value: number | null): string {
    if (value === null) return '–';
    const labels = ['', 'Sehr schwach', 'Schwach', 'Schwach-mittel', 'Mittel', 'Mittel', 'Mittel-stark', 'Stark', 'Sehr stark', 'Sehr stark', 'Maximal'];
    return `${value}/10 ${labels[value] ?? ''}`;
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

  private loadInspectionPhotos(hiveId: number): void {
    this.beekeepingService.getPhotos().pipe(
      map(photos => photos.filter(photo => photo.hive_id === hiveId && photo.inspection_id !== null)),
      switchMap(photos => photos.length
        ? forkJoin(photos.map(photo => this.beekeepingService.getPhotoPreview(photo.id).pipe(
            map(preview => ({ ...photo, preview_url: preview.url })),
            catchError(() => of({ ...photo, preview_url: null }))
          )))
        : of([] as PhotoWithPreview[])
      )
    ).subscribe({
      next: photos => this.inspectionPhotos.set(photos),
      error: () => this.photoErrorMessage.set('Fotos konnten nicht geladen werden.')
    });
  }
}
