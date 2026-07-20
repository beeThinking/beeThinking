# BeeThinking Development Roadmap

**Goal: functional parity with BeeInTouch (beeintouch.de).** BeeThinking should support
the same beekeeping workflows one-to-one — Stockkarte-centric recording, configurable
Durchschau, queen rearing, batch traceability, regulatory registers, and sales — while
keeping its own differentiators (open source, self-hosting, PWA, Google Calendar sync,
Varroa weather, EÜR cashbook).

Sources: public site research (homepage, FAQ, app stores) **and a hands-on walkthrough
of the live BeeInTouch web app (July 2026)** — details marked "app-verified" below.

This document is the working development plan. Update it whenever priorities change or
milestones are completed — stale entries should be removed, not kept.

Status legend: ✅ done · 🔄 in progress · ⬜ planned

---

## Current State (July 2026)

Shipped and working:

- ✅ Monorepo: FastAPI backend, Angular 21 frontend, Docker Compose full stack
- ✅ JWT auth, admin roles; team apiary memberships with invitations
- ✅ Apiaries (Stände), hives (Völker) with stock card, timeline, history endpoints
- ✅ Hive lifecycle: archive, dissolve, merge; apiary batch actions
- ✅ Durchschau workflow: inspections, feedings, treatments, harvests
- ✅ Tasks/appointments with one-way Google Calendar mirroring
- ✅ Inventory (articles + items), photos (MinIO), reports (yearly, harvest, varroa, feedings)
- ✅ Cashbook with entries, receipts, EÜR summary, CSV/PDF export
- ✅ Office area: partners, documents, dashboard
- ✅ CMS content pages with admin UI
- ✅ Varroa weather (Open-Meteo provider) with per-apiary windows and hive assistant
- ✅ PWA shell (Angular service worker / ngsw), local inspection drafts (localStorage)
- ✅ Alembic migrations, CI for backend and frontend
- ✅ Queens API (backend CRUD complete — **no frontend UI yet**, see M2)

Verification baseline: 196 backend unit tests, 47 frontend tests across 12 spec files.

---

## BeeInTouch Reference Model (app-verified)

How the live app is structured — the target picture for parity work:

- **Navigation**: Stände · Lager (Lager, Chargen) · Zucht (Zuchtplanung, Zucht-Selektion)
  · Büro (Kassenbuch, ToDo-Liste, Termine, Honigpreis-Rechner, Futtermengen-Rechner,
  Bienenvolk-Selektion, Bienenvolk-Archiv, Auswertungen, plus print registers:
  Bestandsbuch, Honigbuch, Materiallager-/Fertigprodukte-Bestand, Bestandsliste mit QR,
  Kundenliste mit QR, Fütterungs-PDF).
- **Standübersicht**: map with per-Stand marker, selectable **Flugradius overlay
  (1–8 km)** and a **Trachtpflanzen layer** toggle.
- **Stand detail**: 3-day weather forecast + current conditions; Völker as card grid
  showing queen crown in **Jahresfarbe**, status traffic light, Volkart
  (Wirtschaftsvolk/Ableger), last action + date; batch buttons **Auflösen, Wandern,
  Kopieren**; drag-sortable order.
- **Stockkarte** (`Chronik des Volks`): header fields Stocknummer, Volkart, Jahresfarbe
  Königin, Königin-Zeichen, Volk erstellt, Königin zugesetzt; buttons **QR drucken**,
  Drucken (print card), Speichern. Collapsible "Weitere Daten": Rasse, Beutentyp, Linie,
  Belegstelle, structured **Beebreed-Zuchtbuchnummern** (`DE|LV|Züchter|Nr|Jahr` for
  Königin/Mutter/Drohnen), **Buckfast-Pedigree** (`B|Kasten-Nr|Züchter|Jahr`),
  Lebensnummer, Paartyp, **Stockwaage on/off toggle**. Below: per-colony analytics
  (KPI counters for Ernte kg, Fütterung kg, Durchschau/Varroakontrolle/-behandlung
  counts; chart with grouping Jahr/Monat/Woche/Tag/Stunde and date range).
