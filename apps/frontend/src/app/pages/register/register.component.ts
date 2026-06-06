import { Component, signal, inject, ChangeDetectionStrategy } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators, AbstractControl } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';

function passwordMatchValidator(control: AbstractControl) {
  const password = control.get('password')?.value;
  const confirm = control.get('confirmPassword');
  if (confirm && password !== confirm.value) {
    confirm.setErrors({ passwordMismatch: true });
    return { passwordMismatch: true };
  }
  return null;
}

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink, TranslatePipe],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class RegisterComponent {
  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly translation = inject(TranslationService);

  protected readonly errorMessage = signal('');
  protected readonly successMessage = signal('');
  protected readonly isLoading = signal(false);

  protected readonly registerForm = this.fb.group(
    {
      username: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', Validators.required]
    },
    { validators: passwordMatchValidator }
  );

  protected onSubmit(): void {
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      return;
    }
    this.isLoading.set(true);
    this.errorMessage.set('');
    this.successMessage.set('');

    const { username, email, password } = this.registerForm.value;
    this.authService.register({ username: username!, email: email!, password: password! }).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.successMessage.set(this.translation.t('register.success'));
        setTimeout(() => this.router.navigate(['/login']), 2000);
      },
      error: (error) => {
        this.isLoading.set(false);
        const detail = error.error?.detail;

        if (typeof detail === 'string') {
          // Map backend messages to specific field errors where possible
          const lower = detail.toLowerCase();
          if (lower.includes('username')) {
            this.registerForm.get('username')?.setErrors({ serverError: detail });
            this.registerForm.get('username')?.markAsTouched();
          } else if (lower.includes('email')) {
            this.registerForm.get('email')?.setErrors({ serverError: detail });
            this.registerForm.get('email')?.markAsTouched();
          } else {
            this.errorMessage.set(detail);
          }
        } else if (Array.isArray(detail)) {
          // FastAPI 422: map each error to its field if possible
          const general: string[] = [];
          for (const d of detail as Array<{ loc: string[]; msg: string }>) {
            const field = d.loc?.at(-1) as string | undefined;
            const control = field ? this.registerForm.get(field) : null;
            if (control) {
              control.setErrors({ serverError: d.msg });
              control.markAsTouched();
            } else {
              general.push(d.msg);
            }
          }
          if (general.length) this.errorMessage.set(general.join(' · '));
        } else {
          this.errorMessage.set(this.translation.t('register.error.default'));
        }
      }
    });
  }
}
