import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
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
  private readonly router = inject(Router);
  protected readonly translation = inject(TranslationService);

  protected readonly isAuthenticated = this.authService.isAuthenticated;
  protected readonly menuOpen = signal(false);
  protected readonly moreOpen = signal(false);
  protected readonly inspectionMenuOpen = signal(false);

  protected moreActive(): boolean {
    return [
      '/inventory',
      '/office',
      '/admin/content',
      '/appointments'
    ].some(path => this.router.url.startsWith(path));
  }

  protected inspectionMenuActive(): boolean {
    return [
      '/inspections',
      '/feedings',
      '/treatments',
      '/harvests'
    ].some(path => this.router.url.startsWith(path));
  }

  protected toggleMenu(): void {
    this.menuOpen.update(v => !v);
    this.moreOpen.set(false);
    this.inspectionMenuOpen.set(false);
  }

  protected closeMenu(): void {
    this.menuOpen.set(false);
    this.moreOpen.set(false);
    this.inspectionMenuOpen.set(false);
  }

  protected toggleMore(event: Event): void {
    event.stopPropagation();
    this.inspectionMenuOpen.set(false);
    this.moreOpen.update(v => !v);
  }

  protected toggleInspectionMenu(event: Event): void {
    event.stopPropagation();
    this.moreOpen.set(false);
    this.inspectionMenuOpen.update(v => !v);
  }

  protected toggleLanguage(): void {
    this.translation.toggleLang();
  }

  protected logout(): void {
    this.menuOpen.set(false);
    this.authService.logout();
  }
}
