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
├── index.html
├── main.ts
└── styles.css
```

## Backend

The frontend expects the backend API at `http://localhost:8000/api`.  
See [apps/backend](../backend/README.md) for setup instructions.
