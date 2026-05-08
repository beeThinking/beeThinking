import { Component, ChangeDetectionStrategy, input } from '@angular/core';

@Component({
  selector: 'app-dashboard-card',
  templateUrl: './dashboard-card.component.html',
  styleUrl: './dashboard-card.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DashboardCardComponent {
  title = input.required<string>();
  value = input.required<string | number>();
  description = input.required<string>();
  iconPath = input.required<string>();
  backgroundColor = input.required<string>();
}

