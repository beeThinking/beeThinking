import { ChangeDetectionStrategy, Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ReactiveFormsModule, FormBuilder } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { debounceTime } from 'rxjs';
import { InspectionService } from '../../core/services/inspection.service';
import {
  CriterionSection,
  CriterionValueType,
  InspectionCreate,
  InspectionCriterion
} from '../../core/models/inspection.models';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { InspectionDraftService } from '../../core/services/inspection-draft.service';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { TranslationKey } from '../../core/i18n/en';
import { localDateString } from '../../core/utils/date.utils';

@Component({
  selector: 'app-hive-inspect',
  standalone: true,
  imports: [ReactiveFormsModule, FormsModule, TranslatePipe],
  templateUrl: './hive-inspect.component.html',
  styleUrl: './hive-inspect.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HiveInspectComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly draftService = inject(InspectionDraftService);
  private readonly inspectionService = inject(InspectionService);
  private readonly beekeepingService = inject(BeekeepingService);
  private readonly fb = inject(FormBuilder);
  private readonly translation = inject(TranslationService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly saving = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly draftMessage = signal('');
  protected readonly isOnline = signal(typeof navigator === 'undefined' ? true : navigator.onLine);
  protected readonly hiveId = Number(this.route.snapshot.paramMap.get('id'));
  protected readonly today = localDateString();

  protected readonly criteria = signal<InspectionCriterion[]>([]);
  protected readonly criteriaValues = signal<Record<string, unknown>>({});
  protected readonly showEditor = signal(false);
  protected readonly editorError = signal('');
  protected readonly newCriterionName = signal('');
  protected readonly newCriterionSection = signal<CriterionSection>('verschiedenes');
  protected readonly newCriterionType = signal<CriterionValueType>('stars');
  protected readonly newCriterionOptions = signal('');
  protected readonly sections: CriterionSection[] = ['allg_befund', 'verhalten', 'klima', 'verschiedenes'];
  protected readonly valueTypes: CriterionValueType[] = ['stars', 'bool', 'number', 'text', 'select'];
  protected readonly stars = [1, 2, 3, 4, 5, 6];

  protected readonly createTodo = signal(false);
  protected readonly todoTitle = signal('');
  protected readonly photoFile = signal<File | null>(null);

  protected readonly activeSections = computed(() => {
    const active = this.criteria().filter(criterion => criterion.is_active);
    return this.sections
      .map(section => ({
        section,
        criteria: active.filter(criterion => criterion.section === section)
      }))
      .filter(group => group.criteria.length > 0);
  });

  protected readonly form = this.fb.group({
    date: [this.today],
    queen_seen: [false],
    food_stores: [5],
    varroa_count: [0],
    swarm_cells: ['none'],
    mood: ['normal'],
    strength: ['medium'],
    hive_weight_kg: [null as number | null],
    weather: [''],
    next_steps: [''],
    notes: ['']
  });

  constructor() {
    this.loadCriteria();

    const draft = this.draftService.getDraft(this.hiveId);
    if (draft) {
      this.form.patchValue(draft.data);
      if (draft.data.criteria_values) {
        this.criteriaValues.set({ ...draft.data.criteria_values });
      }
      this.draftMessage.set(this.translation.t('inspect.draftLoaded', { date: this.formatDateTime(draft.updated_at) }));
    }

    this.form.valueChanges.pipe(debounceTime(400), takeUntilDestroyed(this.destroyRef)).subscribe(() => {
      this.persistDraft(this.translation.t('inspect.draftSaved'));
    });

    const onOnline = () => {
      this.isOnline.set(true);
      this.syncDraft();
    };
    const onOffline = () => {
      this.isOnline.set(false);
      this.persistDraft(this.translation.t('inspect.offlineSaved'));
    };
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);
    this.destroyRef.onDestroy(() => {
      window.removeEventListener('online', onOnline);
      window.removeEventListener('offline', onOffline);
    });
  }

  private loadCriteria(): void {
    this.inspectionService.getCriteria().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: criteria => this.criteria.set(criteria),
      error: () => undefined
    });
  }

  protected criterionValue(id: number): unknown {
    return this.criteriaValues()[String(id)];
  }

  protected setCriterionValue(id: number, value: unknown): void {
    this.criteriaValues.update(values => {
      const next = { ...values };
      if (value === null || value === undefined || value === '') {
        delete next[String(id)];
      } else {
        next[String(id)] = value;
      }
      return next;
    });
    this.persistDraft(this.translation.t('inspect.draftSaved'));
  }

  protected toggleStar(criterion: InspectionCriterion, value: number): void {
    const current = this.criterionValue(criterion.id);
    this.setCriterionValue(criterion.id, current === value ? null : value);
  }

  protected sectionLabel(section: CriterionSection): string {
    const key = ({
      allg_befund: 'inspect.section.allgBefund',
      verhalten: 'inspect.section.verhalten',
      klima: 'inspect.section.klima',
      verschiedenes: 'inspect.section.verschiedenes'
    } satisfies Record<CriterionSection, TranslationKey>)[section];
    return this.translation.t(key);
  }

  protected valueTypeLabel(type: CriterionValueType): string {
    const key = ({
      stars: 'inspect.type.stars',
      bool: 'inspect.type.bool',
      number: 'inspect.type.number',
      text: 'inspect.type.text',
      select: 'inspect.type.select'
    } satisfies Record<CriterionValueType, TranslationKey>)[type];
    return this.translation.t(key);
  }

  protected toggleCriterionActive(criterion: InspectionCriterion): void {
    this.inspectionService.updateCriterion(criterion.id, { is_active: !criterion.is_active }).subscribe({
      next: updated => this.criteria.update(list => list.map(item => item.id === updated.id ? updated : item)),
      error: () => this.editorError.set(this.translation.t('inspect.editor.error'))
    });
  }

  protected updateCriterionOptions(criterion: InspectionCriterion, value: string): void {
    const options = value.split(',').map(option => option.trim()).filter(Boolean);
    this.inspectionService.updateCriterion(criterion.id, { options }).subscribe({
      next: updated => this.criteria.update(list => list.map(item => item.id === updated.id ? updated : item)),
      error: () => this.editorError.set(this.translation.t('inspect.editor.error'))
    });
  }

  protected addCriterion(): void {
    const name = this.newCriterionName().trim();
    if (!name) return;
    const type = this.newCriterionType();
    const options = type === 'select'
      ? this.newCriterionOptions().split(',').map(option => option.trim()).filter(Boolean)
      : undefined;
    this.inspectionService.createCriterion({
      name,
      section: this.newCriterionSection(),
      value_type: type,
      options,
      sort_order: (this.criteria().at(-1)?.sort_order ?? 0) + 10
    }).subscribe({
      next: created => {
        this.criteria.update(list => [...list, created]);
        this.newCriterionName.set('');
        this.newCriterionOptions.set('');
      },
      error: () => this.editorError.set(this.translation.t('inspect.editor.error'))
    });
  }

  protected deleteCriterion(criterion: InspectionCriterion): void {
    this.inspectionService.deleteCriterion(criterion.id).subscribe({
      next: () => this.criteria.update(list => list.filter(item => item.id !== criterion.id)),
      error: () => this.editorError.set(this.translation.t('inspect.editor.error'))
    });
  }

  protected selectPhoto(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.photoFile.set(input.files?.[0] ?? null);
  }

  protected save(): void {
    const payload = this.buildPayload();
    if (!this.isOnline()) {
      this.draftService.saveDraft(this.hiveId, payload);
      this.draftMessage.set(this.translation.t('inspect.offlineSaved'));
      return;
    }

    this.submit(payload);
  }

  private syncDraft(): void {
    const draft = this.draftService.getDraft(this.hiveId);
    if (!draft) {
      this.draftMessage.set(this.translation.t('inspect.online'));
      return;
    }
    this.submit(draft.data);
  }

  private submit(payload: InspectionCreate): void {
    if (this.saving()) return;
    this.saving.set(true);
    this.errorMessage.set('');
    this.inspectionService.createInspection(this.hiveId, payload).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => {
        this.draftService.clearDraft(this.hiveId);
        this.createFollowUps(payload);
        this.router.navigate(['/hives', this.hiveId]);
      },
      error: () => {
        this.draftService.saveDraft(this.hiveId, payload);
        this.saving.set(false);
        this.errorMessage.set(this.translation.t('inspect.error.save'));
      }
    });
  }

  private createFollowUps(payload: InspectionCreate): void {
    if (this.createTodo()) {
      const title = this.todoTitle().trim() || payload.next_steps || this.translation.t('inspect.todo.defaultTitle');
      this.beekeepingService.createTask({ hive_id: this.hiveId, title }).subscribe({ error: () => undefined });
    }
    const photo = this.photoFile();
    if (photo) {
      this.beekeepingService.uploadPhoto({ file: photo, hive_id: this.hiveId, caption: payload.notes || '' })
        .subscribe({ error: () => undefined });
    }
  }

  private buildPayload(): InspectionCreate {
    const value = this.form.value;
    const criteriaValues = this.criteriaValues();
    return {
      date: value.date || this.today,
      queen_seen: value.queen_seen ?? false,
      food_stores: value.food_stores ?? undefined,
      varroa_count: value.varroa_count ?? undefined,
      swarm_cells: value.swarm_cells as InspectionCreate['swarm_cells'],
      mood: value.mood as InspectionCreate['mood'],
      strength: value.strength as InspectionCreate['strength'],
      hive_weight_kg: value.hive_weight_kg ?? undefined,
      criteria_values: Object.keys(criteriaValues).length ? criteriaValues : undefined,
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
    return new Date(value).toLocaleString(this.translation.currentLang() === 'de' ? 'de-DE' : 'en-US', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}
