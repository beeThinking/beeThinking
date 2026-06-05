# BeeThinking – Codex Entwicklungsplan

Ziel: Aus dem vorhandenen BeeThinking-Projekt eine sauber self-hostbare Imkerei-Verwaltungsanwendung machen.

Aktueller Stand laut Projektstruktur:

- Frontend: Angular 21
- Backend: FastAPI / Python
- Datenbank: PostgreSQL
- ORM: SQLAlchemy
- Auth: JWT Login/Register vorhanden
- Docker Compose: vorhanden
- Bestehende Domänen: Users, Apiaries, Hives, Inspections

Wichtige Grundentscheidung: Nicht neu starten. Angular + FastAPI + PostgreSQL behalten und systematisch härten/erweitern.

---

## Umsetzungsstatus

Stand: 2026-06-05

### Erledigt

- [x] Phase 1: Projekt stabilisieren
  - [x] `docker compose up --build` geprüft.
  - [x] Backend `/health` geprüft.
  - [x] API Docs `/docs` geprüft.
  - [x] Frontend unter `http://localhost` geprüft.
  - [x] Registrierung/Login manuell im Docker-Stack geprüft.
  - [x] `DEVELOPMENT_NOTES.md` mit Start-, Port- und Testhinweisen gepflegt.
  - [x] Keine Secrets versioniert.
- [x] Phase 2: Datenbank-Migrationen sauber einführen
  - [x] Alembic konfiguriert.
  - [x] SQLAlchemy-Metadata eingebunden.
  - [x] Initiale Migration für Bestandstabellen erstellt.
  - [x] `Base.metadata.create_all(bind=engine)` entfernt.
  - [x] Docker-Start führt Migrationen aus.
  - [x] README um Migrationsbefehle ergänzt.
  - [x] PostgreSQL-Enum-Migration im Docker-Stack geprüft.
- [x] Phase 3: Security- und Auth-Härtung
  - [x] Production-Start mit unsicherem Default-Secret verhindert.
  - [x] CORS konfigurierbar gemacht.
  - [x] JWT-Ablaufzeit konfigurierbar belassen.
  - [x] Auth-Fehler vereinheitlicht.
  - [x] Ownership-Tests für Apiaries, Hives und Inspections ergänzt.
  - [x] `.env.example` mit sicheren Hinweisen ergänzt.
- [x] Phase 4: Datenmodell für echte Imkerei erweitern
  - [x] Queen-Modell erstellt.
  - [x] Task-Modell erstellt.
  - [x] Treatment-Modell erstellt.
  - [x] Harvest-Modell erstellt.
  - [x] Photo-Modell erstellt.
  - [x] Pydantic-Schemas erstellt.
  - [x] CRUD-Module erstellt.
  - [x] Alembic-Migration erstellt.
  - [x] Beziehungen und Ownership-Prüfungen ergänzt.
- [x] Phase 5: API-Routen vervollständigen
  - [x] `/api/tasks` implementiert.
  - [x] `/api/tasks/{task_id}/complete` implementiert.
  - [x] `/api/treatments` implementiert.
  - [x] `/api/harvests` implementiert.
  - [x] `/api/queens` implementiert.
  - [x] `/api/photos` implementiert.
  - [x] `/api/dashboard/summary` implementiert.
  - [x] `/api/hives/{hive_id}/timeline` implementiert.
  - [x] Routen geschützt und nutzerbezogen getestet.
- [x] Phase 6: Imker-Regellogik ins Backend
  - [x] `beekeeping_rules.py` erstellt.
  - [x] Inspection-Felder für Schwarmzellen, Stimmung, Stärke, Wetter und nächste Schritte ergänzt.
  - [x] Warnungen für alte Durchsicht, Futter, Varroa, Königin/Brut und Schwarmzellen ergänzt.
  - [x] Aufgaben nach Durchsicht automatisch erzeugt.
  - [x] Dashboard nutzt Backend-Status.
  - [x] Regeln unit-getestet.
- [x] Phase 7: Frontend: Mobile-first Kernnavigation
  - [x] Dashboard API-basiert überarbeitet.
  - [x] Völkerliste mit Status und schnellen Aktionen ergänzt.
  - [x] Volkdetail mit Timeline erstellt.
  - [x] Mobile Durchsicht erstellt.
  - [x] Aufgaben-, Ernte- und Behandlungsseiten ergänzt.
  - [x] Navigation nach Login geprüft.
- [x] Phase 8: Aufgaben-System fertigstellen
  - [x] Ansichten für Heute, Überfällig, Diese Woche, Alle offen und Erledigt umgesetzt.
  - [x] Aufgabe erstellen.
  - [x] Aufgabe bearbeiten.
  - [x] Aufgabe erledigen.
  - [x] Aufgabe löschen.
  - [x] Aufgabe mit Volk oder Standort verknüpfen.
  - [x] Automatisch erzeugte Aufgaben aus Regeln erscheinen im Aufgabenboard.
