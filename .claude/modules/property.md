# Module: Property

Covers PRD Module 9 (Property Management, admin) and its public faces — Module 4 (Listing/Browse) and Module 5 (Details). The system-of-record module the AI features read from.

**Read:** `docs/04-api-spec.md` §8, `docs/03-database-schema.md`, `docs/01-prd.md` §5/§6/§10.
**Rules:** `backend`, `database`, `frontend`, `testing`.

## Tables
`properties`, `property_media`, `property_embeddings` (pgvector, tagged with `tenant_id` + `property_id`).

## Key requirements
- FR9.1 CRUD with media (photos, video, floor plans, documents).
- FR9.2 Bulk upload (CSV/Excel) with per-row validation and error reporting — malformed rows report individually, never fail the whole batch.
- FR9.3 Approval workflow: Draft → Pending Approval → Published (per-tenant whether approval is required). Not publicly visible until approved.
- FR9.4 Status flags: Featured, Sold, On Hold, Archived.
- FR9.5 **On publish, trigger `app/workers/embed_property.py`** (background task) to build a text representation, generate an embedding, and upsert into `property_embeddings` — so the listing becomes searchable/matchable within the sync window.
- Public: grid/list/map views, combinable filters + AI search, sort, session-based favorites (migrate on login), pagination/infinite scroll, details page resilient to partial data (missing floor plan must not break layout).

## Publish → embedding flow
`POST/PUT /api/v1/properties/{id}` → `property_service` saves → background `embed_property` → upsert to pgvector (tenant-tagged). See `docs/02-architecture.md` §6.4.

## Acceptance / test cases (from `docs/15`)
- `TC-PROP-01` `pending_approval` property is not publicly visible until approved.
- `TC-PROP-02` bulk upload with malformed rows reports per-row errors, not full-batch failure.
- `TC-PROP-03` agent without `properties.edit` gets 403 on write endpoints.
