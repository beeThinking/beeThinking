import { Component, OnInit, inject, signal, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { HiveService } from '../../core/services/hive.service';
import { Hive, HiveCreate, HiveUpdate, HiveStatus, HiveType } from '../../core/models/hive.models';

@Component({
  selector: 'app-beehives',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './beehives.component.html',
  styleUrl: './beehives.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class BeehivesComponent implements OnInit {
  private readonly hiveService = inject(HiveService);
  private readonly fb = inject(FormBuilder);

  protected readonly hives = signal<Hive[]>([]);
  protected readonly isLoading = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly showForm = signal(false);
  protected readonly editingHive = signal<Hive | null>(null);

  protected readonly hiveTypes: HiveType[] = ['langstroth', 'dadant', 'zander', 'other'];
  protected readonly hiveStatuses: HiveStatus[] = ['active', 'inactive', 'lost'];

  protected readonly form = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(100)]],
    location: [''],
    type: ['langstroth' as HiveType],
    status: ['active' as HiveStatus],
    notes: ['']
  });

  ngOnInit(): void {
    this.loadHives();
  }

  private loadHives(): void {
    this.isLoading.set(true);
    this.errorMessage.set('');
    this.hiveService.getHives().subscribe({
      next: (hives) => {
        this.hives.set(hives);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Failed to load hives.');
        this.isLoading.set(false);
      }
    });
  }

  protected openCreateForm(): void {
    this.editingHive.set(null);
    this.form.reset({ type: 'langstroth', status: 'active' });
    this.showForm.set(true);
  }

  protected openEditForm(hive: Hive): void {
    this.editingHive.set(hive);
    this.form.setValue({
      name: hive.name,
      location: hive.location ?? '',
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
        location: values.location || undefined,
        type: values.type as HiveType,
        status: values.status as HiveStatus,
        notes: values.notes || undefined
      };
      this.hiveService.updateHive(editing.id, update).subscribe({
        next: (updated) => {
          this.hives.update(list => list.map(h => h.id === updated.id ? updated : h));
          this.closeForm();
        },
        error: () => this.errorMessage.set('Failed to update hive.')
      });
    } else {
      const create: HiveCreate = {
        name: values.name!,
        location: values.location || undefined,
        type: values.type as HiveType,
        status: values.status as HiveStatus,
        notes: values.notes || undefined
      };
      this.hiveService.createHive(create).subscribe({
        next: (hive) => {
          this.hives.update(list => [...list, hive]);
          this.closeForm();
        },
        error: () => this.errorMessage.set('Failed to create hive.')
      });
    }
  }

  protected deleteHive(hive: Hive): void {
    if (!confirm(`Delete "${hive.name}"?`)) return;
    this.hiveService.deleteHive(hive.id).subscribe({
      next: () => this.hives.update(list => list.filter(h => h.id !== hive.id)),
      error: () => this.errorMessage.set('Failed to delete hive.')
    });
  }

  protected statusLabel(status: HiveStatus): string {
    return { active: 'Active', inactive: 'Inactive', lost: 'Lost' }[status];
  }

  protected typeLabel(type: HiveType): string {
    return { langstroth: 'Langstroth', dadant: 'Dadant', zander: 'Zander', other: 'Other' }[type];
  }
}
