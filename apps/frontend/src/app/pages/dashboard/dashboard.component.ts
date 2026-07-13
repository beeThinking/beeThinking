import { Component, ChangeDetectionStrategy, inject, computed, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { DecimalPipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { ApiaryService } from '../../core/services/apiary.service';
import { ApiaryMember, ApiaryMemberRole } from '../../core/models/apiary.models';
import { TranslationKey } from '../../core/i18n/en';

@Component({
  selector: 'app-dashboard',
  imports: [DecimalPipe, RouterLink, TranslatePipe],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DashboardComponent {
  private readonly beekeepingService = inject(BeekeepingService);
  private readonly translation = inject(TranslationService);
  private readonly apiaryService = inject(ApiaryService);
  protected readonly invitations = signal<ApiaryMember[]>([]);
  protected readonly invitationMessage = signal('');

  constructor() {
    this.loadInvitations();
  }

  protected readonly summary = toSignal(this.beekeepingService.getDashboardSummary(), {
    initialValue: {
      apiary_count: 0,
      hive_count: 0,
      open_task_count: 0,
      overdue_task_count: 0,
      tasks_due_this_week: 0,
      treatment_count: 0,
      harvest_kg_total: 0,
      inventory_item_count: 0,
      latest_inspection_date: null,
      hives: [],
      apiaries: [],
      open_tasks: [],
      upcoming_appointments: [],
      low_inventory: []
    }
  });

  protected readonly attentionHives = computed(() =>
    this.summary().hives.filter(h => h.status !== 'active' || h.swarm_risk !== 'low').slice(0, 6)
  );

  protected formatDate(value: string | null): string {
    if (!value) return this.translation.t('dashboard.noDate');
    return new Date(value).toLocaleDateString(this.translation.currentLang() === 'de' ? 'de-DE' : 'en-US', { day: '2-digit', month: '2-digit' });
  }

  protected apiaryTitle(apiary: { stock_number: string; name: string | null }): string {
    return apiary.name?.trim() || apiary.stock_number;
  }

  protected acceptInvitation(invitation: ApiaryMember): void {
    this.apiaryService.acceptInvitation(invitation.id).subscribe({
      next: () => {
        this.invitations.update(items => items.filter(item => item.id !== invitation.id));
        this.invitationMessage.set(this.translation.t('team.invitation.accepted'));
      },
      error: () => this.invitationMessage.set(this.translation.t('team.error.accept'))
    });
  }

  protected declineInvitation(invitation: ApiaryMember): void {
    this.apiaryService.declineInvitation(invitation.id).subscribe({
      next: () => this.invitations.update(items => items.filter(item => item.id !== invitation.id)),
      error: () => this.invitationMessage.set(this.translation.t('team.error.decline'))
    });
  }

  protected roleLabel(role: ApiaryMemberRole): string {
    return this.translation.t(`team.role.${role}` as TranslationKey);
  }

  private loadInvitations(): void {
    this.apiaryService.getInvitations().subscribe({
      next: invitations => this.invitations.set(invitations),
      error: () => this.invitationMessage.set(this.translation.t('team.error.invitations'))
    });
  }
}