- [x] Phase 9: Foto-Upload vorbereiten und implementieren, Backend/Storage
  - [x] MinIO in Compose ergänzt.
  - [x] Backend-Konfiguration für MinIO ergänzt.
  - [x] Python S3-Client integriert.
  - [x] Upload-Endpunkt gebaut.
  - [x] Preview-Endpunkt gebaut.
  - [x] Photo-Datensatz in PostgreSQL gespeichert.
  - [x] Fotozugriff per Owner geschützt.
  - [x] Frontend-Galerie auf Volkdetail gebaut.
  - [x] Frontend-Galerie auf Durchsichten gebaut.
- [x] Phase 10: Production Deployment auf Linuxserver
  - [x] `docker-compose.prod.yml` ergänzt.
  - [x] `Caddyfile` ergänzt.
  - [x] `.env.production.example` ergänzt.
  - [x] `DEPLOYMENT.md` ergänzt.
  - [x] `BACKUP.md` ergänzt.
  - [x] Production-Compose per `docker compose config` geprüft.
- [x] Phase 11: Tests und CI verbessern
  - [x] Backend-Regeltests ergänzt.
  - [x] Auth-/Ownership-Integrationstests ergänzt.
  - [x] API-Tests für neue Kernrouten ergänzt.
  - [x] Frontend-Lint geprüft.
  - [x] Frontend-Tests geprüft.
  - [x] Frontend-Build geprüft.
  - [x] CI um Migrationen und Compose-Config-Prüfungen erweitert.

### Noch offen

- [ ] Phase 12: PWA und Offline-Entwürfe.
- [ ] Phase 17: Varroawetter-Provider und wetterbasierte Behandlungsfenster.
- [ ] Phase 29: Volk-Lebenszyklus, Historie, Archivierung und Löschen.
- [ ] PDF-Export-Felder für Behandlungsjournal aus Phase 17.
- [ ] Reports/Jahresberichte mit archivierten Völkern aus Phase 29.

---

## Arbeitsregeln für Codex

### Vor jeder Änderung

1. Repository lokal starten und Ist-Zustand prüfen.
2. `README.md`, `apps/backend/README.md`, `docker-compose.yml`, Backend-Modelle und Frontend-Routen lesen.
3. Keine Secrets committen. `.env` bleibt lokal, nur `.env.example` versionieren.
4. Vor größeren Änderungen zuerst kleinen Plan in `DEVELOPMENT_NOTES.md` ergänzen.

### Commit-Regeln

Arbeite mit kleinen, atomaren Commits. Kein großer Sammelcommit.

Commit-Format:

```text
<type>(<scope>): <kurze beschreibung>
```

Erlaubte Typen:

```text
feat     neues Feature
fix      Bugfix
refactor interne Verbesserung ohne Featureänderung
test     Tests
chore    Build, Docker, Tooling, Doku
security Sicherheitsverbesserung
```

Beispiele:

```text
chore(docker): stabilize local compose setup
refactor(db): introduce alembic migrations
feat(tasks): add task model and api routes
feat(frontend): add mobile inspection flow
security(auth): harden jwt configuration
```

Nach jeder abgeschlossenen Teilaufgabe:

```bash
git status
git add <geänderte Dateien>
git commit -m "type(scope): message"
```

Vor jedem Commit müssen, soweit möglich, diese Checks laufen:

```bash
# Backend
cd apps/backend
pytest

# Frontend
cd apps/frontend
npm run lint
npm run test -- --run
npm run build

# Full stack
cd ../..
docker compose up --build
```

Wenn ein Check aktuell projektbedingt nicht läuft, nicht ignorieren: Ursache in `DEVELOPMENT_NOTES.md` dokumentieren und möglichst beheben.

---

## Phase 1 – Projekt stabilisieren

Ziel: Das vorhandene Projekt muss lokal reproduzierbar laufen.

Aufgaben:

1. `docker compose up --build` prüfen.
2. Backend unter `http://localhost:8000/health` prüfen.
3. API Docs unter `http://localhost:8000/docs` prüfen.
4. Frontend unter `http://localhost` prüfen.
5. Registrierung/Login einmal manuell testen.
6. Falls nötig Dockerfiles, Compose, Environment-Konfiguration reparieren.
7. `DEVELOPMENT_NOTES.md` anlegen mit:
   - Startbefehlen
   - bekannten Problemen
   - verwendeten Ports
   - Testbefehlen

Akzeptanzkriterien:

- `docker compose up --build` startet Frontend, Backend und Datenbank.
- `/health` liefert `{"status":"healthy"}`.
- Ein neuer Nutzer kann sich registrieren und einloggen.
- Keine Secrets im Repository.

Commit:

```text
chore(project): document and stabilize local development setup
```

---

## Phase 2 – Datenbank-Migrationen sauber einführen

Aktuelles Problem: Das Backend nutzt `Base.metadata.create_all(bind=engine)` in `apps/backend/app/main.py`. Für Produktion ist das unsauber.

Ziel: Alembic-Migrationen statt automatischem Tabellenerzeugen.

Aufgaben:

