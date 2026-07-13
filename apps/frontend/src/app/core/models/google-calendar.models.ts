export interface GoogleCalendarStatus {
  enabled: boolean;
  connected: boolean;
  calendar_name: string | null;
  last_sync_at: string | null;
  last_error: string | null;
}

export interface GoogleCalendarSyncResult {
  created: number;
  updated: number;
  deleted: number;
  synced_at: string;
}
