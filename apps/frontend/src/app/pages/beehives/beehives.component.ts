import { Component, inject, signal, computed, ChangeDetectionStrategy } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { HiveService } from '../../core/services/hive.service';
import { ApiaryService } from '../../core/services/apiary.service';
import { Hive, HiveCreate, HiveUpdate, HiveStatus, HiveType } from '../../core/models/hive.models';

@Component({
  selector: 'app-beehives',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './beehives.component.html',
  styleUrl: './beehives.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class BeehivesComponent {
  private readonly hiveService = inject(HiveService);
  private readonly apiaryService = inject(ApiaryService);
  private readonly fb = inject(FormBuilder);

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
        error: () => this.errorMessage.set('Failed to update hive.')
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
        error: () => this.errorMessage.set('Failed to create hive.')
      });
    }
  }

  protected deleteHive(hive: Hive): void {
    if (!confirm(`Delete "${hive.name}"?`)) return;
    this.hiveService.deleteHive(hive.id).subscribe({
      next: () => this.localHives.update(list => (list ?? this.hivesData()).filter(h => h.id !== hive.id)),
      error: () => this.errorMessage.set('Failed to delete hive.')
    });
  }

  protected apiaryName(apiaryId: number): string {
    return this.apiaries().find(a => a.id === apiaryId)?.name ?? `Stand #${apiaryId}`;
  }

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

  protected typeLabel(type: HiveType): string {
    return { langstroth: 'Langstroth', dadant: 'Dadant', zander: 'Zander', other: 'Other' }[type];
  }
}
