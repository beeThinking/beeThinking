import { ChangeDetectionStrategy, Component, DestroyRef, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { forkJoin } from 'rxjs';
import { Hive } from '../../core/models/hive.models';
import { ApiaryService } from '../../core/services/apiary.service';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { HiveService } from '../../core/services/hive.service';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { localDateString } from '../../core/utils/date.utils';

interface NdefReaderLike {
  scan(): Promise<void>;
  write(message: unknown): Promise<void>;
  onreading: ((event: { message: { records: { recordType: string; data?: BufferSource }[] } }) => void) | null;
}

declare global {
  interface Window {
    NDEFReader?: new () => NdefReaderLike;
    BarcodeDetector?: new (options?: { formats: string[] }) => {
      detect(source: CanvasImageSource): Promise<{ rawValue: string }[]>;
    };
  }
}

type BatchAction = 'feeding' | 'treatment';

@Component({
  selector: 'app-scan',
  standalone: true,
  imports: [FormsModule, TranslatePipe],
  templateUrl: './scan.component.html',
  styleUrl: './scan.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ScanComponent {
  private readonly router = inject(Router);
  private readonly hiveService = inject(HiveService);
  private readonly apiaryService = inject(ApiaryService);
  private readonly beekeeping = inject(BeekeepingService);
  private readonly translation = inject(TranslationService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly nfcSupported = typeof window !== 'undefined' && !!window.NDEFReader;
  protected readonly cameraSupported = typeof window !== 'undefined' && !!window.BarcodeDetector
    && typeof navigator !== 'undefined' && !!navigator.mediaDevices?.getUserMedia;

  protected readonly hives = toSignal(this.hiveService.getHives(), { initialValue: [] });
  protected readonly apiaries = toSignal(this.apiaryService.getApiaries(), { initialValue: [] });

  protected readonly message = signal('');
  protected readonly errorMessage = signal('');
  protected readonly multiScan = signal(false);
  protected readonly scanning = signal(false);
  protected readonly nfcWriteHiveId = signal<number | null>(null);
  protected readonly manualHiveId = signal<number | null>(null);
  protected readonly selectedHives = signal<Hive[]>([]);
  protected readonly batchAction = signal<BatchAction>('feeding');
  protected readonly batchDate = signal(localDateString());
  protected readonly batchFeedType = signal('Futtersirup');
  protected readonly batchAmount = signal<number | null>(null);
  protected readonly batchProduct = signal('');
  protected readonly batchNotes = signal('');
  protected readonly batchPending = signal(false);

  private mediaStream: MediaStream | null = null;
  private scanTimer: ReturnType<typeof setInterval> | null = null;

  protected readonly selectedByApiary = computed(() => {
    const groups = new Map<number, Hive[]>();
    for (const hive of this.selectedHives()) {
      groups.set(hive.apiary_id, [...(groups.get(hive.apiary_id) ?? []), hive]);
    }
    return groups;
  });

  constructor() {
    this.destroyRef.onDestroy(() => this.stopCamera());
  }

  protected startNfcScan(): void {
    if (!window.NDEFReader) return;
    this.errorMessage.set('');
    const reader = new window.NDEFReader();
    reader.onreading = event => {
      for (const record of event.message.records) {
        if (record.recordType === 'url' && record.data) {
          const url = new TextDecoder().decode(record.data);
          this.handleScannedUrl(url);
          return;
        }
      }
      this.errorMessage.set(this.translation.t('scan.error.noUrl'));
    };
    reader.scan()
      .then(() => this.message.set(this.translation.t('scan.nfc.waiting')))
      .catch(() => this.errorMessage.set(this.translation.t('scan.error.nfc')));
  }

  protected writeNfcTag(): void {
    const hiveId = this.nfcWriteHiveId();
    if (!window.NDEFReader || !hiveId) return;
    this.errorMessage.set('');
    const reader = new window.NDEFReader();
    reader.write({ records: [{ recordType: 'url', data: `${location.origin}/stock-card/${hiveId}` }] })
      .then(() => this.message.set(this.translation.t('scan.nfc.written')))
      .catch(() => this.errorMessage.set(this.translation.t('scan.error.nfcWrite')));
  }

  protected async startCamera(video: HTMLVideoElement): Promise<void> {
    if (!this.cameraSupported || this.scanning()) return;
    this.errorMessage.set('');
    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      video.srcObject = this.mediaStream;
      await video.play();
      this.scanning.set(true);
      const detector = new window.BarcodeDetector!({ formats: ['qr_code'] });
      this.scanTimer = setInterval(async () => {
        try {
          const codes = await detector.detect(video);
          if (codes.length) {
            this.handleScannedUrl(codes[0].rawValue);
          }
        } catch {
          return;
        }
      }, 500);
    } catch {
      this.errorMessage.set(this.translation.t('scan.error.camera'));
    }
  }

  protected stopCamera(): void {
    if (this.scanTimer) {
      clearInterval(this.scanTimer);
      this.scanTimer = null;
    }
    this.mediaStream?.getTracks().forEach(track => track.stop());
    this.mediaStream = null;
    this.scanning.set(false);
  }

  protected handleScannedUrl(url: string): void {
    const match = url.match(/\/stock-card\/(\d+)/) ?? url.match(/\/hives\/(\d+)/);
    if (!match) {
      this.errorMessage.set(this.translation.t('scan.error.unknownCode'));
      return;
    }
    const hiveId = Number(match[1]);
    if (this.multiScan()) {
      this.addHive(hiveId);
      return;
    }
    this.stopCamera();
    this.router.navigate(['/stock-card', hiveId]);
  }

  protected addManualHive(): void {
    const hiveId = this.manualHiveId();
    if (hiveId) {
      this.addHive(hiveId);
      this.manualHiveId.set(null);
    }
  }

  private addHive(hiveId: number): void {
    const hive = this.hives().find(item => item.id === hiveId);
    if (!hive) {
      this.errorMessage.set(this.translation.t('scan.error.unknownHive'));
      return;
    }
    if (this.selectedHives().some(item => item.id === hiveId)) {
      return;
    }
    this.selectedHives.update(list => [...list, hive]);
    this.message.set(this.translation.t('scan.added', { name: hive.name }));
  }

  protected removeHive(hive: Hive): void {
    this.selectedHives.update(list => list.filter(item => item.id !== hive.id));
  }

  protected apiaryName(apiaryId: number): string {
    const apiary = this.apiaries().find(item => item.id === apiaryId);
    return apiary ? (apiary.name || apiary.stock_number) : `#${apiaryId}`;
  }

  protected runBatchAction(): void {
    const groups = this.selectedByApiary();
    if (!groups.size || this.batchPending()) return;
    const action = this.batchAction();
    if (action === 'feeding' && !this.batchAmount()) {
      this.errorMessage.set(this.translation.t('scan.error.amountMissing'));
      return;
    }
    if (action === 'treatment' && !this.batchProduct().trim()) {
      this.errorMessage.set(this.translation.t('scan.error.productMissing'));
      return;
    }
    this.batchPending.set(true);
    this.errorMessage.set('');
    const requests = Array.from(groups.entries()).map(([apiaryId, hives]) =>
      this.beekeeping.createBatchAction(apiaryId, action, {
        hive_ids: hives.map(hive => hive.id),
        date: this.batchDate(),
        notes: this.batchNotes() || undefined,
        feed_type: action === 'feeding' ? this.batchFeedType() : undefined,
        amount_kg_or_l: action === 'feeding' ? this.batchAmount() ?? undefined : undefined,
        product: action === 'treatment' ? this.batchProduct() : undefined
      })
    );
    forkJoin(requests).subscribe({
      next: results => {
        const created = results.reduce((sum, result) => sum + result.created, 0);
        this.message.set(this.translation.t('scan.batchDone', { n: String(created) }));
        this.selectedHives.set([]);
        this.batchPending.set(false);
      },
      error: () => {
        this.errorMessage.set(this.translation.t('scan.error.batch'));
        this.batchPending.set(false);
      }
    });
  }
}
