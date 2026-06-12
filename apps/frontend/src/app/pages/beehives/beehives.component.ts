import { Component, inject, signal, computed, ChangeDetectionStrategy } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { HiveService } from '../../core/services/hive.service';
import { ApiaryService } from '../../core/services/apiary.service';
import { Hive, HiveCreate, HiveUpdate, HiveStatus, HiveType } from '../../core/models/hive.models';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { TranslationKey } from '../../core/i18n/en';

@Component({
  selector: 'app-beehives',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink, TranslatePipe],
  templateUrl: './beehives.component.html',
  styleUrl: './beehives.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class BeehivesComponent {
  private readonly hiveService = inject(HiveService);
  private readonly apiaryService = inject(ApiaryService);
  private readonly fb = inject(FormBuilder);
  private readonly translation = inject(TranslationService);

  private readonly hivesData = toSignal(this.hiveService.getHives(), { initialValue: [] });
  private readonly localHives = signal<Hive[] | null>(null);

  protected readonly apiaries = toSignal(this.apiaryService.getApiaries(), { initialValue: [] });
  protected readonly hives = computed(() => this.localHives() ?? this.hivesData());
  protected readonly isLoading = computed(() => this.localHives() === null && this.hivesData().length === 0);
  protected readonly errorMessage = signal('');
  protected readonly showForm = signal(false);
  protected readonly editingHive = signal<Hive | null>(null);

  protected readonly hiveTypes: HiveType[] = ['langstroth', 'dadant', 'zander', 'other'];
  protected readonly hiveStatuses: HiveStatus[] = ['active', 'inactive', 'lost', 'created_by_mistake'];

  protected readonly form = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(100)]],
    apiary_id: [null as number | null, [Validators.required]],
    type: ['langstroth' as HiveType],
    status: ['active' as HiveStatus],
    notes: ['']
  });

  protected openCreateForm(): void {
    this.editingHive.set(null);
    this.form.reset({ type: 'langstroth', status: 'active' });
    this.showForm.set(true);
  }

  protected openEditForm(hive: Hive): void {
    this.editingHive.set(hive);
    this.form.setValue({
      name: hive.name,
      apiary_id: hive.apiary_id,
      type: hive.type,
      status: hive.status,
      notes: hive.notes ?? ''
    });
    this.showForm.set(true);
  }

  protected closeForm(): void {
    this.showForm.set(false);
    this.editingHive.set(null);
    this.form.reset();
  }

  protected onSubmit(): void {
    if (this.form.invalid) return;

    const values = this.form.value;
    const editing = this.editingHive();

    if (editing) {
      const update: HiveUpdate = {
        name: values.name ?? undefined,
        apiary_id: values.apiary_id ?? undefined,
        type: values.type as HiveType,
        status: values.status as HiveStatus,
        notes: values.notes || undefined
      };
      this.hiveService.updateHive(editing.id, update).subscribe({
        next: (updated) => {
          this.localHives.update(list => (list ?? this.hivesData()).map(h => h.id === updated.id ? updated : h));
          this.closeForm();
        },
        error: () => this.errorMessage.set(this.translation.t('beehives.error.update'))
      });
    } else {
      const create: HiveCreate = {
        name: values.name!,
        apiary_id: values.apiary_id!,
        type: values.type as HiveType,
        status: values.status as HiveStatus,
        notes: values.notes || undefined
      };
      this.hiveService.createHive(create).subscribe({
        next: (hive) => {
          this.localHives.update(list => [...(list ?? this.hivesData()), hive]);
          this.closeForm();
        },
        error: () => this.errorMessage.set(this.translation.t('beehives.error.create'))
      });
    }
  }

  protected deleteHive(hive: Hive): void {
    if (!confirm(this.translation.t('beehives.delete.confirm', { name: hive.name }))) return;
    this.hiveService.deleteHive(hive.id).subscribe({
      next: () => this.localHives.update(list => (list ?? this.hivesData()).filter(h => h.id !== hive.id)),
      error: () => this.errorMessage.set(this.translation.t('beehives.error.delete'))
    });
  }

  protected apiaryName(apiaryId: number): string {
    const apiary = this.apiaries().find(a => a.id === apiaryId);
    return apiary ? this.apiaryTitle(apiary) : this.translation.t('common.apiaryRef', { id: apiaryId });
  }

  protected apiaryTitle(apiary: { stock_number: string; name: string | null }): string {
    return apiary.name?.trim() || apiary.stock_number;
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
}
