import { Component, signal, inject, ChangeDetectionStrategy } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, ActivatedRoute, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink, TranslatePipe],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class LoginComponent {
  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly translation = inject(TranslationService);

  private readonly returnUrl = this.route.snapshot.queryParams['returnUrl'] ?? '/dashboard';

  protected readonly errorMessage = signal('');
  protected readonly isLoading = signal(false);

  readonly loginForm = this.fb.group({
    username: ['', [Validators.required, Validators.minLength(3)]],
    password: ['', [Validators.required, Validators.minLength(8)]]
  });

  onSubmit(): void {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }
    this.isLoading.set(true);
    this.errorMessage.set('');

    const { username, password } = this.loginForm.value;
    this.authService.login({ username: username!, password: password! }).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.router.navigate([this.returnUrl]);
      },
      error: (error) => {
        this.isLoading.set(false);
        const detail = error.error?.detail;
        if (typeof detail === 'string') {
          this.errorMessage.set(detail);
        } else if (Array.isArray(detail)) {
          this.errorMessage.set(detail.map((d: { msg: string }) => d.msg).join(' · '));
        } else {
          this.errorMessage.set(this.translation.t('login.error.default'));
        }
      }
    });
  }
}
