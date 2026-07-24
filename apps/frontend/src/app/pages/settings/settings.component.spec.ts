import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { PushNotificationService } from '../../core/services/push-notification.service';
import { SettingsComponent } from './settings.component';

describe('SettingsComponent', () => {
  const pushServiceMock = {
    getVapidPublicKey: vi.fn().mockReturnValue(of({ public_key: null, enabled: false })),
    listSubscriptions: vi.fn().mockReturnValue(of([])),
    createSubscription: vi.fn(),
    deleteSubscription: vi.fn()
  };

  beforeEach(async () => {
    vi.clearAllMocks();
    pushServiceMock.getVapidPublicKey.mockReturnValue(of({ public_key: null, enabled: false }));
    pushServiceMock.listSubscriptions.mockReturnValue(of([]));
    await TestBed.configureTestingModule({
      imports: [SettingsComponent],
      providers: [{ provide: PushNotificationService, useValue: pushServiceMock }]
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
});