1. Alembic korrekt konfigurieren.
2. Alle SQLAlchemy-Modelle in Alembic-Metadata einbinden.
3. Initial-Migration erstellen für:
   - users
   - apiaries
   - hives
   - inspections
4. `Base.metadata.create_all(bind=engine)` aus `main.py` entfernen.
5. Docker-Start so anpassen, dass Migrationen kontrolliert ausgeführt werden.
6. README um Migrationsbefehle erweitern.

Akzeptanzkriterien:

- Neue Datenbank kann per Alembic initialisiert werden.
- App startet ohne `create_all`.
- Migrationen sind versioniert.
- Tests laufen weiterhin.

Commit:

```text
refactor(db): replace create_all with alembic migrations
```

---

## Phase 3 – Security- und Auth-Härtung

Ziel: Die Anwendung soll sicher genug für Self-Hosting sein.

Aufgaben:

1. Prüfen, ob `SECRET_KEY` in Produktion zwingend gesetzt sein muss.
2. Unsichere Default-Secrets verhindern.
3. Passwort-Hashing prüfen und ggf. auf Argon2 oder stabile bcrypt-Konfiguration bringen.
4. CORS für Produktion einschränkbar machen.
5. JWT-Ablaufzeit konfigurierbar lassen.
6. Einheitliche Auth-Fehler zurückgeben.
7. Backend-Tests für Zugriffsschutz ergänzen:
   - Nutzer A darf Daten von Nutzer B nicht sehen.
   - Nutzer A darf fremde Hives/Apiaries/Inspections nicht ändern oder löschen.

Akzeptanzkriterien:

- App startet in Production-Modus nicht mit unsicherem Default-Secret.
- Fremdzugriffe sind per Tests abgesichert.
- `.env.example` enthält sichere Hinweise.

Commit:

```text
security(auth): harden jwt auth and ownership checks
```

---

## Phase 4 – Datenmodell für echte Imkerei erweitern

Ziel: Fehlende Kernobjekte ergänzen.

Neue Backend-Modelle:

### Queen

Felder:

```text
id
owner_id
hive_id nullable
name nullable
year
origin nullable
marking_color nullable
is_active
notes
created_at
updated_at
```

### Task

Felder:

```text
id
owner_id
hive_id nullable
apiary_id nullable
title
description nullable
due_date nullable
priority: low | medium | high | urgent
status: open | done | cancelled
source: manual | inspection | system
created_at
updated_at
completed_at nullable
```

### Treatment

Felder:

```text
id
owner_id
hive_id
started_at
ended_at nullable
product
method nullable
dosage nullable
reason nullable
notes nullable
created_at
updated_at
```

### Harvest

Felder:

```text
id
owner_id
apiary_id nullable
hive_id nullable
harvest_date
crop_type nullable
amount_kg
batch_code nullable
notes nullable
created_at
updated_at
```

### Photo

Felder:

```text
id
owner_id
hive_id nullable
inspection_id nullable
object_key
filename
content_type
size_bytes
caption nullable
created_at
```

Aufgaben:

1. SQLAlchemy-Modelle erstellen.
2. Pydantic-Schemas erstellen.
3. CRUD-Module erstellen.
4. Alembic-Migration erstellen.
5. Beziehungen sauber definieren.
6. Ownership konsequent prüfen.

Akzeptanzkriterien:

- Migration läuft sauber.
- Alle neuen Tabellen haben User-Zuordnung.
- Kein Zugriff auf fremde Daten.

Commits:

```text
feat(db): add queen task treatment harvest and photo models
feat(api): add crud and schemas for new beekeeping entities
```

---

## Phase 5 – API-Routen vervollständigen

Ziel: Backend ist als echte Verwaltungs-API nutzbar.

Neue Routen:

```text
/api/tasks
/api/tasks/{task_id}
/api/treatments
/api/treatments/{treatment_id}
/api/harvests
/api/harvests/{harvest_id}
/api/queens
/api/queens/{queen_id}
/api/photos
```

Erwartete Operationen:

```text
GET list
POST create
GET detail
PUT update
DELETE delete
```

Sonderrouten:

```text
POST /api/tasks/{task_id}/complete
GET /api/dashboard/summary
GET /api/hives/{hive_id}/timeline
```

Akzeptanzkriterien:

- OpenAPI-Doku zeigt alle Routen.
- Jede Route ist geschützt.
- Listen liefern nur Daten des eingeloggten Nutzers.
- Tests decken Create/List/Update/Delete für Kernobjekte ab.

Commits:

```text
feat(tasks): add task api routes
feat(beekeeping): add queen treatment harvest api routes
feat(dashboard): add summary and hive timeline endpoints
```

---

## Phase 6 – Imker-Regellogik ins Backend

Ziel: Die App soll nicht nur speichern, sondern Hinweise geben.

Datei anlegen:

```text
apps/backend/app/services/beekeeping_rules.py
```

Funktionen:

```python
calculate_hive_status(hive, latest_inspection) -> str
calculate_swarm_risk(hive, latest_inspection, today) -> str
get_inspection_warnings(inspection) -> list[str]
suggest_tasks_after_inspection(hive, inspection) -> list[TaskCreate]
```

