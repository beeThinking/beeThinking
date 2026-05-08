# Contributing to BeeThinking

Thank you for your interest in contributing! This document explains how to get involved.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## How to Contribute

### Reporting Bugs

Use the [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) issue template. Include:
- A clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (OS, browser, Python/Node version)

### Suggesting Features

Use the [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) issue template.

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

## Commit Convention

```
<ticket-number> - <short description>

Optional:
* Breaking Changes
* Critical Changes
* Bugfixes
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
