import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { of, Subject } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthService } from '../../core/services/auth.service';
import { LoginComponent } from './login.component';

describe('LoginComponent', () => {
  const routerMock = {
    navigate: vi.fn(),
    createUrlTree: vi.fn().mockReturnValue({}),
    serializeUrl: vi.fn().mockReturnValue('/register'),
    events: of({})
  };

  const activatedRouteMock = {
    snapshot: {
      queryParams: {}
    }
  };

  const authServiceMock = {
    login: vi.fn().mockReturnValue(of({ access_token: 'token', token_type: 'bearer' }))
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoginComponent],
      providers: [
        { provide: Router, useValue: routerMock },
        { provide: ActivatedRoute, useValue: activatedRouteMock },
        { provide: AuthService, useValue: authServiceMock }
      ]
    }).compileComponents();

    vi.clearAllMocks();
  });

  it('should create', () => {
    // Arrange
    const fixture = TestBed.createComponent(LoginComponent);

    // Act
    const component = fixture.componentInstance;

    //Assert
    expect(component).toBeTruthy();
  });

  it('invalid login', () => {
    // Arrange
    const fixture = TestBed.createComponent(LoginComponent);

    // Act
    const component = fixture.componentInstance;
    component.onSubmit();

    // Assert
    expect(authServiceMock.login).not.toHaveBeenCalled();
  })

  it('valid login', () => {
    // Arrange
    const fixture = TestBed.createComponent(LoginComponent);

    // Act
    const component = fixture.componentInstance;
    component.loginForm.setValue({ username: 'testuser', password: 'test5678' });
    component.onSubmit();

    // Assert
    expect(authServiceMock.login).toHaveBeenCalled();
  })

  it('should call login with form username and passwort', () => {
    const fixture = TestBed.createComponent(LoginComponent);
    const component = fixture.componentInstance;
    const credentials = { username: 'testuser', password: 'test5678' };

    component.loginForm.setValue(credentials);
    component.onSubmit();

    expect(authServiceMock.login).toHaveBeenCalledTimes(1);
    expect(authServiceMock.login).toHaveBeenCalledWith(credentials);
  });

  it('should render username and password inputs with submit button', () => {
    const fixture = TestBed.createComponent(LoginComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.querySelector('#username')).toBeTruthy();
    expect(element.querySelector('#password')).toBeTruthy();
    expect(element.querySelector('button[type="submit"]')).toBeTruthy();
  });

  it('should show required field errors after invalid submit', () => {
    const fixture = TestBed.createComponent(LoginComponent);
    const component = fixture.componentInstance;

    fixture.detectChanges();
    component.onSubmit();
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('Benutzername ist erforderlich');
    expect(element.textContent).toContain('Passwort ist erforderlich');
  });

  it('should show loading state while login request is pending', () => {
    const fixture = TestBed.createComponent(LoginComponent);
    const component = fixture.componentInstance;
    const pendingLogin$ = new Subject<{ access_token: string; token_type: string }>();

    authServiceMock.login.mockReturnValue(pendingLogin$.asObservable());
    component.loginForm.setValue({ username: 'testuser', password: 'test5678' });
    component.onSubmit();
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    const submitButton = element.querySelector('button[type="submit"]') as HTMLButtonElement;

    expect(submitButton.disabled).toBe(true);
    expect(submitButton.textContent).toContain('Anmeldung läuft...');

    pendingLogin$.complete();
  });
});
