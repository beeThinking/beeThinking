# Testing diagnosis (2026-03-31)

## Context
- Issue reported: tests seemed broken.
- Follow-up issue: `login.component.spec.ts` should be fixed for learning progress.
- Follow-up request: add two `nativeElement` examples for DOM testing.
- Follow-up request: add a third `nativeElement` example for loading state.

## Decision log
1. Reproduce first with a non-watch run using `npm test -- --watch=false`.
2. Prioritize setup errors before touching spec files.
3. Install local dependencies with `npm install` because the first run used a global Angular CLI and failed with `Cannot find module '@angular/build/package.json'`.
4. Re-run tests after install to verify whether the issue is framework setup or test logic.
5. Update `src/app/pages/login/login.component.spec.ts` to use standalone `imports: [LoginComponent]` and explicit provider mocks.
6. Replace Jasmine spies with Vitest mocks (`vi.fn`) because the test runner is Vitest in this project.
7. Add two DOM tests using `fixture.nativeElement`:
   - render check for `#username`, `#password`, and submit button
   - validation message check after invalid submit
8. Extend the router mock with RouterLink-required members (`createUrlTree`, `serializeUrl`, `events`) so `fixture.detectChanges()` works in DOM tests.
9. Add a third DOM test for pending login state with a `Subject`-backed observable to keep the request open and verify loading UI (`Signing in...`, disabled submit button).

## Result
- Test run passed: `src/app/app.spec.ts` (2/2 tests).
- Test run passed: `src/app/pages/login/login.component.spec.ts` (7/7 tests).
- No production code change required.

## Follow-ups
- Optional: align Node.js version with dependency engine requirements to remove `EBADENGINE` warning.
- Optional: review `npm audit` output (27 vulnerabilities reported).
- Next learning step: add a DOM assertion for post-success state (button text returns to `Sign In`) after completing the pending login stream.
