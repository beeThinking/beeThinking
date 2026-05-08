# BeeThinking Frontend

Angular 21 SPA for the BeeThinking beekeeping management application.

## Requirements

- Node.js 22+
- npm 10+

## Setup

```bash
npm install
```

## Development

```bash
npm start       # http://localhost:4200
```

The app reloads automatically on file changes.

## Build

```bash
npm run build   # output: dist/bee-thinking/
```

## Tests

```bash
npm test        # unit tests with Vitest
npm run lint    # ESLint
```

## Project Structure

```
src/
├── app/
│   ├── core/           # Guards, interceptors, services, models
│   ├── layout/         # Navbar, footer
│   ├── pages/          # Feature pages (dashboard, beehives, login, ...)
│   └── shared/         # Reusable components
├── environments/       # environment.ts / environment.prod.ts
├── index.html
├── main.ts
└── styles.css          # Global styles, design tokens, mobile-first base
```

## Mobile-First CSS (mandatory)

The entire frontend follows a **mobile-first** CSS approach. This is a hard convention.

**Rules:**
- Write base styles for the smallest screen first (≥ 320 px). Use `@media (min-width: …)` for larger screens. Never use `max-width` queries.
- **Breakpoints:** `480px` (sm) · `768px` (md) · `1024px` (lg)
- **Spacing:** use CSS custom properties from `styles.css` (`--space-xs` … `--space-2xl`, `--page-px`). No hardcoded `px` values.
- **Touch targets:** all interactive elements must be at least `44 × 44 px`.
- **Inputs:** always `font-size: 1rem` to prevent iOS auto-zoom.
- **Modals:** bottom sheet on mobile (`align-items: flex-end`, `border-radius: 16px 16px 0 0`), centered on desktop.
- **Hover effects:** wrap in `@media (hover: hover)` — do not fire on touch devices.
- **Horizontal scroll containers:** add `-webkit-overflow-scrolling: touch` and `scrollbar-width: none`.

## Backend

The frontend expects the backend API at `http://localhost:8000/api` (configured via `src/environments/environment.ts`).  
See [apps/backend](../backend/README.md) for setup instructions.
