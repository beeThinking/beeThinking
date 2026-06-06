import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
@Component({
  selector: 'app-footer',
  imports: [RouterLink, TranslatePipe],
  templateUrl: './footer.component.html',
  styleUrl: './footer.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class FooterComponent {
  protected readonly year = new Date().getFullYear();
}
