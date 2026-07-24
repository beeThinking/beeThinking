import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';

import { PushSubscriptionResponse, VapidPublicKeyResponse } from '../../core/models/push.models';
import { PushNotificationService } from '../../core/services/push-notification.service';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [TranslatePipe],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class SettingsComponent {
  private readonly push = inject(PushNotificationService);
  private readonly translation = inject(TranslationService);
  private readonly auth = inject(AuthService);

  protected readonly vapid = signal<VapidPublicKeyResponse | null>(null);
  protected readonly subscriptions = signal<PushSubscriptionResponse[]>([]);
  protected readonly loading = signal(true);
  protected readonly working = signal(false);
  protected readonly message = signal('');
  protected readonly exportWorking = signal(false);

  constructor() {
    this.load();
  }

  protected get supported(): boolean {
    return typeof navigator !== 'undefined' && 'serviceWorker' in navigator && 'PushManager' in window;
  }

  protected get enabled(): boolean {
    return this.subscriptions().length > 0;
  }

  protected async toggle(): Promise<void> {
    if (this.working()) return;
    if (!this.supported) {
      this.message.set(this.translation.t('settings.push.unsupported'));
      return;
    }
    if (this.enabled) {
      await this.unsubscribe();
      return;
    }
    await this.subscribe();
  }

  protected downloadAccountExport(): void {
    if (this.exportWorking()) return;
    this.exportWorking.set(true);
    this.message.set('');
    this.auth.downloadAccountExport().subscribe({
      next: blob => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'beethinking-account-export.zip';
        document.body.appendChild(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 0);
        this.exportWorking.set(false);
      },
      error: () => {
        this.message.set(this.translation.t('settings.export.error'));
        this.exportWorking.set(false);
      }
    });
  }

  private load(): void {
    this.push.getVapidPublicKey().subscribe({
      next: vapid => {
        this.vapid.set(vapid);
        this.push.listSubscriptions().subscribe({
          next: subscriptions => {
            this.subscriptions.set(subscriptions);
            this.loading.set(false);
          },
          error: () => {
            this.message.set(this.translation.t('settings.push.error.load'));
            this.loading.set(false);
          }
        });
      },
      error: () => {
        this.message.set(this.translation.t('settings.push.error.load'));
        this.loading.set(false);
      }
    });
  }

  private async subscribe(): Promise<void> {
    const publicKey = this.vapid()?.public_key;
    if (!this.vapid()?.enabled || !publicKey) {
      this.message.set(this.translation.t('settings.push.unavailable'));
      return;
    }
    this.working.set(true);
    try {
      const registration = await navigator.serviceWorker.ready;
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        this.message.set(this.translation.t('settings.push.permissionDenied'));
        return;
      }
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(publicKey)
      });
      const payload = subscription.toJSON();
      const p256dhKey = payload.keys?.['p256dh'];
      const authKey = payload.keys?.['auth'];
      if (!payload.endpoint || !p256dhKey || !authKey) {
        throw new Error('Invalid push subscription');
      }
      this.push.createSubscription({
        endpoint: payload.endpoint,
        p256dh_key: p256dhKey,
        auth_key: authKey,
        user_agent: navigator.userAgent
      }).subscribe({
        next: created => {
          this.subscriptions.update(items => [...items, created]);
          this.message.set(this.translation.t('settings.push.enabled'));
          this.working.set(false);
        },
        error: () => {
          this.message.set(this.translation.t('settings.push.error.save'));
          this.working.set(false);
        }
      });
    } catch {
      this.message.set(this.translation.t('settings.push.error.save'));
      this.working.set(false);
    }
  }

  private async unsubscribe(): Promise<void> {
    this.working.set(true);
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      await subscription?.unsubscribe();
      const current = [...this.subscriptions()];
      let remaining = current.length;
      for (const item of current) {
        this.push.deleteSubscription(item.id).subscribe({
          next: () => {
            remaining -= 1;
            if (remaining === 0) {
              this.subscriptions.set([]);
              this.message.set(this.translation.t('settings.push.disabled'));
              this.working.set(false);
            }
          },
          error: () => {
            this.message.set(this.translation.t('settings.push.error.save'));
            this.working.set(false);
          }
        });
      }
    } catch {
      this.message.set(this.translation.t('settings.push.error.save'));
      this.working.set(false);
    }
  }

  private urlBase64ToUint8Array(value: string): Uint8Array<ArrayBuffer> {
    const padded = value.padEnd(value.length + (4 - value.length % 4) % 4, '=');
    const base64 = padded.replace(/-/g, '+').replace(/_/g, '/');
    const raw = atob(base64);
    return Uint8Array.from(raw, character => character.charCodeAt(0)) as Uint8Array<ArrayBuffer>;
  }
}
