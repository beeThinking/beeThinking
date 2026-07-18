import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { of, throwError } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthService } from '../../core/services/auth.service';
import { RegisterComponent } from './register.component';

describe('RegisterComponent', () => {
  const routerMock = {
    navigate: vi.fn(),
    createUrlTree: vi.fn().mockReturnValue({}),
    serializeUrl: vi.fn().mockReturnValue('/login'),
    events: of({})
  };

  const authServiceMock = {
    register: vi.fn().mockReturnValue(of({ id: 1, username: 'beekeeper' }))
  };

  const validForm = {
    username: 'beekeeper',
    email: 'bee@example.com',
    password: 'MyBees2026!',
    confirmPassword: 'MyBees2026!'
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RegisterComponent],
      providers: [
        { provide: Router, useValue: routerMock },
        { provide: ActivatedRoute, useValue: { snapshot: { queryParams: {} } } },
        { provide: AuthService, useValue: authServiceMock }
      ]
    }).compileComponents();

    vi.clearAllMocks();
    authServiceMock.register.mockReturnValue(of({ id: 1, username: 'beekeeper' }));
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(RegisterComponent);

    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should not register with empty form', () => {
    const fixture = TestBed.createComponent(RegisterComponent);
    const component = fixture.componentInstance as unknown as { onSubmit: () => void };

    component.onSubmit();

    expect(authServiceMock.register).not.toHaveBeenCalled();
  });

  it('should reject mismatching passwords', () => {
    const fixture = TestBed.createComponent(RegisterComponent);
    const component = fixture.componentInstance as unknown as {
      onSubmit: () => void;
      registerForm: { setValue: (value: Record<string, string>) => void };
    };

    component.registerForm.setValue({ ...validForm, confirmPassword: 'different' });
    component.onSubmit();

    expect(authServiceMock.register).not.toHaveBeenCalled();
  });

  it('should register with valid form data', () => {
    const fixture = TestBed.createComponent(RegisterComponent);
    const component = fixture.componentInstance as unknown as {
      onSubmit: () => void;
      registerForm: { setValue: (value: Record<string, string>) => void };
    };

    component.registerForm.setValue(validForm);
    component.onSubmit();

    expect(authServiceMock.register).toHaveBeenCalledTimes(1);
    expect(authServiceMock.register).toHaveBeenCalledWith({
      username: validForm.username,
      email: validForm.email,
      password: validForm.password
    });
  });

  it('should show error message when registration fails', () => {
    const fixture = TestBed.createComponent(RegisterComponent);
    const component = fixture.componentInstance as unknown as {
      onSubmit: () => void;
      registerForm: { setValue: (value: Record<string, string>) => void };
    };

    authServiceMock.register.mockReturnValue(throwError(() => ({ status: 400 })));
    component.registerForm.setValue(validForm);
    component.onSubmit();
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.querySelector('.error-message, .form-error, [class*="error"]')).toBeTruthy();
  });

  it('should render registration inputs and submit button', () => {
    const fixture = TestBed.createComponent(RegisterComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.querySelectorAll('input').length).toBeGreaterThanOrEqual(4);
    expect(element.querySelector('button[type="submit"]')).toBeTruthy();
  });
});
