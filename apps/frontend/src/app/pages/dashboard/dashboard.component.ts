import { Component, ChangeDetectionStrategy, inject, computed } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { DashboardCardComponent } from '../../shared/components/dashboard-card.component';
import { HiveService } from '../../core/services/hive.service';

interface DashboardCardData {
  title: string;
  value: string | number;
  description: string;
  iconPath: string;
  backgroundColor: string;
}

@Component({
  selector: 'app-dashboard',
  imports: [DashboardCardComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DashboardComponent {
  private readonly hiveService = inject(HiveService);

  private readonly hives = toSignal(this.hiveService.getHives(), { initialValue: [] });

  protected readonly cards = computed<DashboardCardData[]>(() => {
    const hives = this.hives();
    const active = hives.filter(h => h.status === 'active').length;
    return [
      {
        title: 'Bienenstöcke',
        value: hives.length,
        description: `${active} aktive Völker`,
        iconPath: 'M19 9h-2V6h3c.55 0 1 .45 1 1v2c0 .55-.45 1-1 1zm-4-3v3h-2V6h2zM9 6h2v3H9V6zM4 7c0-.55.45-1 1-1h3v3H5c-.55 0-1-.45-1-1V7zm1 10h3v3H5c-.55 0-1-.45-1-1v-2c0-.55.45-1 1-1zm6 3h-2v-3h2v3zm4 0v-3h2v3h-2zm5-3c.55 0 1 .45 1 1v2c0 .55-.45 1-1 1h-3v-3h3z',
        backgroundColor: 'var(--amelie-gold)'
      },
      {
        title: 'Honig-Ernte',
        value: '–',
        description: 'Dieses Jahr',
        iconPath: 'M12 3L1 9l11 6 9-4.91V17h2V9L12 3zM5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z',
        backgroundColor: 'var(--amelie-orange)'
      },
      {
        title: 'Nächster Termin',
        value: '–',
        description: 'Völkerkontrolle',
        iconPath: 'M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z',
        backgroundColor: 'var(--amelie-brown)'
      },
      {
        title: 'Gesundheitschecks',
        value: '–',
        description: 'Diesen Monat',
        iconPath: 'M9 11H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm2-7h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11z',
        backgroundColor: 'var(--amelie-dark-brown)'
      }
    ];
  });
}
