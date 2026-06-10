# bee thinking product areas

Date: 2026-06-10

## Durchschau as main workflow

Use `Durchschau` as the main beekeeping work area. Variants:

- `Kontrolle`: current inspection flow, stored in `inspections`.
- `Fuettern`: feeding records, stored in `feedings`.
- `Behandeln`: treatment records, stored in `treatments`.
- `Ernten`: harvest records, stored in `harvests`.

Frontend navigation should keep these variants together. Backend currently stores them as separate entities. Since no production data has to be preserved, this can be reshaped into one shared activity model or kept as separate tables with one shared activity projection.

Suggested backend additions:

- `performed_by_user_id` on `inspections`, `feedings`, `treatments`, `harvests`.
- Shared response DTO for hive/apiary activity timeline.
- Optional `activity_type` projection for reporting and filters.

## Team apiaries

Current ownership uses `owner_id == current_user.id` across most CRUD. The app is not productive yet, so this can be changed directly instead of carrying legacy ownership through migrations.

Suggested model:

- `apiary_members(id, apiary_id, user_id, role, invited_by_user_id, accepted_at, created_at)`.
- Roles: `owner`, `admin`, `member`, `viewer`.
- Replace direct owner checks for apiary-scoped entities with membership checks.
- Replace direct ownership as access model. Keep creator fields only where they describe authorship or audit data.

Required behavior:

- Multiple users can work on same apiary.
- Each inspection/feeding/treatment/harvest shows author.
- Deleting or editing records should depend on role and possibly author.

## CMS

Current public pages are hard-coded in `InfoPageComponent`. CMS should move editable texts to backend.

Suggested model:

- `content_pages(id, slug, locale, title, eyebrow, lead, cta_label, cta_link, status, updated_by_user_id, updated_at)`.
- `content_sections(id, page_id, sort_order, heading, body)`.
- API:
  - `GET /api/content/pages/{slug}?locale=de`
  - `GET /api/admin/content/pages`
  - `PUT /api/admin/content/pages/{id}`

Permissions:

- Admin-only write access.
- Public read for published pages.

## Kassenbuch and EÜR

Kassenbuch should be own office module, not just report page. It should support Einnahmenueberschussrechnung.

Suggested model:

- `cashbook_entries(id, apiary_id, owner_id, performed_by_user_id, booking_date, direction, category, amount_gross, tax_rate, tax_amount, amount_net, counterparty, description, payment_method, receipt_id, created_at, updated_at)`.
- `cashbook_receipts(id, owner_id, file_object_key, filename, content_type, size_bytes, ocr_status, ocr_text, ocr_provider, created_at)`.
- `cashbook_receipt_suggestions(id, receipt_id, field_name, suggested_value, confidence)`.

Categories:

- Einnahmen: honey sales, wax/products, services, subsidies, other.
- Ausgaben: feed, medication/treatments, equipment, jars/labels, travel, fees, other.

Automatic receipt capture:

1. Upload receipt image/PDF.
2. Store original in object storage.
3. OCR extracts text.
4. Parser suggests date, amount, VAT, vendor, category.
5. User confirms before entry is posted.

Do not auto-post OCR results without user confirmation. Receipt recognition will make mistakes, especially handwritten or folded receipts.

Reports:

- EÜR period summary: income, expenses, surplus.
- Category breakdown.
- CSV export for tax/accounting handoff.
- Receipt completeness: entries without receipt, receipts without confirmed entry.
