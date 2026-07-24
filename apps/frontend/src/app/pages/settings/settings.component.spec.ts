import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { PushNotificationService } from '../../core/services/push-notification.service';
import { AuthService } from '../../core/services/auth.service';
import { SettingsComponent } from './settings.component';

describe('SettingsComponent', () => {
  const pushServiceMock = {
    getVapidPublicKey: vi.fn().mockReturnValue(of({ public_key: null, enabled: false })),
    listSubscriptions: vi.fn().mockReturnValue(of([])),
    createSubscription: vi.fn(),
    deleteSubscription: vi.fn()
  };
  const authServiceMock = { downloadAccountExport: vi.fn().mockReturnValue(of(new Blob(['zip']))) };

  beforeEach(async () => {
    vi.clearAllMocks();
    pushServiceMock.getVapidPublicKey.mockReturnValue(of({ public_key: null, enabled: false }));
    pushServiceMock.listSubscriptions.mockReturnValue(of([]));
    await TestBed.configureTestingModule({
      imports: [SettingsComponent],
      providers: [
        { provide: PushNotificationService, useValue: pushServiceMock },
        { provide: AuthService, useValue: authServiceMock }
      ]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(SettingsComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should load the VAPID configuration and subscriptions', () => {
    TestBed.createComponent(SettingsComponent);
    expect(pushServiceMock.getVapidPublicKey).toHaveBeenCalled();
    expect(pushServiceMock.listSubscriptions).toHaveBeenCalled();
  });

  it('downloads the account export', () => {
    const createObjectURL = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:export');
    const revokeObjectURL = vi.spyOn(URL, 'revokeObjectURL');
    const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);
    const fixture = TestBed.createComponent(SettingsComponent);

    fixture.componentInstance['downloadAccountExport']();

    expect(authServiceMock.downloadAccountExport).toHaveBeenCalledOnce();
    expect(createObjectURL).toHaveBeenCalledOnce();
    expect(click).toHaveBeenCalledOnce();
    expect(revokeObjectURL).not.toHaveBeenCalled();
  });
});
