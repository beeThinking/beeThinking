import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  PushSubscriptionCreate,
  PushSubscriptionResponse,
  VapidPublicKeyResponse
} from '../models/push.models';

@Injectable({ providedIn: 'root' })
export class PushNotificationService {
  private readonly api = inject(ApiService);

  getVapidPublicKey(): Observable<VapidPublicKeyResponse> {
    return this.api.get<VapidPublicKeyResponse>('/api/push/vapid-public-key');
  }

  listSubscriptions(): Observable<PushSubscriptionResponse[]> {
    return this.api.get<PushSubscriptionResponse[]>('/api/push/subscriptions');
  }

  createSubscription(payload: PushSubscriptionCreate): Observable<PushSubscriptionResponse> {
    return this.api.post<PushSubscriptionResponse>('/api/push/subscriptions', payload);
  }

  deleteSubscription(id: number): Observable<void> {
    return this.api.delete<void>(`/api/push/subscriptions/${id}`);
  }
}