- **Chronik**: vertical two-column timeline; event types **Honigernte, Durchschau,
  Varroabehandlung, Varroakontrolle, Fütterung** (Varroakontrolle = mite-count check,
  separate from treatment). Entries carry typed payloads, e.g. Behandlung: Mittel
  ("OXUVAR 5,7% ad us. vet."), Methode (Träufelmethode), Menge; Durchschau entries
  store Beutengewicht, Temperatur and a full weather snapshot (condition, hPa, humidity).
- **Durchschau form**: sections allg. Befund / Verhalten / Klima / Verschiedenes;
  6-star ratings with per-criterion disable, Ja/Nein toggles; **Temperatur + Wetter
  auto-filled from the weather service**; photo dropzone inline; Durchschaudatum;
  **"To-Do anlegen" toggle** to create a follow-up task in the same dialog.
  (Criteria set is user-configurable — the demo account showed the default subset:
  Waben/Brut, Abgeschwärmt, Königin gesehen, Sanftmut, Volksstärke.)
- **Zuchtkalender**: named Zuchtreihe with dated steps **Pflegevolk vorbereiten →
  Umlarven → Annahmekontrolle → Käfigen (1./2. Möglichkeit) → Schlupf → Völkchen
  bilden → Belegstelle → Abholen Belegstelle**; counters Anzahl Larven / angenommen /
  geschlüpft / begattet; Stand assignment; email reminder toggle.
- **Charge**: created by selecting harvest lots (Stocknummer, Stand, Erntejahr,
  Wassergehalt, Menge, Honigsorte) with grouping by Stand/Sorte/Datum/Volk.
- **Lager**: stock per Sorte + container ("Neutralglas 500 g"), Menge in Stück,
  VK-Preis, MHD, archive toggle.
- **Bienenvolk-Selektion**: filter colonies by criteria (letzte-Durchschau-Durchschnitt,
  Volksstärke, Sanftmut, Königin gesehen, Waben, Abgeschwärmt) and **Tags**, then
  batch-generate To-Dos for the matching colonies.

---

## Parity Gap Analysis (vs. BeeInTouch)

| BeeInTouch capability | BeeThinking status | Milestone |
|---|---|---|
| Digitale Stockkarte with typed Chronik | ✅ stock-card + timeline endpoints exist | M2 polish |
| Varroakontrolle (mite count) as own event type | ⬜ only treatments today | M2 |
| Wandern (migratory moves, auto-documented) | ⬜ missing | M2 |
| Kopieren (duplicate colony) | ⬜ missing | M2 |
| Umweiselung / queen data on stock card | ⬜ queens API exists, no UI/event | M2 |
| Auflösen with reason + archive filter | 🔄 dissolve exists; reason/filter UX unclear | M2 |
| Colony tags | ⬜ missing | M2 |
| Durchschau with 70+ configurable criteria | ⬜ fixed schema today | M3 |
| Custom fields + editable Auswahllisten | ⬜ missing | M3 |
| Auto temperature + weather snapshot on inspection | 🔄 weather infra exists (Varroa provider) | M3 |
| Inline follow-up To-Do from inspection dialog | ⬜ missing | M3 |
| QR per hive (print + scan → Stockkarte) | ⬜ missing | M4 |
| Offline field capture with auto-sync | 🔄 inspection drafts only, localStorage | M4 |
| Chargen from harvest lots (Wassergehalt, MHD) | ⬜ missing | M5 |
| Honigbuch (lot traceability register) | ⬜ missing | M5 |
| Bestandsbuch (TAMG register, auto from treatments) | ⬜ treatments tracked, no register output | M5 |
| Lager with VK-Preis, MHD, containers | 🔄 inventory exists, no price/MHD/container | M5/M6 |
| Sales flow: sale → stock decrement → Kassenbuch | ⬜ inventory and cashbook not linked | M6 |
| Königinnenzucht (Zuchtreihen, Kalender, Selektion) | ⬜ missing entirely | M7 |
| Beebreed/Buckfast pedigree fields (structured) | ⬜ missing | M7 |
| Per-user apiary visibility scoping in teams | 🔄 memberships exist, scoping coarse | M8 |
| Map view: Stände + Flugradius + Tracht layer | ⬜ Leaflet available, no map page | M8 |
| Per-colony analytics chart (KPIs, time grouping) | 🔄 global reports exist, nothing per hive | M8 |
| Todos: push reminder, delegation, recurrence | 🔄 tasks exist; no push, no recurrence | M8 |
| Futtermengen-/Honigpreis-Rechner | ⬜ missing (nice-to-have) | M8 |
| Stockwaage (hive scale) integration | ⬜ missing (BeeInTouch has per-colony toggle) | M8+ |
| Print pack: Bestandsliste/Kundenliste mit QR, PDFs | 🔄 some PDF export exists (cashbook) | M5/M6 |

