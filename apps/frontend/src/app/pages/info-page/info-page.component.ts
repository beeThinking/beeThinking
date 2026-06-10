import { ChangeDetectionStrategy, Component, computed, effect, inject, signal } from '@angular/core';
import { RouterLink, ActivatedRoute } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { catchError, map, of } from 'rxjs';
import { TranslationService } from '../../core/services/translation.service';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { ContentPage } from '../../core/models/beekeeping.models';

type InfoPageKey = 'about' | 'contact' | 'docs' | 'tips' | 'faq' | 'support' | 'privacy' | 'imprint' | 'terms';

interface InfoSection {
  heading: string;
  body: string;
}

interface InfoPage {
  eyebrow: string;
  title: string;
  lead: string;
  ctaLabel?: string;
  ctaLink?: string;
  sections: InfoSection[];
}

const PAGES_DE: Record<InfoPageKey, InfoPage> = {
  about: {
    eyebrow: 'Produkt',
    title: 'Über bee thinking',
    lead: 'bee thinking bündelt Stockkarten, Aufgaben, Ernten und Behandlungen in einer ruhigen Arbeitsoberfläche für den Imkereialltag.',
    ctaLabel: 'Übersicht öffnen',
    ctaLink: '/dashboard',
    sections: [
      { heading: 'Wofür die App da ist', body: 'Die Anwendung hilft, Völker, Stände und Eingriffe nachvollziehbar zu dokumentieren. Der Fokus liegt auf schneller Erfassung am Stand und sauberer Historie für spätere Entscheidungen.' },
      { heading: 'Arbeitsweise', body: 'Planung, Kontrollen, Fotos, Varroa-Behandlungen und Archivierung bleiben miteinander verbunden. So gehen saisonale Zusammenhänge nicht in einzelnen Notizen verloren.' },
      { heading: 'Weiterentwicklung', body: 'Neue Funktionen orientieren sich an praktischen Abläufen: weniger Klickwege, klare Listen, exportierbare Nachweise und robuste Offline-Erfassung.' }
    ]
  },
  contact: {
    eyebrow: 'Kontakt',
    title: 'Kontakt aufnehmen',
    lead: 'Fragen, Fehlerberichte und fachliche Hinweise gehören direkt in den Arbeitsfluss.',
    ctaLabel: 'Hilfe lesen',
    ctaLink: '/support',
    sections: [
      { heading: 'Produktfragen', body: 'Für Fragen zur Nutzung beschreibe bitte Betriebssystem, Browser, betroffene Seite und gewünschten Ablauf. So lassen sich Probleme schneller eingrenzen.' },
      { heading: 'Fehler melden', body: 'Hilfreich sind Zeitpunkt, betroffener Datensatz, erwartetes Verhalten und ein Screenshot ohne sensible Daten.' },
      { heading: 'Betreiberangaben', body: 'Offizielle Kontakt- und Betreiberangaben werden im Impressum gepflegt, sobald die Produktivdaten feststehen.' }
    ]
  },
  docs: {
    eyebrow: 'Dokumentation',
    title: 'Dokumentation',
    lead: 'Kurze Orientierung für häufige Arbeitsbereiche in bee thinking.',
    ctaLabel: 'Völker verwalten',
    ctaLink: '/beehives',
    sections: [
      { heading: 'Völker und Stände', body: 'Lege zuerst Bienenstände an, ordne Völker zu und nutze die Detailseiten für Historie, Fotos und Lebenszyklus-Aktionen.' },
      { heading: 'Durchsichten', body: 'Durchsichten erfassen Stärke, Futter, Königinnenstatus, Schwarmrisiko und Notizen. Mobile Entwürfe bleiben lokal erhalten, bis wieder synchronisiert werden kann.' },
      { heading: 'Behandlungen', body: 'Varroa-Behandlungen können mit Wetterfenstern geplant werden. Die Wetterbewertung ist Planungshilfe und ersetzt keine Zulassungs- oder Anwendungshinweise.' }
    ]
  },
  tips: {
    eyebrow: 'Ressourcen',
    title: 'Imker-Tipps',
    lead: 'Pragmatische Hinweise für saubere Dokumentation und wiederholbare Betriebsabläufe.',
    ctaLabel: 'Aufgaben planen',
    ctaLink: '/tasks',
    sections: [
      { heading: 'Direkt am Stand erfassen', body: 'Kurze, strukturierte Einträge direkt nach der Durchsicht sind belastbarer als lange Nachträge am Abend.' },
      { heading: 'Fotos konsequent benennen', body: 'Nutze Bildnotizen für Brutbild, Futterkranz, Königin oder Schadenbild. Das macht spätere Vergleiche schneller.' },
      { heading: 'Behandlungen vorbereiten', body: 'Prüfe Wetterfenster, Volkszustand, Honigräume und zugelassene Mittel vor der Maßnahme. Dokumentiere Start, Ende und Ergebnis.' }
    ]
  },
  faq: {
    eyebrow: 'Hilfe',
    title: 'FAQ',
    lead: 'Antworten auf typische Fragen zur Nutzung.',
    ctaLabel: 'Dokumentation lesen',
    ctaLink: '/docs',
    sections: [
      { heading: 'Kann ich offline erfassen?', body: 'Mobile Durchsichtsformulare sichern Entwürfe lokal. Vollständige Synchronisation braucht wieder Netzwerkzugriff zur API.' },
      { heading: 'Sind archivierte Völker gelöscht?', body: 'Nein. Archivierte, aufgelöste, verkaufte oder zusammengelegte Völker bleiben für Historie und Jahresberichte erhalten.' },
      { heading: 'Woher kommt die Wetterbewertung?', body: 'Die App nutzt Wetterdaten und gepflegte Regeln pro Behandlungsmethode. Die Bewertung ist eine Ampel für Planung, nicht die alleinige Entscheidungsgrundlage.' }
    ]
  },
  support: {
    eyebrow: 'Hilfe',
    title: 'Hilfe',
    lead: 'Schnelle Hilfe braucht reproduzierbare Angaben.',
    ctaLabel: 'Kontakt öffnen',
    ctaLink: '/contact',
    sections: [
      { heading: 'Problem beschreiben', body: 'Nenne Seite, Aktion, Fehlermeldung, Zeitpunkt und ob es im Browser oder in Docker auftritt.' },
      { heading: 'Daten schützen', body: 'Teile keine Passwörter, Tokens oder vollständigen personenbezogenen Datensätze. Screenshots vorher prüfen.' },
      { heading: 'Technische Prüfung', body: 'Bei lokalen Installationen helfen Containerstatus, Browser-Konsole und API-Antwortcode. Das grenzt UI-, Netzwerk- und Backendfehler sauber ein.' }
    ]
  },
  privacy: {
    eyebrow: 'Rechtliches',
    title: 'Datenschutz',
    lead: 'Platzhalter für produktive Datenschutzhinweise. Vor Veröffentlichung müssen Betreiber, Zwecke, Speicherfristen und Rechtsgrundlagen geprüft werden.',
    sections: [
      { heading: 'Verarbeitete Daten', body: 'Die App kann Konto-, Standort-, Volks-, Durchsichts-, Foto-, Aufgaben-, Ernte- und Behandlungsdaten speichern.' },
      { heading: 'Zwecke', body: 'Daten werden zur Verwaltung der Imkerei, Synchronisation, Dokumentation, Auswertung und Betriebssicherheit verarbeitet.' },
      { heading: 'Hinweis', body: 'Diese Seite ist keine Rechtsberatung. Für produktiven Betrieb muss sie durch passende rechtliche Angaben ersetzt werden.' }
    ]
  },
  imprint: {
    eyebrow: 'Rechtliches',
    title: 'Impressum',
    lead: 'Platzhalter für gesetzliche Anbieterkennzeichnung.',
    sections: [
      { heading: 'Anbieter', body: 'Name, Anschrift, Vertretungsberechtigte und Kontaktwege müssen vor Veröffentlichung ergänzt werden.' },
      { heading: 'Verantwortlich', body: 'Angaben zu inhaltlich Verantwortlichen, Registernummern, Umsatzsteuer-ID oder Aufsichtsbehörde hängen vom Betreiber ab.' },
      { heading: 'Status', body: 'Diese Entwicklungsseite verhindert tote Links im Footer, ersetzt aber kein rechtlich geprüftes Impressum.' }
    ]
  },
  terms: {
    eyebrow: 'Rechtliches',
    title: 'AGB',
    lead: 'Platzhalter für Nutzungsbedingungen des produktiven Dienstes.',
    sections: [
      { heading: 'Nutzung', body: 'Die App unterstützt Imkereidokumentation. Fachliche Entscheidungen und Einhaltung gesetzlicher Vorgaben bleiben beim Anwender.' },
      { heading: 'Verfügbarkeit', body: 'Für produktiven Betrieb sollten Leistungsumfang, Backups, Wartung, Support und Datenexport verbindlich beschrieben werden.' },
      { heading: 'Hinweis', body: 'Diese Inhalte sind Entwurfstexte und müssen vor öffentlicher Nutzung juristisch geprüft werden.' }
    ]
  }
};

