import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { DatePipe } from '@angular/common';
import { GoogleCalendarStatus } from '../../core/models/google-calendar.models';
import { TranslatePipe } from '../../core/i18n/translate.pipe';

@Component({
  selector: 'app-google-calendar-bridge',
  standalone: true,
  imports: [DatePipe, TranslatePipe],
  templateUrl: './google-calendar-bridge.component.html',
  styleUrl: './google-calendar-bridge.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class GoogleCalendarBridgeComponent {
  readonly status = input.required<GoogleCalendarStatus>();
  readonly loading = input(false);
  readonly connectRequested = output<void>();
  readonly syncRequested = output<void>();
  readonly disconnectRequested = output<void>();
}
