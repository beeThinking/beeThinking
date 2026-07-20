import { Component, inject, signal, computed, ChangeDetectionStrategy } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { HiveService } from '../../core/services/hive.service';
import { ApiaryService } from '../../core/services/apiary.service';
import { ColonyKind, Hive, HiveCreate, HiveUpdate, HiveStatus, HiveType } from '../../core/models/hive.models';
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
  protected readonly tagFilter = signal('');
  protected readonly filteredHives = computed(() => {
    const filter = this.tagFilter().trim().toLocaleLowerCase();
    if (!filter) return this.hives();
    return this.hives().filter(hive => hive.tags?.some(tag => tag.toLocaleLowerCase().includes(filter)));
  });

  protected readonly hiveTypes: HiveType[] = ['langstroth', 'dadant', 'zander', 'other'];
  protected readonly colonyKinds: ColonyKind[] = ['wirtschaftsvolk', 'ableger', 'schwarm', 'kunstschwarm', 'other'];
  protected readonly hiveStatuses: HiveStatus[] = ['active', 'inactive', 'lost', 'created_by_mistake'];

  protected readonly form = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(100)]],
    apiary_id: [null as number | null, [Validators.required]],
    stock_number: [''],
    type: ['langstroth' as HiveType],
    colony_kind: ['wirtschaftsvolk' as ColonyKind],
    status: ['active' as HiveStatus],
    established_at: [''],
    tags: [''],
    notes: ['']
  });

  protected openCreateForm(): void {
    this.editingHive.set(null);
    this.form.reset({ type: 'langstroth', colony_kind: 'wirtschaftsvolk', status: 'active' });
    this.showForm.set(true);
  }

  protected openEditForm(hive: Hive): void {
    this.editingHive.set(hive);
    this.form.setValue({
      name: hive.name,
      apiary_id: hive.apiary_id,
      stock_number: hive.stock_number ?? '',
      type: hive.type,
      colony_kind: hive.colony_kind,
      status: hive.status,
      established_at: hive.established_at ?? '',
      tags: hive.tags?.join(', ') ?? '',
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
        stock_number: values.stock_number || null,
        type: values.type as HiveType,
        colony_kind: values.colony_kind as ColonyKind,
        status: values.status as HiveStatus,
        established_at: values.established_at || null,
        tags: this.parseTags(values.tags),
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
        stock_number: values.stock_number || null,
        type: values.type as HiveType,
        colony_kind: values.colony_kind as ColonyKind,
        status: values.status as HiveStatus,
        established_at: values.established_at || null,
        tags: this.parseTags(values.tags),
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

  private parseTags(value: string | null | undefined): string[] | null {
    if (!value) return null;
    const tags = value.split(',').map(tag => tag.trim()).filter(Boolean);
    return tags.length ? tags : null;
  }

  protected colonyKindLabel(kind: ColonyKind): string {
    const key = ({
      wirtschaftsvolk: 'colonyKind.wirtschaftsvolk',
      ableger: 'colonyKind.ableger',
      schwarm: 'colonyKind.schwarm',
      kunstschwarm: 'colonyKind.kunstschwarm',
      other: 'colonyKind.other'
    } satisfies Record<ColonyKind, TranslationKey>)[kind];
    return this.translation.t(key);
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

  protected queenColor(hive: Hive): string {
    const named: Record<string, string> = {
      white: '#f7f3e8', weiss: '#f7f3e8', weiß: '#f7f3e8',
      yellow: '#f2c94c', gelb: '#f2c94c', red: '#c94b40', rot: '#c94b40',
      green: '#3f815f', grün: '#3f815f', blue: '#3977ad', blau: '#3977ad'
    };
    const explicit = hive.active_queen_color?.toLocaleLowerCase();
    if (explicit && named[explicit]) return named[explicit];
    const ending = (hive.active_queen_year ?? 0) % 5;
    return ['#3977ad', '#f7f3e8', '#f2c94c', '#c94b40', '#3f815f'][ending];
  }

  protected downloadQrSheet(): void {
    this.hiveService.getQrLabelSheet().subscribe({
      next: blob => {
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = 'bestandsliste-qr.pdf';
        anchor.click();
        URL.revokeObjectURL(url);
      },
      error: () => this.errorMessage.set(this.translation.t('beehives.error.load'))
    });
  }
}