const PAGES_EN: Record<InfoPageKey, InfoPage> = {
  about: {
    eyebrow: 'Product',
    title: 'About bee thinking',
    lead: 'bee thinking brings hive records, tasks, harvests and treatments into one calm workspace for everyday beekeeping.',
    ctaLabel: 'Open dashboard',
    ctaLink: '/dashboard',
    sections: [
      { heading: 'What the app is for', body: 'The app helps document colonies, apiaries and interventions in a traceable way, with fast capture at the apiary and clean history for later decisions.' },
      { heading: 'Workflow', body: 'Planning, inspections, photos, varroa treatments and archiving stay connected, so seasonal context does not disappear into separate notes.' },
      { heading: 'Development', body: 'New features follow practical workflows: fewer clicks, clear lists, exportable records and robust offline capture.' }
    ]
  },
  contact: {
    eyebrow: 'Contact',
    title: 'Contact',
    lead: 'Questions, bug reports and practical feedback belong close to the workflow.',
    ctaLabel: 'Read help',
    ctaLink: '/support',
    sections: [
      { heading: 'Product questions', body: 'For usage questions, include operating system, browser, affected page and expected workflow. That makes issues easier to narrow down.' },
      { heading: 'Report bugs', body: 'Helpful details are time, affected record, expected behavior and a screenshot without sensitive data.' },
      { heading: 'Operator details', body: 'Official contact and operator details are maintained in the imprint once production data is final.' }
    ]
  },
  docs: {
    eyebrow: 'Documentation',
    title: 'Documentation',
    lead: 'Short orientation for common areas in bee thinking.',
    ctaLabel: 'Manage colonies',
    ctaLink: '/beehives',
    sections: [
      { heading: 'Colonies and apiaries', body: 'Create apiaries first, assign colonies and use detail pages for history, photos and lifecycle actions.' },
      { heading: 'Inspections', body: 'Inspections record strength, food stores, queen status, swarm risk and notes. Mobile drafts remain local until synchronization is possible.' },
      { heading: 'Treatments', body: 'Varroa treatments can be planned with weather windows. Weather assessment is planning support and does not replace label or usage instructions.' }
    ]
  },
  tips: {
    eyebrow: 'Resources',
    title: 'Beekeeper tips',
    lead: 'Practical notes for clean records and repeatable workflows.',
    ctaLabel: 'Plan tasks',
    ctaLink: '/tasks',
    sections: [
      { heading: 'Capture at the apiary', body: 'Short structured entries right after an inspection are more reliable than long notes added later.' },
      { heading: 'Name photos consistently', body: 'Use photo notes for brood pattern, food ring, queen or damage. This makes later comparison faster.' },
      { heading: 'Prepare treatments', body: 'Check weather window, colony state, honey supers and approved products before treatment. Document start, end and result.' }
    ]
  },
  faq: {
    eyebrow: 'Help',
    title: 'FAQ',
    lead: 'Answers to common usage questions.',
    ctaLabel: 'Read documentation',
    ctaLink: '/docs',
    sections: [
      { heading: 'Can I record offline?', body: 'Mobile inspection forms store drafts locally. Full synchronization needs network access to the API again.' },
      { heading: 'Are archived colonies deleted?', body: 'No. Archived, dissolved, sold or merged colonies remain available for history and annual reports.' },
      { heading: 'Where does weather assessment come from?', body: 'The app uses weather data and maintained rules per treatment method. The rating is planning support, not the sole basis for decisions.' }
    ]
  },
  support: {
    eyebrow: 'Help',
    title: 'Support',
    lead: 'Fast help needs reproducible details.',
    ctaLabel: 'Open contact',
    ctaLink: '/contact',
    sections: [
      { heading: 'Describe the problem', body: 'Include page, action, error message, time and whether it happens in the browser or in Docker.' },
      { heading: 'Protect data', body: 'Do not share passwords, tokens or full personal records. Check screenshots before sending them.' },
      { heading: 'Technical check', body: 'For local installs, container status, browser console and API status code help separate UI, network and backend issues.' }
    ]
  },
  privacy: {
    eyebrow: 'Legal',
    title: 'Privacy policy',
    lead: 'Placeholder for production privacy information. Operator, purposes, retention periods and legal bases must be checked before publication.',
    sections: [
      { heading: 'Processed data', body: 'The app can store account, location, colony, inspection, photo, task, harvest and treatment data.' },
      { heading: 'Purposes', body: 'Data is processed for apiary management, synchronization, documentation, analysis and operational reliability.' },
      { heading: 'Notice', body: 'This page is not legal advice. Production use needs matching legal content.' }
    ]
  },
  imprint: {
    eyebrow: 'Legal',
    title: 'Imprint',
    lead: 'Placeholder for legally required provider identification.',
    sections: [
      { heading: 'Provider', body: 'Name, address, representatives and contact channels must be added before publication.' },
      { heading: 'Responsible party', body: 'Content responsibility, register numbers, VAT ID or supervisory authority depend on the operator.' },
      { heading: 'Status', body: 'This development page prevents dead footer links but does not replace a legally reviewed imprint.' }
    ]
  },
  terms: {
    eyebrow: 'Legal',
    title: 'Terms',
    lead: 'Placeholder for production terms of service.',
    sections: [
      { heading: 'Use', body: 'The app supports beekeeping documentation. Technical decisions and compliance with legal requirements remain with the user.' },
      { heading: 'Availability', body: 'For production use, scope, backups, maintenance, support and data export should be described bindingly.' },
      { heading: 'Notice', body: 'These contents are drafts and must be legally reviewed before public use.' }
    ]
  }
};

