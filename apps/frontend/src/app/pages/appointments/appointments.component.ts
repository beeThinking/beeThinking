import { Component } from '@angular/core';
import { TranslatePipe } from '../../core/i18n/translate.pipe';

@Component({
  selector: 'app-appointments',
  standalone: true,
  imports: [TranslatePipe],
  templateUrl: './appointments.component.html',
  styleUrl: './appointments.component.css'
})
export class AppointmentsComponent {
}
