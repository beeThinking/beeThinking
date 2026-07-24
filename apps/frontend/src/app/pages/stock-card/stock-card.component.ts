import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';

import { TimelineEvent } from '../../core/models/beekeeping.models';
import { Hive, Queen, QueenUpdate } from '../../core/models/hive.models';
import { HiveService } from '../../core/services/hive.service';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';

@Component({
  selector: 'app-stock-card',
  standalone: true,
  imports: [DatePipe, FormsModule, RouterLink, TranslatePipe],
  templateUrl: './stock-card.component.html',
  styleUrl: './stock-card.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class StockCardComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly hiveService = inject(HiveService);
  private readonly translation = inject(TranslationService);

  protected readonly hiveId = Number(this.route.snapshot.paramMap.get('hiveId'));
  protected readonly typeFilter = signal('all');
  protected readonly fromDate = signal('');
  protected readonly toDate = signal('');
  protected readonly stockCard = toSignal(this.hiveService.getStockCard(this.hiveId), { initialValue: null });
  protected readonly queens = toSignal(this.hiveService.getQueens(this.hiveId), { initialValue: [] });
  protected readonly hive = computed(() => this.localHive() ?? (this.stockCard()?.hive as Hive | null));
  protected readonly activeQueen = computed(() => this.queens().find(queen => queen.is_active) ?? null);
  protected readonly localEvents = signal<TimelineEvent[] | null>(null);
  protected readonly editingEvent = signal<TimelineEvent | null>(null);
  protected readonly editDate = signal('');
  protected readonly editTitle = signal('');
  protected readonly editNotes = signal('');
  protected readonly swipedEvent = signal('');
  protected readonly queenEditing = signal(false);
  protected readonly queenYear = signal(new Date().getFullYear());
  protected readonly queenColor = signal('');
  protected readonly queenMarking = signal('');
  protected readonly queenIntroducedAt = signal('');
  protected readonly queenName = signal('');
  protected readonly queenOrigin = signal('');
  protected readonly actionMessage = signal('');

  protected readonly showBreedingPanel = signal(false);
  protected readonly localHive = signal<Hive | null>(null);
  protected readonly rasse = signal('');
  protected readonly linie = signal('');
  protected readonly lebensnummer = signal('');
  protected readonly paartyp = signal('');
  protected readonly zuchtbuchnummerLand = signal('');
  protected readonly zuchtbuchnummerLv = signal('');
  protected readonly zuchtbuchnummerZuechter = signal('');
  protected readonly zuchtbuchnummerNr = signal('');
  protected readonly zuchtbuchnummerJahr = signal<number | null>(null);
  protected readonly zuchtbuchnummerMutterLand = signal('');
  protected readonly zuchtbuchnummerMutterLv = signal('');
  protected readonly zuchtbuchnummerMutterZuechter = signal('');
  protected readonly zuchtbuchnummerMutterNr = signal('');
  protected readonly zuchtbuchnummerMutterJahr = signal<number | null>(null);
  protected readonly zuchtbuchnummerDrohnenLand = signal('');
  protected readonly zuchtbuchnummerDrohnenLv = signal('');
  protected readonly zuchtbuchnummerDrohnenZuechter = signal('');
  protected readonly zuchtbuchnummerDrohnenNr = signal('');
  protected readonly zuchtbuchnummerDrohnenJahr = signal<number | null>(null);
  protected readonly pedigreePedigree = signal('');
  protected readonly pedigreeKastenNr = signal('');
  protected readonly pedigreeZuechter = signal('');
  protected readonly pedigreeJahr = signal<number | null>(null);
  protected readonly belegstelleLand = signal('');
  protected readonly belegstelleVerband = signal('');
  protected readonly belegstelleNummer = signal('');
  protected readonly belegstelleDurchgang = signal('');
  protected readonly breedingCandidate = signal(false);
  private touchStartX = 0;
  protected readonly qrUrl = computed(() => `${location.origin}${this.stockCard()?.qr_url ?? `/stock-card/${this.hiveId}`}`);
  protected readonly eventTypes = computed(() => {
    const types = new Set((this.localEvents() ?? this.stockCard()?.events ?? []).map(event => event.type));
    return ['all', ...Array.from(types)];
  });
  protected readonly events = computed(() => {
    const from = this.fromDate();
    const to = this.toDate();
    return (this.localEvents() ?? this.stockCard()?.events ?? []).filter(event => {
      if (this.typeFilter() !== 'all' && event.type !== this.typeFilter()) return false;
      if (from && event.date < from) return false;
      if (to && event.date > to) return false;
      return true;
    });
  });

  protected eventMeta(event: TimelineEvent): string {
    if (event.type === 'harvest') return `${event.amount_kg ?? 0} kg`;
    if (event.type === 'feeding') return `${event.amount_kg_or_l ?? 0} kg/l`;
    if (event.status) return event.status;
    if (event.type === 'varroa_check') return `${event.mite_count ?? '–'} Milben · ${event.mites_per_day ?? '–'}/Tag`;
    return event.type;
  }

  protected openEventEdit(event: TimelineEvent): void {
    this.editingEvent.set(event);
    this.editDate.set(event.date);
    this.editTitle.set(event.title);
    this.editNotes.set(event.notes ?? '');
  }

  protected saveEvent(): void {
    const event = this.editingEvent();
    if (!event) return;
    const payload = { date: this.editDate(), title: this.editTitle(), notes: this.editNotes() };
    this.hiveService.updateTimelineEntry(this.hiveId, event, payload).subscribe({
      next: () => {
        const source = this.localEvents() ?? this.stockCard()?.events ?? [];
        this.localEvents.set(source.map(item => item.type === event.type && item.id === event.id ? { ...item, ...payload } : item));
        this.editingEvent.set(null);
        this.actionMessage.set('Eintrag aktualisiert.');
      },
      error: () => this.actionMessage.set('Eintrag konnte nicht aktualisiert werden.')
    });
  }

  protected deleteEvent(event: TimelineEvent): void {
    if (!confirm(`„${event.title}“ aus der Chronik löschen?`)) return;
    this.hiveService.deleteTimelineEntry(this.hiveId, event).subscribe({
      next: () => {
        const source = this.localEvents() ?? this.stockCard()?.events ?? [];
        this.localEvents.set(source.filter(item => item.type !== event.type || item.id !== event.id));
        this.actionMessage.set('Eintrag gelöscht.');
      },
      error: () => this.actionMessage.set('Eintrag konnte nicht gelöscht werden.')
    });
  }

  protected touchStart(event: TouchEvent): void {
    this.touchStartX = event.touches[0]?.clientX ?? 0;
  }

  protected touchEnd(event: TouchEvent, timelineEvent: TimelineEvent): void {
    const end = event.changedTouches[0]?.clientX ?? this.touchStartX;
    if (this.touchStartX - end > 45 && (timelineEvent.editable || timelineEvent.deletable)) {
      this.swipedEvent.set(`${timelineEvent.type}-${timelineEvent.id}`);
    } else if (end - this.touchStartX > 45) {
      this.swipedEvent.set('');
    }
  }

  protected openQueenEdit(queen: Queen): void {
    this.queenYear.set(queen.year);
    this.queenColor.set(queen.marking_color ?? '');
    this.queenMarking.set(queen.marking_code ?? '');
    this.queenIntroducedAt.set(queen.introduced_at ?? '');
    this.queenName.set(queen.name ?? '');
    this.queenOrigin.set(queen.origin ?? '');
    this.queenEditing.set(true);
  }

  protected saveQueen(): void {
    const queen = this.activeQueen();
    if (!queen) return;
    this.hiveService.updateQueen(queen.id, {
      year: this.queenYear(),
      marking_color: this.queenColor() || null,
      marking_code: this.queenMarking() || null,
      introduced_at: this.queenIntroducedAt() || null,
      name: this.queenName() || null,
      origin: this.queenOrigin() || null
    }).subscribe({
      next: () => {
        queen.year = this.queenYear();
        queen.marking_color = this.queenColor() || null;
        queen.marking_code = this.queenMarking() || null;
        queen.introduced_at = this.queenIntroducedAt() || null;
        queen.name = this.queenName() || null;
        queen.origin = this.queenOrigin() || null;
        this.queenEditing.set(false);
        this.actionMessage.set('Königin aktualisiert.');
      },
      error: () => this.actionMessage.set('Königin konnte nicht aktualisiert werden.')
    });
  }

  protected printQr(): void {
    this.hiveService.getHiveQrSvg(this.hiveId).subscribe(blob => {
      blob.text().then(svg => {
        const hive = this.hive();
        const title = hive ? `${hive.name}${hive.stock_number ? ' · #' + hive.stock_number : ''}` : `Volk ${this.hiveId}`;
        const popup = window.open('', '_blank', 'width=420,height=560');
        if (!popup) return;
        popup.document.write(`<html><head><title>${title}</title><style>body{font-family:sans-serif;text-align:center;padding:24px}svg{width:280px;height:280px}</style></head><body><h2>${title}</h2>${svg}<p>${this.qrUrl()}</p></body></html>`);
        popup.document.close();
        popup.focus();
        popup.print();
      });
    });
  }

  protected openBreedingPanel(): void {
    const queen = this.activeQueen();
    const hive = this.hive();
    if (queen) {
      this.rasse.set(queen.rasse ?? '');
      this.linie.set(queen.linie ?? '');
      this.lebensnummer.set(queen.lebensnummer ?? '');
      this.paartyp.set(queen.paartyp ?? '');
      this.zuchtbuchnummerLand.set(queen.zuchtbuchnummer_land ?? '');
      this.zuchtbuchnummerLv.set(queen.zuchtbuchnummer_lv ?? '');
      this.zuchtbuchnummerZuechter.set(queen.zuchtbuchnummer_zuechter ?? '');
      this.zuchtbuchnummerNr.set(queen.zuchtbuchnummer_nr ?? '');
      this.zuchtbuchnummerJahr.set(queen.zuchtbuchnummer_jahr ?? null);
      this.zuchtbuchnummerMutterLand.set(queen.zuchtbuchnummer_mutter_land ?? '');
      this.zuchtbuchnummerMutterLv.set(queen.zuchtbuchnummer_mutter_lv ?? '');
      this.zuchtbuchnummerMutterZuechter.set(queen.zuchtbuchnummer_mutter_zuechter ?? '');
      this.zuchtbuchnummerMutterNr.set(queen.zuchtbuchnummer_mutter_nr ?? '');
      this.zuchtbuchnummerMutterJahr.set(queen.zuchtbuchnummer_mutter_jahr ?? null);
      this.zuchtbuchnummerDrohnenLand.set(queen.zuchtbuchnummer_drohnen_land ?? '');
      this.zuchtbuchnummerDrohnenLv.set(queen.zuchtbuchnummer_drohnen_lv ?? '');
      this.zuchtbuchnummerDrohnenZuechter.set(queen.zuchtbuchnummer_drohnen_zuechter ?? '');
      this.zuchtbuchnummerDrohnenNr.set(queen.zuchtbuchnummer_drohnen_nr ?? '');
      this.zuchtbuchnummerDrohnenJahr.set(queen.zuchtbuchnummer_drohnen_jahr ?? null);
      this.pedigreePedigree.set(queen.pedigree_pedigree ?? '');
      this.pedigreeKastenNr.set(queen.pedigree_kasten_nr ?? '');
      this.pedigreeZuechter.set(queen.pedigree_zuechter ?? '');
      this.pedigreeJahr.set(queen.pedigree_jahr ?? null);
      this.belegstelleLand.set(queen.belegstelle_land ?? '');
      this.belegstelleVerband.set(queen.belegstelle_verband ?? '');
      this.belegstelleNummer.set(queen.belegstelle_nummer ?? '');
      this.belegstelleDurchgang.set(queen.belegstelle_durchgang ?? '');
    }
    this.breedingCandidate.set(hive?.is_breeding_candidate ?? false);
    this.showBreedingPanel.set(true);
  }

  protected closeBreedingPanel(): void {
    this.showBreedingPanel.set(false);
  }

  protected saveBreedingData(): void {
    const queen = this.activeQueen();
    const hive = this.hive();
    if (hive) {
      this.hiveService.updateHive(hive.id, { is_breeding_candidate: this.breedingCandidate() }).subscribe({
        next: updated => {
          this.localHive.set(updated);
          this.actionMessage.set(this.translation.t('stockCard.breeding.saved'));
        },
        error: () => this.actionMessage.set(this.translation.t('stockCard.breeding.error.save'))
      });
    }
    if (queen) {
      const payload: QueenUpdate = {
        rasse: this.rasse() || null,
        linie: this.linie() || null,
        lebensnummer: this.lebensnummer() || null,
        paartyp: this.paartyp() || null,
        zuchtbuchnummer_land: this.zuchtbuchnummerLand() || null,
        zuchtbuchnummer_lv: this.zuchtbuchnummerLv() || null,
        zuchtbuchnummer_zuechter: this.zuchtbuchnummerZuechter() || null,
        zuchtbuchnummer_nr: this.zuchtbuchnummerNr() || null,
        zuchtbuchnummer_jahr: this.zuchtbuchnummerJahr(),
        zuchtbuchnummer_mutter_land: this.zuchtbuchnummerMutterLand() || null,
        zuchtbuchnummer_mutter_lv: this.zuchtbuchnummerMutterLv() || null,
        zuchtbuchnummer_mutter_zuechter: this.zuchtbuchnummerMutterZuechter() || null,
        zuchtbuchnummer_mutter_nr: this.zuchtbuchnummerMutterNr() || null,
        zuchtbuchnummer_mutter_jahr: this.zuchtbuchnummerMutterJahr(),
        zuchtbuchnummer_drohnen_land: this.zuchtbuchnummerDrohnenLand() || null,
        zuchtbuchnummer_drohnen_lv: this.zuchtbuchnummerDrohnenLv() || null,
        zuchtbuchnummer_drohnen_zuechter: this.zuchtbuchnummerDrohnenZuechter() || null,
        zuchtbuchnummer_drohnen_nr: this.zuchtbuchnummerDrohnenNr() || null,
        zuchtbuchnummer_drohnen_jahr: this.zuchtbuchnummerDrohnenJahr(),
        pedigree_pedigree: this.pedigreePedigree() || null,
        pedigree_kasten_nr: this.pedigreeKastenNr() || null,
        pedigree_zuechter: this.pedigreeZuechter() || null,
        pedigree_jahr: this.pedigreeJahr(),
        belegstelle_land: this.belegstelleLand() || null,
        belegstelle_verband: this.belegstelleVerband() || null,
        belegstelle_nummer: this.belegstelleNummer() || null,
        belegstelle_durchgang: this.belegstelleDurchgang() || null
      };
      this.hiveService.updateQueen(queen.id, payload).subscribe({
        next: updated => {
          Object.assign(queen, updated);
          this.actionMessage.set(this.translation.t('stockCard.breeding.saved'));
        },
        error: () => this.actionMessage.set(this.translation.t('stockCard.breeding.error.save'))
      });
    }
    this.showBreedingPanel.set(false);
  }
}