@Component({
  selector: 'app-info-page',
  imports: [RouterLink],
  templateUrl: './info-page.component.html',
  styleUrl: './info-page.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class InfoPageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly translation = inject(TranslationService);
  private readonly beekeeping = inject(BeekeepingService);
  private readonly cmsPage = signal<InfoPage | null>(null);
  private readonly pageKey = toSignal(
    this.route.data.pipe(map(data => (data['page'] ?? 'about') as InfoPageKey)),
    { initialValue: 'about' as InfoPageKey }
  );

  protected readonly page = computed(() => {
    const cms = this.cmsPage();
    if (cms) return cms;
    const pages = this.translation.currentLang() === 'de' ? PAGES_DE : PAGES_EN;
    return pages[this.pageKey()] ?? pages.about;
  });

  constructor() {
    effect(() => {
      const slug = this.pageKey();
      const locale = this.translation.currentLang();
      this.beekeeping.getContentPage(slug, locale).pipe(
        map(page => this.toInfoPage(page)),
        catchError(() => of(null))
      ).subscribe(page => this.cmsPage.set(page));
    });
  }

  private toInfoPage(page: ContentPage): InfoPage {
    return {
      eyebrow: page.eyebrow ?? '',
      title: page.title,
      lead: page.lead ?? '',
      ctaLabel: page.cta_label ?? undefined,
      ctaLink: page.cta_link ?? undefined,
      sections: page.sections.map(section => ({
        heading: section.heading,
        body: section.body
      }))
    };
  }
}
