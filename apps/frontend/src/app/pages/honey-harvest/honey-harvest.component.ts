import { Component } from '@angular/core';
import { TranslatePipe } from '../../core/i18n/translate.pipe';

@Component({
  selector: 'app-honey-harvest',
  standalone: true,
  imports: [TranslatePipe],
  templateUrl: './honey-harvest.component.html',
  styleUrl: './honey-harvest.component.css'
})
export class HoneyHarvestComponent {
}
