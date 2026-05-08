# Vitest test API imports decision (2026-04-01)

## Context
Running `vitest` failed with `ReferenceError: describe is not defined` in:
- `src/app/app.spec.ts`
- `src/app/pages/login/login.component.spec.ts`

## Decision
Use explicit imports from `vitest` in each spec file:
- `beforeEach`
- `describe`
- `expect`
- `it`
- `vi` (where needed)

## Rationale
- Keeps test files self-contained.
- Avoids introducing a global Vitest config file for a small fix.
- Works regardless of whether `test.globals` is enabled.

## Applied changes
- Updated `src/app/app.spec.ts`
- Updated `src/app/pages/login/login.component.spec.ts`

## Additional decision
Direct `vitest` execution also requires Angular TestBed environment initialization.

Added:
- `vitest.config.ts` with `jsdom` environment and `setupFiles` entry.
- `src/test-setup.ts` to call `TestBed.initTestEnvironment(BrowserTestingModule, platformBrowserTesting())`.

Reason:
- Prevents `Need to call TestBed.initTestEnvironment() first` when running `vitest` directly.