Regeln zum Start:

1. Letzte Durchsicht älter als 14 Tage → Warnung.
2. Futterstatus kritisch/niedrig → Aufgabe Futter prüfen.
3. Varroa-Wert vorhanden und hoch → Warnung/Behandlung prüfen.
4. Königin nicht gesehen und Brut schwach → Weiselstatus prüfen.
5. Schwarmzellen-Feld ergänzen und bei positivem Wert → Schwarmrisiko hoch.

Dazu Inspection-Modell erweitern:

```text
swarm_cells: none | play_cups | queen_cells
mood: calm | normal | aggressive
strength: weak | medium | strong
weather nullable
next_steps nullable
```

Akzeptanzkriterien:

- Nach neuer Durchsicht können Aufgaben vorgeschlagen oder automatisch erstellt werden.
- Dashboard nutzt Backend-Status statt nur Frontend-Berechnung.
- Regeln sind unit-getestet.

Commits:

```text
feat(inspections): extend inspection fields for practical hive checks
feat(rules): add beekeeping status warnings and task suggestions
```

---

## Phase 7 – Frontend: Mobile-first Kernnavigation

Ziel: Frontend für Nutzung am Bienenstand optimieren.

Screens prüfen/überarbeiten:

```text
/dashboard
/apiaries
/beehives
/inspections
/appointments
/honey-harvest
```

Neue oder verbesserte Screens:

```text
/dashboard              Heute wichtig
/apiaries               Standorte
/apiaries/:id           Standortdetail
/beehives               Völkerliste
/beehives/:id           Volkdetail mit Timeline
/beehives/:id/inspect   Durchsicht starten
/tasks                  Aufgabenboard
/harvests               Honigernten
/treatments             Behandlungen
```

Design-Prinzipien:

1. Mobile-first.
2. Große Buttons für Durchsicht.
3. Wenig Tippen am Stand.
4. Statusfarben für Völker.
5. Schneller Zugriff auf „Durchsicht starten“.
6. Keine komplexen Tabellen auf Handy.

Akzeptanzkriterien:

- Navigation funktioniert nach Login.
- Dashboard zeigt echte API-Daten.
- Völkerliste zeigt Status, Standort, letzte Durchsicht.
- Volkdetail zeigt Stammdaten und Timeline.
- Durchsicht kann mobil schnell gespeichert werden.

Commits:

```text
feat(frontend): redesign dashboard for daily beekeeper workflow
feat(frontend): add hive detail timeline and mobile inspection flow
feat(frontend): add tasks harvests and treatments pages
```

---

## Phase 8 – Aufgaben-System fertigstellen

Ziel: Aufgaben werden zum Alltagstool.

Frontend-Ansichten:

```text
Heute
Überfällig
Diese Woche
Alle offen
Erledigt
```

Funktionen:

1. Aufgabe erstellen.
2. Aufgabe bearbeiten.
3. Aufgabe erledigen.
4. Aufgabe löschen.
5. Aufgabe mit Volk oder Standort verknüpfen.
6. Automatisch vorgeschlagene Aufgaben nach Durchsicht anzeigen.

Akzeptanzkriterien:

- Überfällige Aufgaben werden klar markiert.
- Aufgaben können mit einem Klick erledigt werden.
- Aufgaben aus Imker-Regeln erscheinen nachvollziehbar.

Commit:

```text
feat(tasks): implement beekeeper task board
```

---

## Phase 9 – Foto-Upload vorbereiten und implementieren

Ziel: Fotos von Durchsichten/Völkern speichern.

Empfohlene Self-Hosting-Lösung: MinIO.

Aufgaben:

1. `minio` Service in `docker-compose.yml` ergänzen.
2. Backend-Konfiguration für MinIO ergänzen.
3. Python S3-Client integrieren.
4. Upload-Endpunkt bauen.
5. Download/Preview-Endpunkt oder signierte URLs bauen.
6. Photo-Datensatz in PostgreSQL speichern.
7. Frontend-Galerie auf Volkdetail und Durchsichtdetail bauen.

Akzeptanzkriterien:

- Foto kann hochgeladen werden.
- Foto ist einem Hive oder einer Inspection zugeordnet.
- Nutzer kann keine fremden Fotos sehen.
- MinIO-Daten werden persistent gespeichert.

Commits:

```text
chore(storage): add minio service for self-hosted photo storage
feat(photos): implement secure hive and inspection photo uploads
```

---

## Phase 10 – Production Deployment auf Linuxserver

Ziel: Sauberes Self-Hosting.

Dateien ergänzen:

```text
docker-compose.prod.yml
Caddyfile
.env.production.example
DEPLOYMENT.md
BACKUP.md
```

Production-Services:

```text
caddy
frontend
backend
postgres
minio
```

Caddy-Aufgaben:

1. HTTPS automatisch für Domain.
2. `/api/*` an Backend weiterleiten.
3. Frontend ausliefern.
4. Optional `/minio` nicht öffentlich machen, falls nicht nötig.

