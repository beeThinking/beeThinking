# BeeThinking Ubiquitous Language

## Purpose

This file defines shared BeeThinking domain language for product, UI, API, code, tests and documentation.

Use these terms consistently. When German UI wording and English code wording differ, this file defines the mapping.

## Language Rules

- Code, API paths, database tables and backend models use English names.
- German UI may use beekeeper-facing German names where they are clearer.
- Documentation may mention both names on first use.
- Do not introduce new synonyms unless domain meaning differs.
- Prefer one concept per term. If meaning changes, add a new term instead of overloading an old one.

## Core Terms

| English term | German UI term | Meaning | Code/API usage |
|---|---|---|---|
| User | Benutzer | Person with account and login. | `User`, `/api/users` |
| Apiary | Stand, Bienenstand | Location where hives are kept. | `Apiary`, `/api/apiaries` |
| Stock number | Betriebsnummer, Standnummer | Official or internal identifier for an apiary/stand. | `stock_number` |
| Hive | Volk, Bienenvolk | Managed bee colony in a hive box at an apiary. | `Hive`, `/api/hives` |
| Hive lifecycle | Volk-Lebenszyklus | State/history of a hive from creation to archive/death/merge/sale. | `HiveStatus`, `HiveEvent` |
| Inspection | Durchschau, Kontrolle | Structured hive check with condition data and notes. | `Inspection`, `/api/hives/{hive_id}/inspections` |
| Treatment | Behandlung | Beekeeping treatment, often Varroa-related. | `Treatment`, `/api/treatments` |
| Feeding | Fütterung | Feed action for hive or apiary. | `Feeding`, `/api/feedings` |
| Harvest | Ernte, Honigernte | Honey harvest record. | `Harvest`, `/api/harvests` |
| Queen | Königin | Queen data for one hive. | `Queen`, `/api/queens` |
| Task | Aufgabe | Planned or open work item. | `Task`, `/api/tasks` |
| Appointment | Termin | Calendar-like planned event. | Route/page concept |
| Photo | Foto, Bild | Image linked to hive, inspection or other domain object. | `Photo`, `/api/photos` |
| Dashboard | Dashboard, Übersicht | Overview page with current operational summary. | `/api/dashboard`, `/dashboard` |
| Report | Bericht, Auswertung | Generated or calculated summary. | `/api/reports`, `/office/reports` |

## Office And Accounting Terms

| English term | German UI term | Meaning | Code/API usage |
|---|---|---|---|
| Office | Büro | Administrative area for accounting and reports. | `/api/office`, `/office` |
| Cashbook | Kassenbuch | Income and expense ledger. | `Cashbook`, `/api/cashbook` |
| Cashbook entry | Buchung | One income or expense record. | `CashbookEntry` |
| Income | Einnahme | Positive cashbook entry. | entry type/value |
| Expense | Ausgabe | Negative cashbook entry. | entry type/value |
| Receipt | Beleg | File or reference proving a cashbook entry. | `CashbookReceipt` |
| EÜR | EÜR | Einnahmenüberschussrechnung summary. | report/summary concept |
| Category | Kategorie | Accounting/category grouping for entries. | `category` |
| Tax | Steuer | Tax-related amount or field. | tax fields |
| VAT | MwSt., Umsatzsteuer | Value-added tax. | VAT/tax fields |

## CMS And Public Content Terms

| English term | German UI term | Meaning | Code/API usage |
|---|---|---|---|
| Content page | Inhaltsseite | Editable public/static page. | `ContentPage`, `/api/content` |
| Content admin | CMS-Verwaltung | Admin UI for editing content pages. | `/api/admin/content`, `/admin/cms` |
| About | Über uns | Public info page. | `/about` |
| Contact | Kontakt | Public contact page. | `/contact` |
| Docs | Dokumentation | Public documentation/help page. | `/docs` |
| Tips | Tipps | Public beekeeping tips page. | `/tips` |
| FAQ | FAQ | Frequently asked questions. | `/faq` |
| Support | Support | Support info page. | `/support` |
| Privacy | Datenschutz | Privacy policy page. | `/privacy` |
| Imprint | Impressum | Legal imprint page. | `/imprint` |
| Terms | AGB/Nutzungsbedingungen | Terms page. | `/terms` |

## Inventory Terms

| English term | German UI term | Meaning | Code/API usage |
|---|---|---|---|
| Inventory | Lager, Inventar | Tracked materials and equipment. | Inventory pages/services |
| Article | Artikel | Reusable item definition or product type. | `Article`, `/api/articles` |
| Inventory item | Lagerbestand, Inventarposition | Concrete stock quantity or item instance. | `InventoryItem`, `/api/inventory-items` |

## Team And Permission Terms

| English term | German UI term | Meaning | Code/API usage |
|---|---|---|---|
| Owner | Besitzer, Eigentümer | User who owns created apiary/hive/resource. | `owner`, `owner_id` |
| Member | Mitglied | User with access to an apiary through collaboration. | `ApiaryMember` |
| Admin | Administrator | User with system-level admin permission. | `is_admin`, `ADMIN_EMAILS` |
| Active user | Aktiver Benutzer | User allowed to authenticate and use protected routes. | `is_active` |
| Verified user | Verifizierter Benutzer | User with verified email/account state. | `is_verified` |

## Hive Status Values

Use existing enum values in code and API.

