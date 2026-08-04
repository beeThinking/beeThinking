# AGENTS.md — BeeThinking Monorepo

This file provides context and conventions for AI coding assistants working in this repository.

---

## Project Overview

BeeThinking is a beekeeping management application. It consists of:

- **Backend** (`apps/backend/`) — REST API built with FastAPI, SQLAlchemy, and JWT authentication
- **Frontend** (`apps/frontend/`) — Single-page application built with Angular 21
- **Mobile** (`apps/mobile/`) — iOS-first Flutter client; Android is planned

The backend and frontend stack can be started with `docker-compose up` from the repository root. Mobile is not a Docker or Flutter Web target.

---

## Repository Structure

```
beeThinking/
├── apps/
│   ├── backend/          # Python / FastAPI
│   │   ├── app/
│   │   │   ├── api/      # Route handlers
│   │   │   ├── core/     # Config (pydantic-settings) and security (JWT, bcrypt)
│   │   │   ├── crud/     # Database operations
│   │   │   ├── db/       # SQLAlchemy engine and session
│   │   │   ├── models/   # ORM models
│   │   │   ├── schemas/  # Pydantic request/response schemas
│   │   │   └── main.py   # FastAPI app, CORS, router registration
│   │   ├── tests/
│   │   │   ├── unit/     # Isolated unit tests
│   │   │   └── integration/  # End-to-end API tests
│   │   ├── requirements.txt
│   │   └── .env.example
│   ├── frontend/         # Angular 21
│   │   └── src/app/
│   │       ├── core/     # Guards, interceptors, services, models
│   │       ├── layout/   # Navbar, footer
│   │       ├── pages/    # Feature pages (dashboard, beehives, login, register, …)
│   │       └── shared/   # Reusable components
│   └── mobile/           # Flutter 3.24.5 / iOS
│       ├── lib/src/
│       │   ├── auth/     # Authentication API, state, repository, secure tokens
│       │   ├── config/   # Compile-time application configuration
│       │   └── screens/  # Application screens
│       ├── ios/          # Native iOS runner
│       └── test/         # Unit and widget tests
├── .github/
│   ├── workflows/        # CI: backend, frontend, and mobile validation
│   ├── ISSUE_TEMPLATE/   # Bug report and feature request forms
│   └── pull_request_template.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
└── docker-compose.yml
```

---

## Tech Stack

### Backend
| Concern | Library |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (`python-jose`), bcrypt (`passlib`) |
| Settings | `pydantic-settings` via `.env` |
| Server | Uvicorn |
| Tests | pytest + pytest-asyncio + httpx |
| Database (dev) | SQLite |
| Database (prod) | PostgreSQL 15 |

### Frontend
| Concern | Library |
|---|---|
| Framework | Angular 21 (standalone components) |
| Language | TypeScript 5.9 |
| Tests | Vitest + jsdom + Angular TestBed |
| Linting | ESLint + angular-eslint |
| Architecture | Sheriff (module boundaries) |
| HTTP | Angular `HttpClient` + auth interceptor |
| Routing | Angular Router + auth guard |

### Mobile
| Concern | Library / tool |
|---|---|
| Framework | Flutter 3.24.5 (stable) |
| Language | Dart 3.5+ |
| Target | iOS first; Android later |
| HTTP | `http` |
| Token storage | `flutter_secure_storage` |
| Tests | `flutter_test` |

---

## Development Commands

### Backend
```bash
cd apps/backend
cp .env.example .env          # first time only
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload  # http://localhost:8000
pytest                         # run all tests
pytest -m unit                 # unit tests only
pytest -m integration          # integration tests only
pytest --cov=app               # with coverage
```

### Frontend
```bash
cd apps/frontend
npm install                    # first time only
npm start                      # http://localhost:4200
npm test                       # Vitest unit tests
npm run lint                   # ESLint
npm run build                  # production build → dist/bee-thinking/
```

### Mobile
```bash
flutter --directory apps/mobile pub get
flutter --directory apps/mobile run
cd apps/mobile
dart format --output=none --set-exit-if-changed .
flutter analyze
flutter test
flutter build ios --release --no-codesign --dart-define=API_BASE_URL=https://api.example.com
```

Debug builds default to `http://localhost:8000`. Override with `--dart-define=API_BASE_URL=...`; non-debug builds require the value and release builds require HTTPS.

### Full stack
```bash
docker-compose up              # starts db + backend (8000) + frontend (80)
docker-compose up --build      # rebuild images first
```

---

## Code Conventions