Backup-Konzept:

1. PostgreSQL Dump.
2. MinIO-Daten sichern.
3. `.env` separat sichern.
4. Restore-Anleitung dokumentieren.

Akzeptanzkriterien:

- Eine Domain kann über Caddy genutzt werden.
- Production-Compose nutzt keine Dev-Reloads.
- Keine Ports unnötig öffentlich.
- Deployment-Anleitung funktioniert auf Ubuntu Server.

Commits:

```text
chore(deploy): add production docker compose with caddy
chore(docs): add linux server deployment and backup guide
```

---

## Phase 11 – Tests und CI verbessern

Ziel: Änderungen bleiben stabil.

Backend:

1. Unit-Tests für Regeln.
2. Integrationstests für Auth und Ownership.
3. API-Tests für neue Routen.
4. Testdaten-Factorys vereinfachen.

Frontend:

1. Build muss laufen.
2. Lint muss laufen.
3. Kritische Services testen.
4. Mindestens Smoke-Tests für Login/Dashboard.

CI:

1. GitHub Actions prüfen.
2. Backend-Workflow reparieren/erweitern.
3. Frontend-Workflow reparieren/erweitern.
4. Docker-Build optional prüfen.

Akzeptanzkriterien:

- Pull Requests zeigen Backend- und Frontend-Checks.
- Hauptfeatures sind nicht mehr komplett ungetestet.

Commits:

```text
test(backend): cover ownership and beekeeping rules
test(frontend): add smoke tests for core pages
chore(ci): update backend and frontend workflows
```

---

## Phase 12 – PWA und Offline-Entwürfe

Ziel: Am Bienenstand nutzbar, auch bei schlechtem Netz.

Nicht sofort vollständig offline-first bauen. Erst einfache Entwürfe.

Aufgaben:

1. Angular PWA einrichten.
2. App-Icon und Manifest ergänzen.
3. Durchsicht-Entwürfe lokal speichern.
4. Entwurf später absenden.
5. Nutzer klar anzeigen, ob Daten synchronisiert wurden.

Akzeptanzkriterien:

- App kann auf Handy zum Home-Bildschirm hinzugefügt werden.
- Eine begonnene Durchsicht geht bei Netzproblem nicht sofort verloren.

Commit:

```text
feat(pwa): add installable app shell and offline inspection drafts
```

---

## Fehlende Features – priorisierte Liste

### Muss für MVP

1. Saubere Migrationen.
2. Sichere User-Zuordnung überall.
3. Dashboard mit echten Daten.
4. Völkerliste und Volkdetail.
5. Mobile Durchsicht.
6. Aufgaben.
7. Production-Docker-Setup.

### Sollte danach kommen

1. Königinnenverwaltung.
2. Behandlungen.
3. Honigernte und Chargen.
4. Foto-Upload.
5. Imker-Regellogik.
6. Backup/Restore-Doku.

### Später

1. PWA/Offline-Entwürfe.
2. Wetterintegration.
3. Push-Erinnerungen.
4. QR-Code für Honig-Chargen.
5. KI-Auswertungen.
6. Mehrbenutzer/Familie/Verein.

---

## Empfohlene Umsetzungsreihenfolge

Strikt in dieser Reihenfolge arbeiten:

```text
1. Projekt stabilisieren
2. Alembic-Migrationen
3. Security/Ownership-Tests
4. Datenmodell erweitern
5. API-Routen
6. Dashboard + mobile Durchsicht
7. Aufgaben
8. Production Deployment
9. Fotos/MinIO
10. Behandlungen/Honig/Königinnen im Frontend abrunden
11. Tests/CI verbessern
12. PWA/Offline
```

Nicht mit KI, Wetter oder App-Store starten.

---

## Definition of Done pro Phase

Eine Phase gilt nur als fertig, wenn:

1. Code kompiliert/läuft.
2. Tests wurden ausgeführt oder begründet dokumentiert.
3. Docker-Setup ist nicht kaputt.
4. README/Docs sind angepasst, wenn Bedienung oder Setup betroffen sind.
5. Kein Secret wurde committet.
6. Es gibt mindestens einen sauberen Commit zur Phase.

---

## Startprompt für Codex CLI

Nutze diesen Prompt, um Codex mit der Arbeit beginnen zu lassen:

```text
Du arbeitest im bestehenden beeThinking Repository.
Lies zuerst CODEX_IMPLEMENTATION_PLAN.md vollständig.
Starte mit Phase 1 und arbeite strikt in kleinen, atomaren Commits.
Vor jedem Commit führe passende Tests/Builds aus und dokumentiere Probleme in DEVELOPMENT_NOTES.md.
Verändere keine Secrets und committe keine .env Dateien.
Wenn eine Phase fertig ist, erstelle einen sauberen Conventional Commit und fahre mit der nächsten Phase fort.
Beginne jetzt mit Phase 1: Projekt stabilisieren.
```

---

## Phase 17 – Varroawetter-Provider und wetterbasierte Behandlungsfenster

