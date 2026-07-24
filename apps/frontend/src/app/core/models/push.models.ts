export interface PushSubscriptionCreate {
  endpoint: string;
  p256dh_key: string;
  auth_key: string;
  user_agent?: string;
}

export interface PushSubscriptionResponse {
  id: number;
  user_id: number;
  endpoint: string;
  created_at: string;
}

export interface VapidPublicKeyResponse {
  public_key: string | null;
  enabled: boolean;
}
