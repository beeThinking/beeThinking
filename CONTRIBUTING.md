# Contributing to BeeThinking

Thank you for your interest in contributing! This document explains how to get involved.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## How to Contribute

### Reporting Bugs

Use the [Bug Report](.github/ISSUE_TEMPLATE/bug_report.yml) issue template. Include:
- A clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (OS, browser, Python/Node version)

### Suggesting Features

Use the [Feature Request](.github/ISSUE_TEMPLATE/feature_request.yml) issue template.

### Submitting a Pull Request

1. **Fork** the repository and create a branch from `main`:
   ```bash
   git checkout -b feat/your-feature
   ```
2. **Follow the commit convention** (see below).
3. **Make sure CI passes** — run tests locally before pushing.
4. **Open a Pull Request** against `main` and fill in the PR template.

## Development Setup

### Backend

```bash
cd apps/backend
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run tests:
```bash
pytest
```

### Frontend

```bash
cd apps/frontend
npm install
npm start
```

Run tests:
```bash
npm test
npm run lint
```

### Mobile

Mobile development is iOS-first with Flutter `3.24.5`; Android is planned, while Web and Docker targets are out of scope. Xcode is required to run or build the app.

```bash
flutter --directory apps/mobile pub get
flutter --directory apps/mobile run
```

Debug builds default to `http://localhost:8000`. Set another backend with `--dart-define=API_BASE_URL=https://api.example.com`; non-debug builds require this definition. API base URLs are configuration, not secret storage. Authentication tokens must remain in platform secure storage—never commit, log, or persist them in source, environment files, or plain-text preferences.

Run checks from `apps/mobile`:

```bash
dart format --output=none --set-exit-if-changed .
flutter analyze
flutter test
flutter build ios --release --no-codesign --dart-define=API_BASE_URL=https://api.example.com
```

## Commit Convention

Use Conventional Commits:

```text
<type>(<scope>): <imperative summary>
```

Examples:

```text
feat(cashbook): add EÜR summary
fix(auth): normalize invalid-token errors
docs(readme): update local setup
```

All commit messages must be written in **English**.

## Branch Naming

| Type | Pattern |
|------|---------|
| Feature | `feat/<short-name>` |
| Bug fix | `fix/<short-name>` |
| Docs | `docs/<short-name>` |
| Chore | `chore/<short-name>` |

## Security

Please do **not** open public issues for security vulnerabilities. Instead, follow the process described in [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
