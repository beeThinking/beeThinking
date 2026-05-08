# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| `main`  | yes       |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability, please report it responsibly:

1. Open a [GitHub Security Advisory](https://github.com/beeThinking/beeThinking/security/advisories/new) in this repository.
2. Provide as much detail as possible:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

You will receive a response within **7 days**. If the issue is confirmed, a patch will be prepared and a coordinated disclosure date will be agreed upon before any public announcement.

## Security Best Practices for Contributors

- Never commit secrets, API keys, or credentials.
- Use `.env` files (excluded from version control via `.gitignore`) for sensitive configuration.
- Keep dependencies up to date — Dependabot alerts are enabled on this repository.
- Follow the principle of least privilege when adding new API endpoints or database queries.
