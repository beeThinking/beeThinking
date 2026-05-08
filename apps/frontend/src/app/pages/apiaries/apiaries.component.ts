import { Component, inject, signal, computed, ChangeDetectionStrategy } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { DecimalPipe } from '@angular/common';
import { ApiaryService } from '../../core/services/apiary.service';
import { Apiary, ApiaryCreate, ApiaryUpdate } from '../../core/models/apiary.models';

@Component({
  selector: 'app-apiaries',
  standalone: true,
  imports: [ReactiveFormsModule, DecimalPipe],
  templateUrl: './apiaries.component.html',
  styleUrl: './apiaries.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ApiariesComponent {
  private readonly apiaryService = inject(ApiaryService);
  private readonly fb = inject(FormBuilder);

  private readonly apiarysData = toSignal(this.apiaryService.getApiaries(), { initialValue: [] });
  private readonly localApiaries = signal<Apiary[] | null>(null);

  protected readonly apiaries = computed(() => this.localApiaries() ?? this.apiarysData());
  protected readonly isLoading = computed(() => this.localApiaries() === null && this.apiarysData().length === 0);
  protected readonly errorMessage = signal('');
  protected readonly showForm = signal(false);
  protected readonly editingApiary = signal<Apiary | null>(null);

  protected readonly form = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(100)]],
    address: [''],
    latitude: [null as number | null, [Validators.min(-90), Validators.max(90)]],
    longitude: [null as number | null, [Validators.min(-180), Validators.max(180)]],
    notes: ['']
  });

  protected openCreateForm(): void {
    this.editingApiary.set(null);
    this.form.reset();
    this.showForm.set(true);
  }

  protected openEditForm(apiary: Apiary): void {
    this.editingApiary.set(apiary);
    this.form.setValue({
      name: apiary.name,
      address: apiary.address ?? '',
      latitude: apiary.latitude ?? null,
      longitude: apiary.longitude ?? null,
      notes: apiary.notes ?? ''
    });
    this.showForm.set(true);
  }

  protected closeForm(): void {
    this.showForm.set(false);
    this.editingApiary.set(null);
    this.form.reset();
  }

  protected onSubmit(): void {
    if (this.form.invalid) return;

    const values = this.form.value;
    const editing = this.editingApiary();

    if (editing) {
      const update: ApiaryUpdate = {
        name: values.name ?? undefined,
        address: values.address || undefined,
        latitude: values.latitude ?? undefined,
        longitude: values.longitude ?? undefined,
        notes: values.notes || undefined
      };
      this.apiaryService.updateApiary(editing.id, update).subscribe({
        next: (updated) => {
          this.localApiaries.update(list => (list ?? this.apiarysData()).map(a => a.id === updated.id ? updated : a));
          this.closeForm();
        },
        error: () => this.errorMessage.set('Failed to update apiary.')
      });
    } else {
      const create: ApiaryCreate = {
        name: values.name!,
        address: values.address || undefined,
        latitude: values.latitude ?? undefined,
        longitude: values.longitude ?? undefined,
        notes: values.notes || undefined
      };
      this.apiaryService.createApiary(create).subscribe({
        next: (apiary) => {
          this.localApiaries.update(list => [...(list ?? this.apiarysData()), apiary]);
          this.closeForm();
        },
        error: () => this.errorMessage.set('Failed to create apiary.')
      });
    }
  }

  protected deleteApiary(apiary: Apiary): void {
    if (!confirm(`Delete "${apiary.name}"?`)) return;
    this.apiaryService.deleteApiary(apiary.id).subscribe({
      next: () => this.localApiaries.update(list => (list ?? this.apiarysData()).filter(a => a.id !== apiary.id)),
      error: () => this.errorMessage.set('Failed to delete apiary.')
    });
  }
}
