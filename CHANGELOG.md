# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [1.0.0] - 2026-07-24

### Added
- Monorepo structure with `apps/backend` (FastAPI) and `apps/frontend` (Angular 21)
- Root `docker-compose.yml` orchestrating database, backend, and frontend
- Frontend `Dockerfile` (multi-stage Node build + Nginx)
- Community health files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`
- GitHub issue templates and pull request template
- CI workflows for backend (pytest) and frontend (lint + test)
- Team apiary memberships and activity authorship fields
- CMS content APIs with admin UI and public page fallback
- Cashbook APIs and frontend EÜR summary
- Durchschau navigation with inspection, feeding, treatment and harvest variants
- Sales records, POS workflow, automatic stock/cashbook updates, customer QR list, and sales reporting
- Queen-rearing records, breeding calendar, reminders, and candidate selection
- Team task delegation, recurring tasks, hive selection, Web Push, map, analytics, calculators, and calendar pull sync
- Production backup/restore drill, refresh-token rotation, auth rate limiting, structured metrics, and account data export
