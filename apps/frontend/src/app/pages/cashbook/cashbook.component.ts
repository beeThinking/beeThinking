import { CurrencyPipe, DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { forkJoin } from 'rxjs';

import { ApiaryService } from '../../core/services/apiary.service';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import {
  CashbookDirection,
  CashbookEntry,
  OfficeDashboard,
  OfficeDocument,
  OfficeDocumentStatus,
  OfficeDocumentType,
  OfficePartner,
  OfficePartnerType
} from '../../core/models/beekeeping.models';

type OfficeTab = 'overview' | 'cashbook' | 'partners' | 'receipts' | 'invoices' | 'offers' | 'exports';

const CATEGORY_LABELS: Record<string, string> = {
  honey: 'Honig',
  material: 'Arbeitsmaterial',
  products: 'Fertigprodukte',
  feed: 'Futter',
  other: 'Sonstiges',
  honey_sales: 'Honig',
  jars_labels: 'Arbeitsmaterial'
};

@Component({
  selector: 'app-cashbook',
  standalone: true,
  imports: [CurrencyPipe, DatePipe, ReactiveFormsModule],
  templateUrl: './cashbook.component.html',
  styleUrl: './cashbook.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class CashbookComponent {
  private readonly beekeeping = inject(BeekeepingService);
  private readonly apiaryService = inject(ApiaryService);
  private readonly fb = inject(FormBuilder);

  protected readonly tabs: { id: OfficeTab; label: string }[] = [
    { id: 'overview', label: 'Übersicht' },
    { id: 'cashbook', label: 'Kassenbuch' },
    { id: 'partners', label: 'Partner' },
    { id: 'receipts', label: 'Belege' },
    { id: 'invoices', label: 'Rechnungen' },
    { id: 'offers', label: 'Angebote' },
    { id: 'exports', label: 'Exporte' }
  ];
  protected readonly categories = ['honey', 'material', 'products', 'feed', 'other'];
  protected readonly months = [
    'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
  ];
  protected readonly years = computed(() => {
    const current = new Date().getFullYear();
    return Array.from({ length: 8 }, (_, index) => current - index);
  });

  protected readonly tab = signal<OfficeTab>('overview');
  protected readonly year = signal(new Date().getFullYear());
  protected readonly month = signal<number | null>(null);
  protected readonly entries = signal<CashbookEntry[]>([]);
  protected readonly dashboard = signal<OfficeDashboard>({ year: this.year(), month: null, income: 0, expenses: 0, balance: 0, monthly: [], categories: [] });
  protected readonly apiaries = signal<{ id: number; stock_number: string; name: string | null }[]>([]);
  protected readonly partners = signal<OfficePartner[]>([]);
  protected readonly documents = signal<OfficeDocument[]>([]);
  protected readonly showBookingForm = signal<CashbookDirection | null>(null);
  protected readonly showPartnerForm = signal<OfficePartnerType | null>(null);
  protected readonly showDocumentForm = signal<OfficeDocumentType | null>(null);
  protected readonly errorMessage = signal('');
  protected readonly exportPending = signal(false);

  protected readonly signedEntries = computed(() =>
    this.entries().map(entry => ({
      ...entry,
      signedAmount: entry.direction === 'income' ? entry.amount_gross : -entry.amount_gross
    }))
  );

  protected readonly visibleDocuments = computed(() => {
    const tab = this.tab();
    const type = tab === 'invoices' ? 'invoice' : tab === 'offers' ? 'offer' : tab === 'receipts' ? 'receipt' : null;
    return type ? this.documents().filter(document => document.document_type === type) : this.documents();
  });

  protected readonly bookingForm = this.fb.group({
    booking_date: [this.localDate(new Date()), Validators.required],
    direction: ['expense' as CashbookDirection, Validators.required],
    category: ['material', Validators.required],
    title: ['', Validators.required],
    invoice_number: [''],
    partner_id: [null as number | null],
    amount_gross: [0, [Validators.required, Validators.min(0)]],
    tax_rate: [0, [Validators.min(0), Validators.max(100)]],
    amount_net: [0, [Validators.required, Validators.min(0)]],
    counterparty: [''],
    payment_method: [''],
    apiary_id: [null as number | null],
    description: ['']
  });

  protected readonly partnerForm = this.fb.group({
    partner_type: ['customer' as OfficePartnerType, Validators.required],
    name: ['', Validators.required],
    email: [''],
    phone: [''],
    address: [''],
    tax_id: [''],
    notes: ['']
  });

  protected readonly documentForm = this.fb.group({
    document_type: ['invoice' as OfficeDocumentType, Validators.required],
    status: ['draft' as OfficeDocumentStatus, Validators.required],
    document_number: ['', Validators.required],
    title: ['', Validators.required],
    document_date: [this.localDate(new Date()), Validators.required],
    due_date: [''],
    partner_id: [null as number | null],
    amount_gross: [0, [Validators.required, Validators.min(0)]],
    tax_rate: [0, [Validators.min(0), Validators.max(100)]],
    amount_net: [0, [Validators.required, Validators.min(0)]],
    notes: ['']
  });

  constructor() {
    this.load();
  }

  protected setTab(tab: OfficeTab): void {
    this.tab.set(tab);
    this.errorMessage.set('');
  }

  protected load(): void {
    const year = this.year();
    const month = this.month();
    const from = this.localDate(new Date(year, month ? month - 1 : 0, 1));
    const to = this.localDate(month ? new Date(year, month, 0) : new Date(year, 11, 31));
    forkJoin({
      entries: this.beekeeping.getCashbookEntries(from, to),
      dashboard: this.beekeeping.getOfficeDashboard(year, month),
      apiaries: this.apiaryService.getApiaries(),
      partners: this.beekeeping.getOfficePartners(),
      documents: this.beekeeping.getOfficeDocuments()
    }).subscribe({
      next: result => {
        this.entries.set(result.entries);
        this.dashboard.set(result.dashboard);
        this.apiaries.set(result.apiaries.map(apiary => ({ id: apiary.id, stock_number: apiary.stock_number, name: apiary.name })));
        this.partners.set(result.partners);
        this.documents.set(result.documents);
      },
      error: () => this.errorMessage.set('Büro konnte nicht geladen werden.')
    });
  }

  protected setMonth(value: string): void {
    this.month.set(value ? Number(value) : null);
    this.load();
  }

  protected setYear(value: string): void {
    this.year.set(Number(value));
    this.load();
  }

  protected openBooking(direction: CashbookDirection): void {
    this.bookingForm.reset({
      booking_date: this.localDate(new Date()),
      direction,
      category: direction === 'income' ? 'honey' : 'material',
      amount_gross: 0,
      tax_rate: 0,
      amount_net: 0
    });
    this.showBookingForm.set(direction);
    this.setTab('cashbook');
  }

  protected saveBooking(): void {
    if (this.bookingForm.invalid) return;
    const value = this.bookingForm.value;
    const partner = value.partner_id ? this.partners().find(item => item.id === Number(value.partner_id)) : null;
    this.beekeeping.createCashbookEntry({
      booking_date: value.booking_date!,
      direction: value.direction!,
      category: value.category!,
      title: value.title || undefined,
      invoice_number: value.invoice_number || undefined,
      partner_id: value.partner_id ? Number(value.partner_id) : null,
      amount_gross: Number(value.amount_gross ?? 0),
      tax_rate: Number(value.tax_rate ?? 0),
      amount_net: Number(value.amount_net ?? 0),
      counterparty: partner?.name || value.counterparty || undefined,
      description: value.description || undefined,
      payment_method: value.payment_method || undefined,
      apiary_id: value.apiary_id ? Number(value.apiary_id) : null
    }).subscribe({
      next: () => {
        this.showBookingForm.set(null);
        this.load();
      },
      error: () => this.errorMessage.set('Buchung konnte nicht gespeichert werden.')
    });
  }

  protected savePartner(): void {
    if (this.partnerForm.invalid) return;
    const value = this.partnerForm.value;
    this.beekeeping.createOfficePartner({
      partner_type: value.partner_type!,
      name: value.name!,
      email: value.email || undefined,
      phone: value.phone || undefined,
      address: value.address || undefined,
      tax_id: value.tax_id || undefined,
      notes: value.notes || undefined
    }).subscribe({
      next: () => {
        this.showPartnerForm.set(null);
        this.partnerForm.reset({ partner_type: 'customer' });
        this.load();
      },
      error: () => this.errorMessage.set('Partner konnte nicht gespeichert werden.')
    });
  }

  protected openPartner(type: OfficePartnerType): void {
    this.partnerForm.reset({ partner_type: type });
    this.showPartnerForm.set(type);
    this.setTab('partners');
  }

  protected openDocument(type: OfficeDocumentType): void {
    this.documentForm.reset({
      document_type: type,
      status: 'draft',
      document_date: this.localDate(new Date()),
      amount_gross: 0,
      tax_rate: 0,
      amount_net: 0
    });
    this.showDocumentForm.set(type);
    this.setTab(type === 'offer' ? 'offers' : type === 'invoice' ? 'invoices' : 'receipts');
  }

  protected saveDocument(): void {
    if (this.documentForm.invalid) return;
    const value = this.documentForm.value;
    this.beekeeping.createOfficeDocument({
      document_type: value.document_type!,
      status: value.status!,
      document_number: value.document_number!,
      title: value.title!,
      document_date: value.document_date!,
      due_date: value.due_date || null,
      partner_id: value.partner_id ? Number(value.partner_id) : null,
      amount_gross: Number(value.amount_gross ?? 0),
      tax_rate: Number(value.tax_rate ?? 0),
      amount_net: Number(value.amount_net ?? 0),
      notes: value.notes || undefined,
      line_items: [{ description: value.title!, quantity: 1, unit_price: Number(value.amount_gross ?? 0), tax_rate: Number(value.tax_rate ?? 0) }]
    }).subscribe({
      next: () => {
        this.showDocumentForm.set(null);
        this.load();
      },
      error: () => this.errorMessage.set('Dokument konnte nicht gespeichert werden.')
    });
  }

  protected deleteEntry(entry: CashbookEntry): void {
    if (!confirm('Diese Buchung löschen?')) return;
    this.beekeeping.deleteCashbookEntry(entry.id).subscribe({
      next: () => this.load(),
      error: () => this.errorMessage.set('Buchung konnte nicht gelöscht werden.')
    });
  }

  protected deletePartner(partner: OfficePartner): void {
    if (!confirm(`"${partner.name}" löschen?`)) return;
    this.beekeeping.deleteOfficePartner(partner.id).subscribe({
      next: () => this.load(),
      error: () => this.errorMessage.set('Partner konnte nicht gelöscht werden.')
    });
  }

  protected deleteDocument(document: OfficeDocument): void {
    if (!confirm(`"${document.title}" löschen?`)) return;
    this.beekeeping.deleteOfficeDocument(document.id).subscribe({
      next: () => this.load(),
      error: () => this.errorMessage.set('Dokument konnte nicht gelöscht werden.')
    });
  }

  protected partnersForDirection(direction: CashbookDirection | null): OfficePartner[] {
    if (direction === 'income') return this.partners().filter(partner => partner.partner_type === 'customer');
    if (direction === 'expense') return this.partners().filter(partner => partner.partner_type === 'supplier');
    return this.partners();
  }

  protected partnerName(id: number | null): string {
    if (!id) return 'Ohne Partner';
    return this.partners().find(partner => partner.id === id)?.name ?? `Partner #${id}`;
  }

  protected apiaryName(id: number | null): string {
    if (!id) return 'Keine Imkerei';
    const apiary = this.apiaries().find(item => item.id === id);
    return apiary ? (apiary.name?.trim() || apiary.stock_number) : `Imkerei #${id}`;
  }

  protected categoryLabel(category: string): string {
    return CATEGORY_LABELS[category] ?? category;
  }

  protected periodLabel(): string {
    const month = this.month();
    return month ? this.months[month - 1] : 'Jahr';
  }

  protected documentTypeLabel(type: OfficeDocumentType): string {
    return ({ receipt: 'Beleg', invoice: 'Rechnung', offer: 'Angebot', report: 'Report' } satisfies Record<OfficeDocumentType, string>)[type];
  }

  protected documentStatusLabel(status: OfficeDocumentStatus): string {
    return ({ draft: 'Entwurf', sent: 'Gesendet', accepted: 'Angenommen', paid: 'Bezahlt', cancelled: 'Storniert' } satisfies Record<OfficeDocumentStatus, string>)[status];
  }

  protected maxMonthlyValue(): number {
    return Math.max(1, ...this.dashboard().monthly.flatMap(item => [item.income, item.expenses]));
  }

  protected barWidth(value: number): string {
    return `${Math.max(3, Math.round((value / this.maxMonthlyValue()) * 100))}%`;
  }

  protected downloadCsv(): void {
    this.downloadExport('csv');
  }

  protected downloadPdf(): void {
    this.downloadExport('pdf');
  }

  private downloadExport(type: 'csv' | 'pdf'): void {
    if (this.exportPending()) return;
    this.exportPending.set(true);
    this.errorMessage.set('');
    const request = type === 'csv'
      ? this.beekeeping.downloadOfficeCsv(this.year())
      : this.beekeeping.downloadOfficePdf(this.year());
    request.subscribe({
      next: blob => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `kassenbuch-${this.year()}.${type}`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 0);
        this.exportPending.set(false);
      },
      error: () => {
        this.errorMessage.set('Export konnte nicht heruntergeladen werden.');
        this.exportPending.set(false);
      }
    });
  }

  private localDate(value: Date): string {
    const year = value.getFullYear();
    const month = String(value.getMonth() + 1).padStart(2, '0');
    const day = String(value.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
}
