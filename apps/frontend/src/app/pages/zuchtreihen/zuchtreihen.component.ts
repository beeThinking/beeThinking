import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { BeekeepingService } from '../../core/services/beekeeping.service';
import { ApiaryService } from '../../core/services/apiary.service';
import { HiveService } from '../../core/services/hive.service';
import { Zuchtreihe, ZuchtreiheCreate, ZuchtreiheUpdate } from '../../core/models/breeding.models';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';

@Component({
  selector: 'app-zuchtreihen',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink, TranslatePipe],
  templateUrl: './zuchtreihen.component.html',
  styleUrl: './zuchtreihen.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ZuchtreihenComponent {
  private readonly beekeeping = inject(BeekeepingService);
  private readonly apiaryService = inject(ApiaryService);
  private readonly hiveService = inject(HiveService);
  private readonly fb = inject(FormBuilder);
  private readonly translation = inject(TranslationService);

  private readonly zuchtreihenData = toSignal(this.beekeeping.getZuchtreihen(), { initialValue: [] });
  private readonly localZuchtreihen = signal<Zuchtreihe[] | null>(null);

  protected readonly apiaries = toSignal(this.apiaryService.getApiaries(), { initialValue: [] });
  protected readonly hives = toSignal(this.hiveService.getHives(), { initialValue: [] });
  protected readonly zuchtreihen = computed(() => this.localZuchtreihen() ?? this.zuchtreihenData());
  protected readonly errorMessage = signal('');
  protected readonly showForm = signal(false);
  protected readonly editingZuchtreihe = signal<Zuchtreihe | null>(null);

  protected readonly form = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(200)]],
    apiary_id: [null as number | null, [Validators.required]],
    herkunftsvolk_id: [null as number | null],
    anzahl_larven: [null as number | null],
    anzahl_angenommen: [null as number | null],
    anzahl_geschluepft: [null as number | null],
    anzahl_begattet: [null as number | null],
    notes: ['']
  });

  protected openCreateForm(): void {
    this.editingZuchtreihe.set(null);
    this.form.reset();
    this.showForm.set(true);
  }

  protected openEditForm(zuchtreihe: Zuchtreihe): void {
    this.editingZuchtreihe.set(zuchtreihe);
    this.form.setValue({
      name: zuchtreihe.name,
      apiary_id: zuchtreihe.apiary_id,
      herkunftsvolk_id: zuchtreihe.herkunftsvolk_id,
      anzahl_larven: zuchtreihe.anzahl_larven,
      anzahl_angenommen: zuchtreihe.anzahl_angenommen,
      anzahl_geschluepft: zuchtreihe.anzahl_geschluepft,
      anzahl_begattet: zuchtreihe.anzahl_begattet,
      notes: zuchtreihe.notes ?? ''
    });
    this.showForm.set(true);
  }

  protected closeForm(): void {
    this.showForm.set(false);
    this.editingZuchtreihe.set(null);
    this.form.reset();
  }

  protected onSubmit(): void {
    if (this.form.invalid) return;
    const values = this.form.value;
    const editing = this.editingZuchtreihe();

    if (editing) {
      const update: ZuchtreiheUpdate = {
        name: values.name ?? undefined,
        apiary_id: values.apiary_id ?? undefined,
        herkunftsvolk_id: values.herkunftsvolk_id,
        anzahl_larven: values.anzahl_larven,
        anzahl_angenommen: values.anzahl_angenommen,
        anzahl_geschluepft: values.anzahl_geschluepft,
        anzahl_begattet: values.anzahl_begattet,
        notes: values.notes || undefined
      };
      this.beekeeping.updateZuchtreihe(editing.id, update).subscribe({
        next: updated => {
          this.localZuchtreihen.update(list => (list ?? this.zuchtreihenData()).map(z => z.id === updated.id ? updated : z));
          this.closeForm();
        },
        error: () => this.errorMessage.set(this.translation.t('zuchtreihen.error.update'))
      });
    } else {
      const create: ZuchtreiheCreate = {
        name: values.name!,
        apiary_id: values.apiary_id!,
        herkunftsvolk_id: values.herkunftsvolk_id,
        anzahl_larven: values.anzahl_larven,
        anzahl_angenommen: values.anzahl_angenommen,
        anzahl_geschluepft: values.anzahl_geschluepft,
        anzahl_begattet: values.anzahl_begattet,
        notes: values.notes || undefined
      };
      this.beekeeping.createZuchtreihe(create).subscribe({
        next: created => {
          this.localZuchtreihen.update(list => [...(list ?? this.zuchtreihenData()), created]);
          this.closeForm();
        },
        error: () => this.errorMessage.set(this.translation.t('zuchtreihen.error.create'))
      });
    }
  }

  protected deleteZuchtreihe(zuchtreihe: Zuchtreihe): void {
    if (!confirm(this.translation.t('zuchtreihen.delete.confirm', { name: zuchtreihe.name }))) return;
    this.beekeeping.deleteZuchtreihe(zuchtreihe.id).subscribe({
      next: () => this.localZuchtreihen.update(list => (list ?? this.zuchtreihenData()).filter(z => z.id !== zuchtreihe.id)),
      error: () => this.errorMessage.set(this.translation.t('zuchtreihen.error.delete'))
    });
  }

  protected apiaryName(apiaryId: number): string {
    const apiary = this.apiaries().find(a => a.id === apiaryId);
    return apiary ? (apiary.name?.trim() || apiary.stock_number) : this.translation.t('zuchtreihen.apiaryRef', { id: apiaryId });
  }

  protected hiveName(hiveId: number | null): string {
    if (!hiveId) return '–';
    return this.hives().find(h => h.id === hiveId)?.name ?? this.translation.t('zuchtreihen.hiveRef', { id: hiveId });
  }

  protected successRate(value: number | null): string {
    return value !== null ? `${value.toFixed(0)}%` : '–';
  }
}