Ziel: Die App soll wetterabhängige Varroa-Behandlungsfenster je Standort anzeigen und in den normalen Prozess integrieren. Sie darf keine verbindliche tierärztliche Behandlungsanweisung geben, sondern nur eine nachvollziehbare Planungshilfe mit Quellen-/Datenhinweis.

Fachlicher Hintergrund:

- Ameisensäure- und Thymol-Anwendungen sind stark von Temperatur und teils Luftfeuchte abhängig.
- Bei zu niedrigen Temperaturen kann die Wirkung zu gering sein.
- Bei zu hohen Temperaturen können Schäden am Volk entstehen.
- Oxalsäure-Anwendungen hängen nicht nur vom Wetter ab, sondern besonders von Brutfreiheit, Methode, Zulassung und Packungsbeilage.
- Externe Varroawetter-Dienste zeigen standort-/regionbezogene Fenster für geeignete, kritische oder ungeeignete Anwendungstage.

Wichtige Architekturentscheidung:

Nicht direkt Logik hart ins Frontend schreiben. Stattdessen ein Backend-Provider-System bauen.

Provider-Konzept:

```text
app/services/varroa_weather/
  base.py
  internal_rules_provider.py
  open_meteo_provider.py
  official_varroawetter_provider.py
  schemas.py
```

Konfiguration:

```text
VARROA_WEATHER_PROVIDER=internal_rules|open_meteo|official_varroawetter|disabled
VARROA_WEATHER_CACHE_TTL_HOURS=6
VARROA_WEATHER_OFFICIAL_ENDPOINT=
VARROA_WEATHER_OFFICIAL_API_KEY=
```

Hinweis zu offiziellen Varroawetter-Daten:

Codex soll prüfen, ob für den gewünschten Dienst eine offiziell dokumentierte API oder erlaubte Datenquelle existiert. Falls keine API dokumentiert ist, darf keine fragile HTML-Scraping-Lösung als Standard gebaut werden. Stattdessen:

1. Provider-Schnittstelle vorbereiten.
2. Offiziellen Provider als Stub mit klarer Fehlermeldung implementieren.
3. Interne Regeln mit Open-Meteo-Wetterdaten als Fallback nutzen.
4. In der README dokumentieren, wie ein offizieller Endpoint später eingetragen wird.

Datenmodell ergänzen:

```text
varroa_weather_windows
- id
- apiary_id
- source
- provider_version
- treatment_type
- date
- rating: suitable | caution | unsuitable | unknown
- reason
- min_temperature
- max_temperature
- avg_humidity
- precipitation_probability
- wind_speed
- raw_payload_json
- fetched_at
- created_at
```

Behandlungstypen:

```text
formic_acid_short
formic_acid_long
thymol
oxalic_acid_dribble
oxalic_acid_sublimation
lactic_acid
biotechnical
other
```

Backend-Funktionen:

```text
get_varroa_weather_window(apiary_id, treatment_type, start_date, days=5)
refresh_varroa_weather_windows(apiary_id)
rate_treatment_weather_window(weather_day, treatment_type)
suggest_best_treatment_days(apiary_id, treatment_type)
```

API-Endpunkte:

```text
GET  /api/apiaries/{apiary_id}/varroa-weather
POST /api/apiaries/{apiary_id}/varroa-weather/refresh
GET  /api/hives/{hive_id}/varroa-assistant
```

Frontend:

1. Standortdetailseite zeigt "Varroa-Wetterfenster" für die nächsten Tage.
2. Varroa-Assistent zeigt je Behandlungstyp eine Ampel:
   - Grün: Wetterfenster wahrscheinlich geeignet
   - Gelb: kritisch, Details prüfen
   - Rot: ungeeignet
   - Grau: keine Daten
3. Beim Erstellen eines Behandlungsvorgangs wird das aktuelle Wetterfenster angezeigt.
4. Beim Speichern einer Behandlung wird das verwendete Wetterfenster im Behandlungsjournal gespeichert.
5. PDF-Export des Behandlungsjournals enthält Wetterquelle, Abrufzeitpunkt und Bewertung.

Beispiel-UI:

```text
Varroa-Wetter – Waldstand

Heute
Ameisensäure: kritisch
Grund: erwartete Höchsttemperatur zu hoch

Morgen
Ameisensäure: geeignet
Thymol: geeignet
Oxalsäure: Wetter ok, Brutfreiheit separat prüfen

[Behandlung planen]
[Wetterdaten aktualisieren]
```

Sicherheits- und Haftungstexte:

Die App muss bei Empfehlungen immer anzeigen:

```text
Diese Anzeige ist eine Planungshilfe. Bitte Zulassung, Packungsbeilage, regionale Empfehlungen und Volkzustand prüfen.
```

Keine Formulierungen wie:

```text
Jetzt behandeln.
```

Stattdessen:

```text
Wetterfenster wirkt geeignet. Behandlung prüfen/planen.
```

Codex-Aufgaben:

