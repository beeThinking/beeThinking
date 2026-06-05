import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { RouterLink, ActivatedRoute } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';

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

const PAGES: Record<InfoPageKey, InfoPage> = {
  about: {
    eyebrow: 'Produkt',
    title: 'Über bee thinking',
    lead: 'bee thinking bündelt Stockkarten, Aufgaben, Ernten und Behandlungen in einer ruhigen Arbeitsoberfläche für den Imkereialltag.',
    ctaLabel: 'Dashboard öffnen',
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
    ctaLabel: 'Support lesen',
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
    eyebrow: 'Support',
    title: 'Support',
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

@Component({
  selector: 'app-info-page',
  imports: [RouterLink],
  templateUrl: './info-page.component.html',
  styleUrl: './info-page.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class InfoPageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly pageKey = toSignal(
    this.route.data.pipe(map(data => (data['page'] ?? 'about') as InfoPageKey)),
    { initialValue: 'about' as InfoPageKey }
  );

  protected readonly page = computed(() => PAGES[this.pageKey()] ?? PAGES.about);
}