BeeThinking differentiators to preserve (absent from BeeInTouch app and public site):
Google Calendar sync, Varroa weather windows, EÜR cashbook, PWA without app store,
open source / self-hosting, full data export.

---

## Milestone 1 — Foundation & Code Health

Goal: stable base before parity work. Debt list is grounded in a July 2026 code survey.

- ✅ Frontend test coverage: specs added for dashboard, apiaries, hive detail, cashbook,
  inventory articles and register (47 tests across 12 spec files)
- ✅ Backend test gaps: unit tests added for content (public), cashbook, feedings,
  inventory and reports; config validation covered (196 unit tests)
- ✅ Hand-written `public/sw.js` replaced with `@angular/service-worker` (ngsw)
- ✅ Dead config removed: `VARROA_WEATHER_OFFICIAL_ENDPOINT` / `_API_KEY` dropped;
  `official_varroawetter` remains a documented stub
- ✅ `GOOGLE_CALENDAR_TOKEN_KEY` now required whenever Google Calendar is enabled
  (no `SECRET_KEY` fallback for token encryption)
- ✅ Terminology unified: canonical routes `hives/*` and `apiaries/*`; legacy
  `beehives/*` and `stands/*` redirect

## Milestone 2 — Stockkarte & Colony Lifecycle Parity

Goal: the Stockkarte becomes the central object with a complete typed chronicle,
matching the app-verified Stand → Volk → Stockkarte → Chronik model.

- ✅ **Stockkarte header parity**: Stocknummer, Volkart, Volk erstellt and tags on the
  hive model and form (Jahresfarbe lives on the queen; Königin-Zeichen still open)
- ✅ **Queens UI**: active queen shown on hive detail with year/color/origin;
  requeening creates the successor (crown on apiary cards still open)
- ✅ **Varroakontrolle** as separate chronicle event type with own entity, CRUD API,
  quick-entry form and timeline integration
- ✅ **Treatment payload parity**: product/method/dosage fields already exist on the
  treatment model — verified sufficient as Bestandsbuch input (M5)
- ✅ **Umweiselung (requeening)** as chronicle event: deactivates the old queen,
  creates the new one, documents reason and date in the timeline
- ✅ **Wandern (migration)**: single move endpoint + apiary batch action, from/to
  documented as chronicle event, UI on hive detail
- ✅ **Kopieren**: duplicate colony endpoint + UI (copied master data, chronicle event)
- ✅ **Auflösen polish**: reason was already captured in the event metadata; archive
  view now filters by final status (dissolved/merged/sold/dead/lost)
- ✅ **Colony tags**: tags on model, form, hive detail; tag filter on the hive list
- ✅ Unified chronicle view: timeline merges all event types; entries editable and
  deletable in place via timeline PATCH/DELETE endpoints
- ✅ Colony card grid on apiary detail: persistable hive order (hive-order endpoint),
  batch actions Auflösen/Wandern/Kopieren, queen crown in year color on cards
- ✅ Quick-edit and delete on chronicle entries (timeline PATCH/DELETE + stock card
  quick actions)

## Milestone 3 — Configurable Durchschau

Goal: match BeeInTouch's configurable inspection form (app-verified structure:
sections allg. Befund / Verhalten / Klima / Verschiedenes; star ratings + toggles).

- ✅ Criteria catalog: per-user criteria as data, typed (stars 1–6, yes/no, number,
  text, pick list), grouped into sections; default set seeded on first access
- ✅ Per-user inspection form configuration: activate/deactivate and order criteria
  (single `inspection_criteria` table per user — no separate config table needed)
