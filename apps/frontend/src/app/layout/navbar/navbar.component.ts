import { Component, ChangeDetectionStrategy, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, TranslatePipe],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class NavbarComponent {
  private readonly authService = inject(AuthService);
  protected readonly translation = inject(TranslationService);

  protected readonly isAuthenticated = this.authService.isAuthenticated;
  protected readonly menuOpen = signal(false);

  protected toggleMenu(): void {
    this.menuOpen.update(v => !v);
  }

  protected closeMenu(): void {
    this.menuOpen.set(false);
  }

  protected toggleLanguage(): void {
    this.translation.toggleLang();
  }

  protected logout(): void {
    this.menuOpen.set(false);
    this.authService.logout();
  }
}
