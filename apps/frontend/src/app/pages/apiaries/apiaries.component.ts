import { Component, inject, signal, computed, ChangeDetectionStrategy } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { DecimalPipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiaryService } from '../../core/services/apiary.service';
import { Apiary, ApiaryCreate, ApiaryUpdate } from '../../core/models/apiary.models';
import { ApiaryMapPickerComponent, ApiaryPosition } from '../../shared/components/apiary-map-picker.component';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';

@Component({
  selector: 'app-apiaries',
  standalone: true,
  imports: [ReactiveFormsModule, DecimalPipe, RouterLink, ApiaryMapPickerComponent, TranslatePipe],
  templateUrl: './apiaries.component.html',
  styleUrl: './apiaries.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ApiariesComponent {
  private readonly apiaryService = inject(ApiaryService);
  private readonly fb = inject(FormBuilder);
  private readonly translation = inject(TranslationService);

  private readonly apiarysData = toSignal(this.apiaryService.getApiaries(), { initialValue: [] });
  private readonly localApiaries = signal<Apiary[] | null>(null);

  protected readonly apiaries = computed(() => this.localApiaries() ?? this.apiarysData());
  protected readonly isLoading = computed(() => this.localApiaries() === null && this.apiarysData().length === 0);
  protected readonly errorMessage = signal('');
  protected readonly showForm = signal(false);
  protected readonly editingApiary = signal<Apiary | null>(null);
  protected readonly addressLookupPending = signal(false);
  protected readonly addressLookupMessage = signal('');
  private lastAutoAddress = '';

  protected readonly form = this.fb.group({
    stock_number: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(100)]],
    name: ['', [Validators.maxLength(100)]],
    address: [''],
    latitude: [null as number | null, [Validators.min(-90), Validators.max(90)]],
    longitude: [null as number | null, [Validators.min(-180), Validators.max(180)]],
    notes: ['']
  });

  protected openCreateForm(): void {
    this.editingApiary.set(null);
    this.form.reset();
    this.lastAutoAddress = '';
    this.addressLookupMessage.set('');
    this.showForm.set(true);
  }

  protected openEditForm(apiary: Apiary): void {
    this.editingApiary.set(apiary);
    this.form.setValue({
      stock_number: apiary.stock_number,
      name: apiary.name ?? '',
      address: apiary.address ?? '',
      latitude: apiary.latitude ?? null,
      longitude: apiary.longitude ?? null,
      notes: apiary.notes ?? ''
    });
    this.lastAutoAddress = '';
    this.addressLookupMessage.set('');
    this.showForm.set(true);
  }

  protected closeForm(): void {
    this.showForm.set(false);
    this.editingApiary.set(null);
    this.form.reset();
    this.lastAutoAddress = '';
    this.addressLookupMessage.set('');
  }

  protected onSubmit(): void {
    if (this.form.invalid) return;

    const values = this.form.value;
    const editing = this.editingApiary();

    if (editing) {
      const update: ApiaryUpdate = {
        stock_number: values.stock_number ?? undefined,
        name: values.name || undefined,
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
        error: () => this.errorMessage.set(this.translation.t('apiaries.error.update'))
      });
    } else {
      const create: ApiaryCreate = {
        stock_number: values.stock_number!,
        name: values.name || undefined,
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
        error: () => this.errorMessage.set(this.translation.t('apiaries.error.create'))
      });
    }
  }

  protected setPosition(position: ApiaryPosition): void {
    this.form.patchValue({
      latitude: position.latitude,
      longitude: position.longitude
    });
    this.form.controls.latitude.markAsDirty();
    this.form.controls.longitude.markAsDirty();
    this.lookupAddress(position);
  }

  protected deleteApiary(apiary: Apiary): void {
    if (!confirm(this.translation.t('apiaries.delete.confirm', { name: this.apiaryTitle(apiary) }))) return;
    this.apiaryService.deleteApiary(apiary.id).subscribe({
      next: () => this.localApiaries.update(list => (list ?? this.apiarysData()).filter(a => a.id !== apiary.id)),
      error: () => this.errorMessage.set(this.translation.t('apiaries.error.delete'))
    });
  }

  protected hiveCountLabel(count: number): string {
    return this.translation.t(count === 1 ? 'apiaries.hiveCount' : 'apiaries.hiveCountPlural', { n: count });
  }

  protected apiaryTitle(apiary: Apiary): string {
    return apiary.name?.trim() || apiary.stock_number;
  }

  private lookupAddress(position: ApiaryPosition): void {
    const currentAddress = this.form.controls.address.value?.trim() ?? '';
    if (currentAddress && currentAddress !== this.lastAutoAddress) return;

    this.addressLookupPending.set(true);
    this.addressLookupMessage.set(this.translation.t('apiaries.form.addressLookup'));

    const params = new URLSearchParams({
      format: 'jsonv2',
      lat: String(position.latitude),
      lon: String(position.longitude),
      zoom: '18',
      addressdetails: '1'
    });

    fetch(`https://nominatim.openstreetmap.org/reverse?${params.toString()}`, {
      headers: { Accept: 'application/json' }
    })
      .then(response => response.ok ? response.json() : null)
      .then((result: { display_name?: string } | null) => {
        const address = result?.display_name?.trim();
        if (!address) {
          this.addressLookupMessage.set(this.translation.t('apiaries.form.addressLookupEmpty'));
          return;
        }
        this.lastAutoAddress = address;
        this.form.controls.address.setValue(address);
        this.form.controls.address.markAsDirty();
        this.addressLookupMessage.set(this.translation.t('apiaries.form.addressLookupSuccess'));
      })
      .catch(() => this.addressLookupMessage.set(this.translation.t('apiaries.form.addressLookupError')))
      .finally(() => this.addressLookupPending.set(false));
  }
}
