import { ChangeDetectionStrategy, Component, computed, effect, inject, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { forkJoin, map, switchMap } from 'rxjs';
import { VarroaTreatmentType, VarroaWeatherWindow } from '../../core/models/beekeeping.models';
import { ApiaryService } from '../../core/services/apiary.service';
import { HiveService } from '../../core/services/hive.service';
import { ApiaryMapPickerComponent } from '../../shared/components/apiary-map-picker.component';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { TranslationKey } from '../../core/i18n/en';
import { localDateString } from '../../core/utils/date.utils';
import { ApiaryMember, ApiaryMemberRole } from '../../core/models/apiary.models';
import { AuthService } from '../../core/services/auth.service';
import { Hive } from '../../core/models/hive.models';
import { TimelineEvent } from '../../core/models/beekeeping.models';

@Component({
  selector: 'app-apiary-detail',
  standalone: true,
  imports: [DecimalPipe, FormsModule, RouterLink, ApiaryMapPickerComponent, TranslatePipe],
  templateUrl: './apiary-detail.component.html',
  styleUrl: './apiary-detail.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ApiaryDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly apiaryService = inject(ApiaryService);
  private readonly hiveService = inject(HiveService);
  private readonly translation = inject(TranslationService);
  private readonly auth = inject(AuthService);

  protected readonly apiaryId = Number(this.route.snapshot.paramMap.get('id'));
  protected readonly apiary = toSignal(
    this.route.paramMap.pipe(map(params => Number(params.get('id'))), switchMap(id => this.apiaryService.getApiary(id))),
    { initialValue: null }
  );
  protected readonly hives = toSignal(this.hiveService.getHives(), { initialValue: [] });
  protected readonly apiaries = toSignal(this.apiaryService.getApiaries(), { initialValue: [] });
  protected readonly apiaryHives = computed(() => this.hives()
    .filter(hive => hive.apiary_id === this.apiaryId)
    .sort((a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0)));
  protected readonly hiveOrder = signal<number[]>([]);
  protected readonly orderedHives = computed(() => {
    const hives = this.apiaryHives();
    const order = this.hiveOrder();
    if (!order.length) return hives;
    return [...hives].sort((a, b) => order.indexOf(a.id) - order.indexOf(b.id));
  });
  protected readonly latestEvents = signal<Record<number, TimelineEvent | null>>({});
  protected readonly draggedHiveId = signal<number | null>(null);
  private loadedHiveSignature = '';
  protected readonly selectedTreatment = signal<VarroaTreatmentType>('formic_acid_short');
  protected readonly weatherError = signal('');
  protected readonly weatherLoading = signal(false);
  protected readonly weatherWindows = signal<VarroaWeatherWindow[]>([]);
  protected readonly batchActionType = signal<'inspection' | 'treatment' | 'feeding' | 'harvest' | 'move' | 'dissolve' | 'copy'>('inspection');
  protected readonly batchTargetApiaryId = signal<number | null>(null);
  protected readonly selectedHiveIds = signal<number[]>([]);
  protected readonly batchDate = signal(localDateString());
  protected readonly batchNotes = signal('');
  protected readonly batchAmount = signal<number | null>(null);
  protected readonly batchLabel = signal('');
  protected readonly batchSaving = signal(false);
  protected readonly batchMessage = signal('');
  protected readonly team = signal<ApiaryMember[]>([]);
  protected readonly teamLoading = signal(false);
  protected readonly teamMessage = signal('');
  protected readonly inviteIdentity = signal('');
  protected readonly inviteRole = signal<Exclude<ApiaryMemberRole, 'owner'>>('member');
  protected readonly invitePending = signal(false);
  protected readonly currentRole = computed<ApiaryMemberRole | null>(() => {
    const apiary = this.apiary();
    const user = this.auth.currentUser();
    if (!apiary || !user) return null;
    if (apiary.owner_id === user.id) return 'owner';
    return this.team().find(member => member.user_id === user.id && member.accepted_at)?.role ?? null;
  });
  protected readonly canManageTeam = computed(() => ['owner', 'admin'].includes(this.currentRole() ?? ''));

  protected readonly treatmentOptions: { value: VarroaTreatmentType; labelKey: TranslationKey }[] = [
    { value: 'formic_acid_short', labelKey: 'apiaryDetail.treatment.formicShort' },
    { value: 'formic_acid_long', labelKey: 'apiaryDetail.treatment.formicLong' },
    { value: 'thymol', labelKey: 'treatments.weather.thymol' },
    { value: 'oxalic_acid_dribble', labelKey: 'apiaryDetail.treatment.oxalicDribble' },
    { value: 'oxalic_acid_sublimation', labelKey: 'apiaryDetail.treatment.oxalicSublimation' },
    { value: 'lactic_acid', labelKey: 'apiaryDetail.treatment.lactic' },
    { value: 'biotechnical', labelKey: 'apiaryDetail.treatment.biotechnical' }
  ];

  constructor() {
    this.loadTreatment(this.selectedTreatment());
    this.loadTeam();
    effect(() => {
      const hives = this.apiaryHives();
      const signature = hives.map(hive => hive.id).join(',');
      if (!signature || signature === this.loadedHiveSignature) return;
      this.loadedHiveSignature = signature;
      this.hiveOrder.set(hives.map(hive => hive.id));
      forkJoin(hives.map(hive => this.hiveService.getHiveTimeline(hive.id))).subscribe(timelines => {
        const latest: Record<number, TimelineEvent | null> = {};
        hives.forEach((hive, index) => latest[hive.id] = timelines[index]?.[0] ?? null);
        this.latestEvents.set(latest);
      });
    });
  }

  protected loadTeam(): void {
    this.teamLoading.set(true);
    this.apiaryService.getMembers(this.apiaryId).subscribe({
      next: members => {
        this.team.set(members);
        this.teamLoading.set(false);
      },
      error: () => {
        this.teamMessage.set(this.translation.t('team.error.load'));
        this.teamLoading.set(false);
      }
    });
  }

  protected inviteMember(): void {
    const identity = this.inviteIdentity().trim();
    if (!identity || this.invitePending()) return;
    this.invitePending.set(true);
    this.teamMessage.set('');
    this.apiaryService.inviteMember(this.apiaryId, identity, this.inviteRole()).subscribe({
      next: member => {
        this.team.update(members => {
          const existing = members.findIndex(item => item.id === member.id);
          return existing === -1
            ? [...members, member]
            : members.map(item => item.id === member.id ? member : item);
        });
        this.inviteIdentity.set('');
        this.teamMessage.set(this.translation.t('team.invite.sent'));
        this.invitePending.set(false);
      },
      error: () => {
        this.teamMessage.set(this.translation.t('team.error.invite'));
        this.invitePending.set(false);
      }
    });
  }

  protected changeMemberRole(member: ApiaryMember, role: Exclude<ApiaryMemberRole, 'owner'>): void {
    this.apiaryService.updateMemberRole(this.apiaryId, member.id, role).subscribe({
      next: updated => this.team.update(members => members.map(item => item.id === updated.id ? updated : item)),
      error: () => this.teamMessage.set(this.translation.t('team.error.role'))
    });
  }

  protected removeMember(member: ApiaryMember): void {
    if (!confirm(this.translation.t('team.remove.confirm', { name: member.user.username }))) return;
    this.apiaryService.removeMember(this.apiaryId, member.id).subscribe({
      next: () => this.team.update(members => members.filter(item => item.id !== member.id)),
      error: () => this.teamMessage.set(this.translation.t('team.error.remove'))
    });
  }

  protected roleLabel(role: ApiaryMemberRole): string {
    return this.translation.t(`team.role.${role}` as TranslationKey);
  }

  protected memberInitials(member: ApiaryMember): string {
    return member.user.username.slice(0, 2).toUpperCase();
  }

  protected loadTreatment(value: VarroaTreatmentType): void {
    this.selectedTreatment.set(value);
    this.weatherLoading.set(true);
    this.weatherError.set('');
    this.apiaryService.getVarroaWeather(this.apiaryId, value).subscribe({
      next: windows => {
        this.weatherWindows.set(windows);
        this.weatherLoading.set(false);
      },
      error: () => {
        this.weatherError.set(this.translation.t('apiaryDetail.error.weatherLoad'));
        this.weatherLoading.set(false);
      }
    });
  }

  protected refreshWeather(): void {
    this.weatherLoading.set(true);
    this.weatherError.set('');
    this.apiaryService.refreshVarroaWeather(this.apiaryId).subscribe({
      next: windows => {
        const selected = this.selectedTreatment();
        this.weatherWindows.set(windows.filter(window => window.treatment_type === selected));
        this.weatherLoading.set(false);
      },
      error: () => {
        this.weatherError.set(this.translation.t('apiaryDetail.error.weatherRefresh'));
        this.weatherLoading.set(false);
      }
    });
  }

  protected formatDate(value: string): string {
    return new Date(value).toLocaleDateString(this.translation.currentLang() === 'de' ? 'de-DE' : 'en-US', { weekday: 'short', day: '2-digit', month: '2-digit' });
  }

  protected ratingLabel(rating: string): string {
    return ({
      suitable: this.translation.t('treatments.rating.suitable'),
      caution: this.translation.t('treatments.rating.caution'),
      unsuitable: this.translation.t('treatments.rating.unsuitable'),
      unknown: this.translation.t('treatments.rating.unknown')
    } as Record<string, string>)[rating] ?? rating;
  }

  protected apiaryTitle(apiary: { stock_number: string; name: string | null }): string {
    return apiary.name?.trim() || apiary.stock_number;
  }

  protected toggleHive(id: number, checked: boolean): void {
    this.selectedHiveIds.update(ids => checked ? [...new Set([...ids, id])] : ids.filter(existing => existing !== id));
  }

  protected submitBatchAction(): void {
    const hiveIds = this.selectedHiveIds();
    if (hiveIds.length === 0) {
      this.batchMessage.set('Bitte mindestens ein Volk wählen.');
      return;
    }
    this.batchSaving.set(true);
    this.batchMessage.set('');
    const action = this.batchActionType();
    const label = this.batchLabel().trim();
    const amount = this.batchAmount();
    const payload = {
      hive_ids: hiveIds,
      date: this.batchDate(),
      notes: this.batchNotes() || undefined,
      queen_seen: false,
      product: action === 'treatment' ? (label || 'Varroabehandlung') : undefined,
      feed_type: action === 'feeding' ? (label || 'Futter') : undefined,
      amount_kg_or_l: action === 'feeding' ? (amount ?? 0.1) : undefined,
      crop_type: action === 'harvest' ? (label || 'Honig') : undefined,
      amount_kg: action === 'harvest' ? (amount ?? 0) : undefined,
      target_apiary_id: action === 'move' ? (this.batchTargetApiaryId() ?? undefined) : undefined,
      reason: action === 'dissolve' ? (label || 'dissolved') : undefined
    };
    this.apiaryService.createBatchAction(this.apiaryId, action, payload).subscribe({
      next: result => {
        this.batchMessage.set(`${result.created} Einträge angelegt.`);
        this.batchSaving.set(false);
      },
      error: () => {
        this.batchMessage.set('Sammelaktion konnte nicht gespeichert werden.');
        this.batchSaving.set(false);
      }
    });
  }

  protected lastAction(hive: Hive): TimelineEvent | null {
    return this.latestEvents()[hive.id] ?? null;
  }

  protected queenColor(hive: Hive): string {
    const colors: Record<string, string> = {
      white: '#f7f3e8', weiss: '#f7f3e8', weiß: '#f7f3e8', yellow: '#f2c94c', gelb: '#f2c94c',
      red: '#c94b40', rot: '#c94b40', green: '#3f815f', grün: '#3f815f', blue: '#3977ad', blau: '#3977ad'
    };
    const explicit = hive.active_queen_color?.toLocaleLowerCase();
    if (explicit && colors[explicit]) return colors[explicit];
    return ['#3977ad', '#f7f3e8', '#f2c94c', '#c94b40', '#3f815f'][(hive.active_queen_year ?? 0) % 5] ?? '#f7f3e8';
  }

  protected dropHive(targetId: number): void {
    const sourceId = this.draggedHiveId();
    if (!sourceId || sourceId === targetId) return;
    const order = [...this.hiveOrder()];
    const sourceIndex = order.indexOf(sourceId);
    const targetIndex = order.indexOf(targetId);
    order.splice(sourceIndex, 1);
    order.splice(targetIndex, 0, sourceId);
    this.persistHiveOrder(order);
    this.draggedHiveId.set(null);
  }

  protected moveHiveInOrder(hiveId: number, direction: -1 | 1): void {
    const order = [...this.hiveOrder()];
    const index = order.indexOf(hiveId);
    const next = index + direction;
    if (index < 0 || next < 0 || next >= order.length) return;
    [order[index], order[next]] = [order[next], order[index]];
    this.persistHiveOrder(order);
  }

  private persistHiveOrder(order: number[]): void {
    this.hiveOrder.set(order);
    this.apiaryService.reorderHives(this.apiaryId, order).subscribe({
      error: () => this.batchMessage.set('Reihenfolge konnte nicht gespeichert werden.')
    });
  }
}