| Code value | German UI term | Meaning |
|---|---|---|
| `active` | Aktiv | Hive is managed normally. |
| `archived` | Archiviert | Hive is no longer active but retained for records. |
| `dissolved` | Aufgelöst | Hive was dissolved intentionally. |
| `merged` | Vereinigt | Hive was merged into another hive. |
| `sold` | Verkauft | Hive was sold or transferred away. |
| `dead` | Tot | Colony died. |
| `inactive` | Inaktiv | Hive is not active, generic inactive state. |
| `lost` | Verloren | Hive/colony was lost. |
| `created_by_mistake` | Irrtümlich angelegt | Record was created by mistake. |

## Hive Type Values

| Code value | German UI term | Meaning |
|---|---|---|
| `langstroth` | Langstroth | Langstroth hive system. |
| `dadant` | Dadant | Dadant hive system. |
| `zander` | Zander | Zander hive system. |
| `other` | Sonstige | Other hive system. |

## Inspection Terms

| English term | German UI term | Meaning | Code usage |
|---|---|---|---|
| Queen seen | Königin gesehen | Whether queen was observed during inspection. | `queen_seen` |
| Brood strength | Brutstärke | Strength/amount of brood. | `brood_strength` |
| Varroa count | Varroa-Zählung | Count or measured Varroa load. | `varroa_count` |
| Food stores | Futtervorrat | Amount/score of available food. | `food_stores` |
| Swarm cells | Schwarmzellen | Swarm-related cells seen during inspection. | `swarm_cells` |
| Mood | Stimmung | Colony temperament during inspection. | `mood` |
| Strength | Volksstärke | Overall colony strength. | `strength` |
| Weather snapshot | Wetterdaten | Weather data captured for inspection context. | `weather_*` fields |
| Next steps | Nächste Schritte | Follow-up actions after inspection. | `next_steps` |
| Notes | Notizen | Free-form observations. | `notes` |

## Inspection Enum Values

Swarm cells:

| Code value | German UI term |
|---|---|
| `none` | Keine |
| `play_cups` | Spielnäpfchen |
| `queen_cells` | Weiselzellen |

Mood:

| Code value | German UI term |
|---|---|
| `calm` | Ruhig |
| `normal` | Normal |
| `aggressive` | Aggressiv |

Strength:

| Code value | German UI term |
|---|---|
| `weak` | Schwach |
| `medium` | Mittel |
| `strong` | Stark |

## Varroa Weather Terms

| English term | German UI term | Meaning | Code usage |
|---|---|---|---|
| Varroa weather | Varroawetter | Treatment planning support based on weather and rules. | `varroa_weather` |
| Treatment window | Behandlungsfenster | Time window suitable for treatment. | `VarroaWeatherWindow` |
| Provider | Anbieter | Source/strategy for weather planning. | provider classes |
| Open-Meteo | Open-Meteo | Weather data provider. | `open_meteo` |
| Internal rules | Interne Regeln | Built-in rules without official API. | `internal_rules` |
| Official Varroawetter | Offizielles Varroawetter | Stub for future official provider. | `official_varroawetter` |
| Disabled | Deaktiviert | No Varroa weather planning. | `disabled` |

## Preferred Naming By Layer

| Concept | Backend/model/API | Frontend route/code | German UI |
|---|---|---|---|
| Apiary | `apiary`, `Apiary`, `/api/apiaries` | `apiaries`, `stands` alias allowed | Stand/Bienenstand |
| Hive | `hive`, `Hive`, `/api/hives` | `beehives` route currently used | Volk/Bienenvolk |
| Inspection | `inspection`, `Inspection` | `inspections`, `hive-inspect` | Durchschau |
| Cashbook | `cashbook`, `Cashbook` | `office/cashbook` | Kassenbuch |
| CMS | `content`, `ContentPage` | `admin/cms` | CMS/Inhalte |

## Avoided Terms

Avoid these unless quoting old UI/code:

- `Beehive` as backend model name. Use `Hive`.
- `Standort` for apiary if it can be confused with generic location. Use `Stand` or `Bienenstand`.
- `Colony` in code unless representing biological colony separate from physical hive. Current model is `Hive`.
- `Booking` for cashbook entry unless accounting context requires it. Prefer `CashbookEntry` in code and `Buchung` in German UI.
- `Storage` for inventory. Use `Inventory`/`Lager` to avoid conflict with object storage.

## Translation Guidance

German UI should be beekeeper-facing and natural:

- Use `Stand` in navigation when space is tight.
- Use `Bienenstand` in headings/forms when clarity matters.
- Use `Volk` in operational screens.
- Use `Bienenvolk` in headings or first mention.
- Use `Durchschau` for inspection workflow.
- Use `Kassenbuch` for cashbook.
- Use `Büro` for office area.

English code should stay technical and stable:

- `Apiary` not `Stand`.
- `Hive` not `Beehive` or `Colony`.
- `Inspection` not `Checkup`.
- `CashbookEntry` not `Booking`.
- `ContentPage` not `CmsPage` unless CMS-specific behavior matters.

## Decision Rule For New Terms

When adding new feature language:

1. Check existing term in this file.
2. If existing term fits, reuse it in code, UI and tests.
3. If new concept differs, add a new term with meaning and preferred layer naming.
4. If German UI needs a different word, document mapping.
5. Update tests and translations with same vocabulary.