```text
Implementiere ein Provider-System für Varroa-Wetterfenster im FastAPI Backend.
Erstelle zuerst einen internen Provider, der Open-Meteo-Wetterdaten verwendet und daraus grobe Ampelbewertungen je Behandlungstyp erzeugt.
Baue die Schnittstelle so, dass später ein offizieller Varroawetter-API-Provider eingehängt werden kann.
Baue keinen HTML-Scraper als Standard.
Speichere berechnete Fenster gecacht in PostgreSQL.
Zeige die Wetterfenster im Angular-Frontend auf Standortdetailseite und im Varroa-Assistenten.
Ergänze Sicherheitshinweise und PDF-Export-Felder im Behandlungsjournal.
```

Akzeptanzkriterien:

- Varroa-Wetterfenster können pro Standort abgerufen werden.
- Daten werden gecacht und nicht bei jedem Seitenaufruf neu geladen.
- Provider ist per ENV umschaltbar.
- Kein HTML-Scraping ohne explizite Aktivierung und Dokumentation.
- Behandlungsvorgänge speichern die verwendete Wetterbewertung.
- PDF-Behandlungsjournal enthält Wetterfenster, Quelle und Abrufzeitpunkt.
- Frontend zeigt eine Ampel je Behandlungstyp.
- Nutzer sieht einen klaren Hinweis, dass es eine Planungshilfe ist.

Commit-Vorschläge:

```text
feat(varroa-weather): add provider interface and cached weather windows
feat(varroa-weather): add api endpoints for treatment weather windows
feat(frontend): show varroa weather windows in apiary view
feat(treatments): store weather context in treatment journal
feat(exports): include varroa weather context in treatment pdf
```

---

## Phase 29 – Volk-Lebenszyklus, Historie, Archivierung und Löschen

Ziel: Jedes Volk soll eine vollständige, nachvollziehbare Lebensgeschichte haben. Auflösen, Vereinigen, Umweiseln, Wandern, Archivieren und Löschen müssen sauber dokumentiert werden, ohne historische Nachweise zu verlieren.

### Grundprinzip

Ein Volk soll nicht einfach verschwinden, sobald es nicht mehr aktiv ist. Standard ist:

```text
Aktives Volk → aufgelöst / verkauft / vereinigt / verstorben → automatisch archiviert
```

Physisches Löschen ist nur als bewusste Ausnahme für Fehleingaben vorgesehen.

### Hive-Status erweitern

Erweitere den Volkstatus um:

```text
active
archived
dissolved
merged
sold
dead
lost
created_by_mistake
```

Empfehlung:

- `active`: normales aktives Volk
- `archived`: nicht mehr aktiv, aber historisch sichtbar
- `dissolved`: aufgelöst, z. B. abgekehrt oder vereinigt
- `merged`: in anderes Volk vereinigt
- `sold`: verkauft/abgegeben
- `dead`: tot eingewintert/ausgewintert/verendet
- `lost`: verloren, z. B. Königin/Volk nicht mehr vorhanden
- `created_by_mistake`: Fehleingabe, darf später hart gelöscht werden

### Allgemeine Volk-Historie

Führe eine zentrale Historie/Timeline je Volk ein. Sie soll alle relevanten Ereignisse enthalten oder referenzieren:

```text
- Volk erstellt
- Standortwechsel / Wandern
- Durchsicht
- Fütterung
- Behandlung
- Ernte
- Königin zugesetzt / gewechselt / verloren
- Ableger gebildet
- Volk vereinigt
- Volk aufgelöst
- Volk verkauft
- Volk verstorben
- Volk archiviert
- Korrektur/Storno eines Ereignisses
```

Technische Option:

```text
hive_events
- id
- user_id
- hive_id
- event_type
- event_date
- title
- description
- related_entity_type
- related_entity_id
- metadata_json
- created_by
- created_at
- updated_at
```

Wichtig: Bestehende Dokumenttypen wie inspections, treatments, feedings, harvests usw. bleiben fachliche Tabellen. `hive_events` dient als einheitliche Timeline und verweist auf diese Vorgänge.

### Archivieren statt löschen

Frontend muss zwei Aktionen anbieten:

```text
[Volk archivieren]
[Volk endgültig löschen]
```

Aber:

- Archivieren ist der Standard.
- Endgültig löschen ist nur erlaubt, wenn keine relevanten Fachvorgänge existieren oder das Volk als Fehleingabe markiert wurde.
- Bei vorhandenen Durchsichten, Behandlungen, Ernten, Kassenbuchbezügen oder Behandlungsjournal-Einträgen darf nicht hart gelöscht werden.
- Archivierte Völker erscheinen nicht in Standardlisten, bleiben aber in Suche, Historie, PDFs und Jahresarchiv verfügbar.

### Automatische Archivierung bei Auflösung

Wenn ein Nutzer einen Auflösungsgrund auswählt, wird automatisch archiviert:

```text
Volk auflösen
Grund:
- vereinigt mit Volk X
- tot
- verkauft
- abgegeben
- aufgelöst/abgekehrt
- anderer Grund
Datum
Notiz
```

Nach dem Speichern:

```text
status = dissolved / merged / sold / dead / lost
archived_at = Datum
is_active = false
```