- ✅ Editable Auswahllisten: pick-list options editable per criterion in the form editor
- ✅ Custom fields: user-defined criteria (any type/section) via the form editor
- ✅ **Auto weather on inspection**: server attaches an Open-Meteo snapshot
  (condition, temperature, humidity, wind, precipitation) on create — was already
  implemented in `inspection_weather.py`, verified
- ✅ Beutengewicht (hive weight) field on inspections
- ✅ Photo upload directly in the inspection dialog (file picker, uploaded on save)
- ✅ **Inline To-Do**: toggle in the inspection dialog creates a follow-up task on
  save (title defaults to next steps)
- ✅ Migration path: fixed fields are exposed as system criteria (`field_key` link);
  the form renders one unified catalog while values stay in structured columns,
  so existing reports keep working

## Milestone 4 — QR Tagging & Offline Field Capture

Goal: seconds-fast capture at the hive, like BeeInTouch's Willi app — but as PWA.

- ⬜ QR codes per hive: "QR drucken" on the stock card (app-verified button) —
  generate/print QR labels deep-linking to `/stock-card/:hiveId`; printable label
  sheet (PDF); also Bestandsliste mit QR (all colonies, one sheet)
- ⬜ Deep links to specific dialogs: QR/URL variants that open directly in
  Durchschau/Fütterung/Behandlung dialog for that hive
- ⬜ NFC support via Web NFC API (Chrome/Android) — same deep-link targets; document
  iOS limitation (no Web NFC; QR fallback)
- ⬜ Multi-scan: scan several hives in sequence, then apply one batch action
- ⬜ Offline drafts beyond inspections: feedings, treatments, harvests (extend
  `InspectionDraftService` pattern)
- ⬜ Offline write queue: IndexedDB-backed queue for mutations made offline, replayed
  on reconnect with conflict handling (server-side change vs. offline draft)
- ⬜ Offline read cache: last known apiaries/hives/stock cards available offline
- ⬜ Background sync for photo uploads to MinIO

## Milestone 5 — Traceability & Regulatory Registers

Goal: hive→jar traceability and German compliance (app-verified flow: Ernte-Lose →
Charge → Lager → registers).

- ⬜ Harvest lots: harvest records carry Wassergehalt (moisture %), Honigsorte,
  Erntejahr, Menge — extend existing harvest model
- ⬜ **Chargen (batches)**: create a Charge by selecting harvest lots, with grouping
  by Stand/Sorte/Datum/Volk; lot number, MHD (best-before); Abfüllungen (bottlings)
  split batches into container sizes
- ⬜ Link batches to inventory: bottling creates/increments inventory items with
  container type ("Neutralglas 500 g"), VK-Preis, MHD; warehouse categories
  (Honig, Fertigprodukte, Futter, Arbeitsmaterial) as article classification
- ⬜ **Honigbuch**: generated register of harvests/batches/bottlings with lot numbers —
  view + PDF export
- ⬜ **Bestandsbuch (TAMG)**: auto-generated veterinary register from treatment records
  (Mittel, Methode, Menge, waiting period, treater — fields from M2 treatment parity) —
  view + PDF export in the officially required format (existing `journal/export`
  endpoint is the seed)
- ⬜ Traceability view: from a jar's lot number back to batch → harvest → hive → apiary
- ⬜ Print pack: Bestand Materiallager, Bestand Fertigprodukte, Fütterungs-Report as
  PDFs (BeeInTouch ships these as standard printouts)

## Milestone 6 — Sales & Cashbook Automation

Goal: BeeInTouch's cross-module automation — sale decrements stock and books income.

- ⬜ Sales records: sell inventory items (quantity, price, VAT rate, customer optional)
- ⬜ Auto stock decrement on sale; auto cashbook income entry with correct VAT
- ⬜ Simple POS view (mobile-first): pick article, quantity, price — optimized for
  market-day speed; change calculation
- ⬜ Customer/partner link: reuse existing office partners; Kundenliste mit QR printout
- ⬜ Cashbook: receipt attachments already exist — link sale receipts automatically
- ⬜ Reports: sales by article/period; EÜR summary picks up sales automatically

## Milestone 7 — Königinnenzucht (Queen Rearing)

Goal: rebuild BeeInTouch's most differentiated module (app-verified structure).