### General
- All identifiers, comments, commit messages, and PR descriptions must be in **English**.
- Do not write JSDoc or inline comments unless explicitly requested.
- Prefer editing existing files over creating new ones.
- Do not commit secrets or credentials. Sensitive values belong in `.env` (git-ignored).

### Backend (Python)
- Follow the existing layered structure: `api → crud → models/schemas`.
- Route handlers live in `app/api/`. Keep them thin — business logic goes in `crud/` or `core/`.
- All settings are read through `get_settings()` from `app/core/config.py`. Never hardcode config values.
- New endpoints need at least one unit test in `tests/unit/test_api/`.
- Use `Depends(get_db)` for database sessions — never create sessions manually in handlers.

### Frontend (Angular)
- Use **standalone components** (no NgModules).
- All new files go under the appropriate `core/`, `pages/`, `shared/`, or `layout/` directory.
- Services use Angular's `inject()` function, not constructor injection.
- HTTP calls go through `ApiService` (`core/services/api.service.ts`).
- Authentication state is managed by `AuthService` (`core/services/auth.service.ts`).
- Always import Vitest globals explicitly (`describe`, `it`, `expect`, `vi`, `beforeEach`) in spec files — do not rely on globals config.

### Frontend — Mobile-first CSS (IMPORTANT)
The entire frontend follows a **mobile-first** CSS approach. This is a hard convention — never break it.

Rules:
- **Write base styles for the smallest screen first** (≥ 320 px). Add `@media (min-width: …)` overrides for larger screens. Never use `max-width` media queries.
- **Breakpoints** (defined as CSS custom properties in `styles.css`):
  - `480px` — sm (phablet)
  - `768px` — md (tablet / small desktop)
  - `1024px` — lg (desktop)
- **Spacing** — use the CSS custom property scale (`--space-xs` … `--space-2xl`) and `--page-px` (fluid horizontal padding). Never hardcode `px` spacing in component CSS.
- **Touch targets** — all interactive elements must be at least **44 × 44 px** (`min-height: 44px`). Enforced globally in `styles.css`.
- **Font sizes** — use `clamp()` for headings so they scale fluidly. Set `font-size: 1rem` (16px) on inputs to prevent iOS auto-zoom on focus.
- **Modals** — on mobile (< 768 px) modals render as a **bottom sheet** (`align-items: flex-end`, `border-radius: 16px 16px 0 0`). On desktop they are centered overlays.
- **Hover effects** — wrap hover styles in `@media (hover: hover)` so they are not triggered on touch devices.
- **Scrollable containers** — add `-webkit-overflow-scrolling: touch` and `scrollbar-width: none` for horizontal scroll areas (e.g. hive tab bar).
- Do **not** import `CommonModule` — use Angular 17+ built-in control flow (`@if`, `@for`, `@switch`) instead.
- `ChangeDetectionStrategy.OnPush` is mandatory on every component.

### Mobile (Flutter)
- Keep the current `lib/src/auth`, `lib/src/config`, and `lib/src/screens` boundaries.
- Target iOS first. Android support is later; do not add Flutter Web or Docker integration.
- Configure the backend only through the `API_BASE_URL` Dart definition. Do not hardcode environment-specific production endpoints.
- Store authentication tokens only through platform secure storage. Never place tokens in source, Dart definitions, logs, environment files, or plain-text preferences.
- Run formatting, analysis, tests, and an iOS no-codesign build for mobile changes.

---

## Architecture Decisions

### Authentication
- JWT tokens stored in `localStorage` on the frontend.
- The `AuthInterceptor` (`core/interceptors/auth.interceptor.ts`) automatically attaches the Bearer token to outgoing requests.
- The `AuthGuard` (`core/guards/auth.guard.ts`) protects routes requiring login.
- Backend token expiry: 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`).

### Database
- Development default: SQLite (`DATABASE_URL=sqlite:///./beethinking.db`).
- Production: PostgreSQL 15 (configured in `docker-compose.yml`).
- Schema changes use Alembic migrations. The app must not create tables on import.

### Testing (Frontend)
- Test runner: **Vitest** (not Karma/Jest). Config: `apps/frontend/vitest.config.ts`.
- Environment: jsdom, initialized via `src/test-setup.ts`.
- DOM tests use `fixture.nativeElement` — see existing examples in `login.component.spec.ts`.

---

## Commit Convention

Use Conventional Commits:

```text
<type>(<scope>): <imperative summary>
```

Common types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `build`, `ci`.

Example: `feat(cashbook): add EÜR summary`

---

## Important Decisions Log

Keep decision notes only while they are still useful. Remove stale planning files instead of letting them contradict current code.