Zusätzlich:

- Timeline-Eintrag erzeugen
- offene Aufgaben optional schließen oder verschieben
- Warnung anzeigen, falls offene Behandlungen/Nachkontrollen existieren
- Standortbelegung aktualisieren
- Jahresstatistik aktualisieren

### Völker vereinigen

Sonderfall: Volk A wird mit Volk B vereinigt.

Regeln:

```text
Quellvolk A:
- Status: merged
- archived_at setzen
- merged_into_hive_id = Volk B

Zielvolk B:
- Timeline-Eintrag: Volk A wurde vereinigt
- optional neue Stärke/Futter/Notiz erfassen
```

Die Historie von Volk A bleibt separat erhalten, ist aber mit Volk B verlinkt.

### Archivansicht

Neue Frontend-Ansichten:

```text
/hives/archive
/hives/:id/history
/hives/:id/archive
/hives/:id/dissolve
```

Archivfilter:

```text
- Jahr
- Standort
- Grund
- verkauft
- tot
- vereinigt
- aufgelöst
- Königinnenjahr
```

### API-Endpunkte

```text
GET    /api/hives?status=active
GET    /api/hives?status=archived
GET    /api/hives/{hive_id}/history
POST   /api/hives/{hive_id}/archive
POST   /api/hives/{hive_id}/dissolve
POST   /api/hives/{hive_id}/merge
DELETE /api/hives/{hive_id}
```

DELETE-Regel:

- Nur Admin/Besitzer.
- Nur ohne relevante Abhängigkeiten oder bei `created_by_mistake`.
- Immer Audit-Log schreiben.
- Nie Behandlungsjournal- oder Kassenbuchhistorie zerstören.

### Backend-Regeln

Implementiere Services:

```text
archive_hive(hive_id, reason, date, note)
dissolve_hive(hive_id, reason, date, note)
merge_hives(source_hive_id, target_hive_id, date, note)
can_hard_delete_hive(hive_id)
create_hive_event(...)
get_hive_timeline(hive_id)
```

### Frontend-Regeln

- Standardlisten zeigen nur aktive Völker.
- Archivierte Völker sind klar markiert.
- Auf Volk-Detailseite gibt es eine Timeline.
- Bei Archivierung muss der Nutzer Grund und Datum angeben.
- Bei endgültigem Löschen muss ein Warnhinweis erscheinen.
- Wenn Löschen nicht erlaubt ist, erklärt die UI den Grund und bietet Archivieren an.

### Auswirkungen auf Sammelaktionen

Sammel-Durchsichten, Sammel-Fütterungen, Sammel-Behandlungen und Sammel-Ernten dürfen standardmäßig nur aktive Völker enthalten.

Ausnahmen:

- Archivierte Völker dürfen in historischen Reports erscheinen.
- Archivierte Völker dürfen keine neuen normalen Vorgänge erhalten.
- Korrekturen/Stornos historischer Vorgänge bleiben möglich, sofern berechtigt.

### Reports und Exporte

PDF-/CSV-Exporte müssen archivierte Völker optional enthalten:

```text
include_archived=true/false
```

Jahresbericht soll zusätzlich ausweisen:

```text
- aktive Völker zum Jahresstart
- neue Ableger
- gekaufte/erhaltene Völker
- verkaufte Völker
- vereinigte Völker
- Verluste
- aktive Völker zum Jahresende
```

### Codex-Aufgaben

```text
Erweitere das Datenmodell um Volk-Lebenszyklus, Archivierung und eine allgemeine hive_events Timeline.
Implementiere Backend-Services für Archivieren, Auflösen, Vereinigen und sicheres Löschen.
Passe alle Listen und API-Endpunkte so an, dass standardmäßig nur aktive Völker erscheinen.
Baue eine Archivansicht und eine Historie-Seite je Volk im Angular-Frontend.
Sorge dafür, dass bei Auflösung eines Volkes automatisch archiviert wird.
Hartes Löschen darf nur für Fehleingaben ohne relevante Abhängigkeiten möglich sein.
Ergänze Audit-Log-Einträge für Archivierung, Auflösung, Vereinigen und Löschen.
```

### Akzeptanzkriterien

- Jedes Volk hat eine nachvollziehbare Historie.
- Archivierte Völker verschwinden aus aktiven Standardlisten.
- Archivierte Völker bleiben in Suche, Reports und Historie verfügbar.
- Auflösen archiviert ein Volk automatisch.
- Vereinigen verlinkt Quell- und Zielvolk korrekt.
- Hartes Löschen ist nur bei sicheren Fällen möglich.
- Behandlungsjournal, Kassenbuch und Jahresberichte verlieren keine historischen Daten.
- Sammelaktionen nutzen standardmäßig nur aktive Völker.

### Commit-Vorschläge

```text
feat(hives): add lifecycle states and archive fields
feat(hives): add hive event timeline
feat(hives): implement archive dissolve and merge services
feat(frontend): add hive history and archive views
security(hives): restrict hard delete for historical records
feat(reports): include archived hives in yearly summaries
```
