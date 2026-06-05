import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { debounceTime } from 'rxjs';
import { InspectionService } from '../../core/services/inspection.service';
import { InspectionCreate } from '../../core/models/inspection.models';
import { InspectionDraftService } from '../../core/services/inspection-draft.service';

@Component({
  selector: 'app-hive-inspect',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './hive-inspect.component.html',
  styleUrl: './hive-inspect.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HiveInspectComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly draftService = inject(InspectionDraftService);
  private readonly inspectionService = inject(InspectionService);
  private readonly fb = inject(FormBuilder);

  protected readonly saving = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly draftMessage = signal('');
  protected readonly isOnline = signal(typeof navigator === 'undefined' ? true : navigator.onLine);
  protected readonly hiveId = Number(this.route.snapshot.paramMap.get('id'));
  protected readonly today = new Date().toISOString().slice(0, 10);

  protected readonly form = this.fb.group({
    date: [this.today],
    queen_seen: [false],
    food_stores: [5],
    varroa_count: [0],
    swarm_cells: ['none'],
    mood: ['normal'],
    strength: ['medium'],
    weather: [''],
    next_steps: [''],
    notes: ['']
  });

  constructor() {
    const draft = this.draftService.getDraft(this.hiveId);
    if (draft) {
      this.form.patchValue(draft.data);
      this.draftMessage.set(`Entwurf geladen: ${this.formatDateTime(draft.updated_at)}`);
    }

    this.form.valueChanges.pipe(debounceTime(400)).subscribe(() => {
      this.persistDraft('Entwurf lokal gespeichert.');
    });

    window.addEventListener('online', () => {
      this.isOnline.set(true);
      this.draftMessage.set('Wieder online. Entwurf kann gespeichert werden.');
    });
    window.addEventListener('offline', () => {
      this.isOnline.set(false);
      this.persistDraft('Offline. Entwurf lokal gespeichert.');
    });
  }

  protected save(): void {
    const payload = this.buildPayload();
    if (!this.isOnline()) {
      this.draftService.saveDraft(this.hiveId, payload);
      this.draftMessage.set('Offline. Entwurf lokal gespeichert.');
      return;
    }

    this.saving.set(true);
    this.errorMessage.set('');
    this.inspectionService.createInspection(this.hiveId, payload).subscribe({
      next: () => {
        this.draftService.clearDraft(this.hiveId);
        this.router.navigate(['/beehives', this.hiveId]);
      },
      error: () => {
        this.draftService.saveDraft(this.hiveId, payload);
        this.saving.set(false);
        this.errorMessage.set('Durchsicht konnte nicht gespeichert werden. Entwurf bleibt lokal gesichert.');
      }
    });
  }

  private buildPayload(): InspectionCreate {
    const value = this.form.value;
    return {
      date: value.date || this.today,
      queen_seen: value.queen_seen ?? false,
      food_stores: value.food_stores ?? undefined,
      varroa_count: value.varroa_count ?? undefined,
      swarm_cells: value.swarm_cells as InspectionCreate['swarm_cells'],
      mood: value.mood as InspectionCreate['mood'],
      strength: value.strength as InspectionCreate['strength'],
      weather: value.weather || undefined,
      next_steps: value.next_steps || undefined,
      notes: value.notes || undefined
    };
  }

  private persistDraft(message: string): void {
    const draft = this.draftService.saveDraft(this.hiveId, this.buildPayload());
    this.draftMessage.set(`${message} ${this.formatDateTime(draft.updated_at)}`);
  }

  private formatDateTime(value: string): string {
    return new Date(value).toLocaleString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}