- ⬜ Breeding data on hives/queens: Rasse, Linie, Beutentyp, Lebensnummer, Paartyp,
  structured **Beebreed-Zuchtbuchnummern** (`Land|LV|Züchter|Nr|Jahr` for
  Königin/Mutter/Drohnen), **Buckfast-Pedigree** (`Pedigree|Kasten-Nr|Züchter|Jahr`),
  Belegstelle (`Land|Verband|Nummer|Durchgang`) — "Weitere Daten" panel on stock card
- ⬜ **Zuchtreihen (breeding series)**: named series with source colony and Stand
- ⬜ **Zuchtkalender**: dated steps Pflegevolk vorbereiten → Umlarven →
  Annahmekontrolle → Käfigen (1./2.) → Schlupf → Völkchen bilden → Belegstelle →
  Abholen; auto-calculate step dates from Umlarv-date
- ⬜ Series counters: Anzahl Larven, angenommen, geschlüpft, begattet — success rates
- ⬜ Reminders for breeding steps: tasks auto-created per step (feeds existing task
  system and Google Calendar sync); email/push reminder option
- ⬜ **Zucht-Selektion**: weighted scoring of colonies on inspection criteria to rank
  breeding candidates — depends on M3 criteria catalog

## Milestone 8 — Team, Map, Analytics & Utilities

Goal: round out collaboration and quality-of-life parity.

- ⬜ Per-user apiary visibility scoping: member sees all Stände or an explicit subset
  (extend membership model with apiary scope)
- ⬜ Task delegation to team members; recurring tasks/appointments
- ⬜ **Bienenvolk-Selektion**: filter colonies by criteria averages and tags, then
  batch-generate To-Dos for the matches (app-verified workflow)
- ⬜ Push notifications (Web Push) for task deadlines (1 day before) and breeding steps
- ⬜ Map view of all Stände (Leaflet already in stack): per-location weather
  (current + 3-day forecast, Open-Meteo already integrated), **Flugradius overlay
  (1–8 km selectable)**, optional Trachtpflanzen layer
- ⬜ Per-colony analytics on the stock card: KPI counters (Ernte kg, Fütterung kg,
  event counts) + chart with time grouping (Jahr/Monat/Woche/Tag/Stunde) and date range
- ⬜ Futtermengen-Rechner (winter feed calculator) — also as public CMS page (lead magnet)
- ⬜ Honigpreis-Rechner (cost/price calculator incl. per-kg and per-colony costs)
- ⬜ Two-way option for Google Calendar sync (import Google-side edits) — currently
  strictly one-way app → Google
- ⬜ (Stretch) Stockwaage integration: per-colony scale toggle + weight time series —
  BeeInTouch has the toggle; needs a scale data source (API/import) to be useful

## Milestone 9 — Production Hardening & Release

Goal: safe, boring operations.

- ⬜ Backup automation and restore drill (extend `BACKUP.md` into scripted procedure)
- ⬜ Rate limiting on auth endpoints
- ⬜ Refresh-token flow (30-minute access token forces frequent re-login — hurts
  field use especially)
- ⬜ Structured logging and basic metrics (request timing, error rates)
- ⬜ Data export: full account export (CSV/JSON) — differentiator, BeeInTouch offers none
- ⬜ First tagged release: move `CHANGELOG.md` [Unreleased] into a versioned entry

---

## Explicitly Out of Scope

- Native mobile apps — PWA + Web NFC/QR is the mobile strategy (BeeInTouch needs two
  native apps for this; we deliberately don't)
- HTML scraping of third-party weather sites — provider policy forbids it;
  `official_varroawetter` stays stubbed until an official API exists
- Multi-tenant SaaS hosting, pricing tiers, ads — single-instance, self-hosted, free
- NFC/merch hardware shop, DNA-Trachtanalyse, video academy, "Frag Willi" chatbot —
  service business, not software

## Process

- Each milestone item becomes a GitHub issue before work starts
- Milestones 2–7 each ship behind complete vertical slices (model → migration → API →
  UI → i18n de/en → tests), following the patterns in `context.md`
- Schema changes always ship with an Alembic migration
- New endpoints need at least one unit test (see `CLAUDE.md`)
- Conventional Commits; PRs run backend and frontend CI
