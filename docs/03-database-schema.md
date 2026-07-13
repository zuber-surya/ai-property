# Database Schema — PropVista CRM

> **Doc 03 of the PropVista CRM documentation set.** Defines the core entities, tables, relationships, and the tenant-isolation pattern (`tenant_id` + Postgres RLS) that every table must follow. Written for Supabase Postgres, accessed via SQLAlchemy + Alembic migrations.
>
> **Status:** Draft v1.2 · **Last updated:** July 2026
> Depends on: `02-architecture.md`
> **v1.1:** closed the blocking schema gaps surfaced by the per-screen specs (`16-customer-spec/`, `17-admin-spec/`).
> **v1.2:** applied the MVP product decisions taken on 2026-07-13 — manual lead claim, pg_cron + a Python jobs worker, synchronous reports, SendGrid/Twilio, self-hosted session counting, and a retention policy. **All previously open schema questions are now closed.** See [Section 9 — Changelog](#9-changelog).

---

## 1. Conventions

- Primary keys: `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`.
- Every tenant-owned table includes: `tenant_id UUID NOT NULL REFERENCES tenants(id)`.
- Every table includes: `created_at TIMESTAMPTZ DEFAULT now()`, `updated_at TIMESTAMPTZ DEFAULT now()`.
- Soft delete via `deleted_at TIMESTAMPTZ NULL` on user-facing entities (properties, leads, users, cms_pages) rather than hard deletes, to preserve CRM history.
- Naming: snake_case tables and columns, plural table names.
- **Enum-like columns are `text` + a `CHECK` constraint**, not Postgres `ENUM` types — adding a value to a Postgres enum is a migration that locks the table, and these lists will change. The allowed values are listed per column below and are **normative**: an application must not write a value that isn't listed here.
- **Uniqueness constraints are part of the schema, not an implementation detail.** Where a table has one, it's stated explicitly — several of them are load-bearing for tenant isolation (see `tenants.domain`) or for correctness of the anonymous-session migration (see `favorites`).

---

## 2. Entity Relationship Overview

```
tenants ──< users
   │
   ├──< properties ──< property_media
   │         │
   │         ├──< property_embeddings (pgvector)
   │         └──< property_views
   │
   ├──< leads ──< lead_notes
   │       │
   │       ├──< lead_activities (stage + ownership history)
   │       │
   │       ├──> requirement_profiles   (what this lead wants)
   │       ├──> chat_conversations     (the conversation that produced it)
   │       └──> users                  (the customer, once registered)
   │
   ├──< requirement_profiles ──< requirement_matches
   │
   ├──< chat_conversations ──< chat_messages
   │
   ├──< notifications              (delivered, per-user)
   ├──< notification_preferences   (per-user channel opt-ins)
   ├──< notification_rules         (per-tenant staff routing)
   │
   ├──< cms_pages
   ├──< cms_banners
   │
   ├──< search_queries             (AI-search telemetry, powers FR13.4)
   ├──< bulk_uploads ──< bulk_upload_rows
   │
   ├──< ai_config
   └──< audit_log                  (append-only)

amenities  — platform-level lookup (the canonical vocabulary; not tenant-scoped)
```

---

## 3. Core Tables

### 3.1 `tenants`
Platform-level table — not itself tenant-scoped (this is the table `tenant_id` references).

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `name` | text | Business name |
| `domain` | text | Custom domain or subdomain slug. **`UNIQUE NOT NULL`** — see the warning below |
| `domain_verified_at` | timestamptz | NULL until DNS ownership is verified. A custom domain must **not** be routed until this is set (`17-admin-spec/20` §9) |
| `branding_logo_url` | text | |
| `branding_primary_color` | text | Hex. Hover/active/disabled shades are **derived** in the frontend, not stored |
| `branding_accent_color` | text | nullable |
| `status` | text | `active` · `trial` · `suspended`. **Suspension keeps the public site serving and blocks admin login** — see below |
| `timezone` | text | IANA name, e.g. `Asia/Kolkata`. **Every dated report and KPI is computed in this timezone**, never UTC or the browser's — otherwise two admins in the same company see different numbers |
| `requires_property_approval` | boolean | DEFAULT `false`. Drives the Draft → Pending Approval → Published gate (FR9.3) |
| `contact_address` | text | nullable — rendered on the public Contact page |
| `contact_phone` | text | nullable |
| `contact_email` | text | nullable |
| `business_hours` | jsonb | nullable — e.g. `{"mon_sat": "09:30-18:30", "sun": null}` |
| `created_at` / `updated_at` | timestamptz | |

> ⚠️ **`domain` uniqueness is a security control, not a data-quality nicety.** It is the key the tenant resolver (`core/tenancy.py`) uses to map an incoming public request to a tenant. Two tenants sharing a domain makes tenant resolution *ambiguous*, which means serving one tenant's data on another's site. Enforce `UNIQUE` at the database level — an application-layer check is not sufficient.

**What each `status` does** (decided 2026-07-13):

| Status | Public site | Admin login | AI endpoints | Data |
|---|---|---|---|---|
| `active` | ✅ serving | ✅ | ✅ | — |
| `trial` | ✅ serving | ✅ | ✅ | Same as active. Billing is out of scope, so `trial` is currently **a label, not a behavior** |
| `suspended` | **✅ still serving** | **⛔ blocked** | ✅ still enabled | Retained |

> **Accepted trade-off:** a suspended tenant's buyers see no outage, so their listings, search, and chatbot keep working — which means **we keep paying Bedrock for a tenant who isn't paying us.** This was chosen deliberately over taking their site dark. If AI spend on suspended tenants becomes material, the lever is to disable `ai/*` for `status = 'suspended'` without touching the rest of the site.

> `suspended` blocks **admin login**, which means their staff cannot work the leads their still-live public site keeps generating. Those leads accumulate in `new`, unclaimed. That is a consequence of the choice, not a bug — but it argues for reactivating quickly.

### 3.2 `users`
Covers customers, agents, admins, super admins — role differentiates. Linked to Supabase Auth via `auth_user_id`.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `auth_user_id` | UUID | FK to Supabase `auth.users.id` |
| `tenant_id` | UUID | NULL for super admin (platform-level); required otherwise |
| `email` | text | |
| `full_name` | text | |
| `phone` | text | nullable |
| `role` | text | `customer` · `agent` · `admin` · `super_admin` |
| `is_active` | boolean | DEFAULT `true`. Read on **every** request — deactivation takes effect immediately, not on token expiry |
| `created_at` / `updated_at` / `deleted_at` | timestamptz | |

**Uniqueness:** `UNIQUE (auth_user_id, tenant_id)`.

> ⚠️ **One Supabase identity, one row *per tenant*.** The v1.0 schema implied `auth_user_id` was unique on its own. It is not workable: the same person can legitimately be a customer on tenant A's public site and an agent in tenant B's portal (a consultant who works with two brokerages; brokerage staff who browse their own listings). The lookup in `core/security.py` must therefore be `(auth_user_id, tenant_id)` → user, with `tenant_id` coming from the resolved request context — **never `auth_user_id` alone**, which would return an arbitrary row and hand the caller the wrong role. Super admins are the exception: `tenant_id IS NULL`, one row.

### 3.3 `roles_permissions` *(supports Module 11 — granular role config)*

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | |
| `role_name` | text | Custom role label if tenant defines beyond the base 4 |
| `permissions` | jsonb | Feature-flag map, e.g. `{"properties.edit": true, "reports.view": false}` |

**Deferred past MVP** — the four fixed roles cover every flow in `16-customer-spec/` and `17-admin-spec/`. See §7.

### 3.4 `properties`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | |
| `title` | text | |
| `description` | text | **Primary input to the embedding.** A thin description silently degrades AI search for this listing forever (`17-admin-spec/04` §3.1) |
| `property_type` | text | `apartment` · `villa` · `plot` · `commercial` · `office` · `land` |
| `listing_type` | text | `sale` · `rent` |
| `price` | numeric | The **asking** price. Not what it sold for — see `leads.deal_value` |
| `area_sqft` | numeric | |
| `bedrooms` | int | nullable (a plot has none) |
| `bathrooms` | int | nullable |
| `location_address` | text | |
| `location_lat` | double precision | nullable — without it the property can't appear in map view |
| `location_lng` | double precision | nullable |
| `amenities` | jsonb | Array of **amenity codes** from `amenities.code` (§3.18). **Not free text** |
| `status` | text | `draft` · `pending_approval` · `published` · `sold` · `on_hold` · `archived` |
| `is_featured` | boolean | DEFAULT `false`. Orthogonal to status — a featured property must **also** be `published` to appear anywhere |
| `agent_id` | UUID | FK → users (role=agent), nullable. The agent *assigned* to sell it |
| `created_by` | UUID | FK → users, nullable. The user who *created* it. Distinct from `agent_id`, and required for agent ownership-scoping (`08-auth-roles-spec.md` §5) |
| `expires_at` | timestamptz | nullable. Drives the `listing_expiring` notification event (FR15.2), which previously had no possible trigger |
| `embedding_source_hash` | text | nullable. Hash of the text that produced the current embedding. **Regenerate the embedding only when this changes** — see the warning below |
| `created_at` / `updated_at` / `deleted_at` | timestamptz | |

> ⚠️ **`archived` (status) and `deleted_at` (soft delete) are different things.** `archived` = the tenant has taken it off the market but keeps it in their inventory list. `deleted_at` = removed from the tenant's view entirely, retained only so historical leads still resolve. Both are invisible to the public and both must be **removed from `property_embeddings`**. Do not conflate them in queries or UI.

> ⚠️ **De-indexing matters as much as indexing.** A property that becomes `sold`, `archived`, `on_hold`, or soft-deleted must have its `property_embeddings` row deleted. Otherwise AI search keeps returning it and the chatbot keeps offering it — a bug that throws no error and that nobody notices for weeks.

### 3.5 `property_media`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `property_id` | UUID | FK → properties |
| `tenant_id` | UUID | denormalized for RLS simplicity |
| `media_type` | text | `image` · `video` · `floor_plan` · `document` |
| `url` | text | Supabase Storage URL |
| `sort_order` | int | |
| `created_at` | timestamptz | |

> ⚠️ **Storage access — a knowingly accepted risk (decided 2026-07-13).** **All media types, including `document`, live in a single public Supabase Storage bucket.** Anyone with a media URL — leaked, shared, or guessed — can read it, with no authentication and no tenant check. Supabase Storage URLs are not secret.
>
> This is acceptable **only** while `document` means brochures, price lists, and public collateral. **If a tenant ever uploads an ownership paper, an agreement, or an ID scan, this becomes a data-exposure incident.** The mitigation, if that day comes, is a private bucket for `media_type = 'document'` served via short-lived signed URLs. The admin UI should say plainly, at the upload control, that documents are publicly accessible.

### 3.6 `property_embeddings` *(pgvector — supports AI Search & Recommendation)*

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `property_id` | UUID | FK → properties, `UNIQUE` (one current vector per property) |
| `tenant_id` | UUID | **Must be a filter *inside* the vector query, not a post-filter** — see §5 |
| `embedding` | vector(1024) | Amazon Titan Text Embeddings V2, 1024 dimensions (see `06-ai-search-spec.md`) |
| `source_text` | text | The text that was embedded (for debugging/re-embedding) |
| `model_version` | text | Tracks which embedding model/version generated this vector |
| `created_at` / `updated_at` | timestamptz | |

Regenerable from `properties` — not a single point of unrecoverable failure.

### 3.7 `properties` → `property_views` *(supports FR8.2)*

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | |
| `property_id` | UUID | FK → properties |
| `session_id` | text | nullable — anonymous viewer |
| `user_id` | UUID | nullable — FK → users |
| `viewed_at` | timestamptz | DEFAULT now() |

Backs the "property views over time" chart (FR8.2), which previously had no data source. **You cannot backfill views you never recorded** — if this table isn't there when the first property goes live, that history is gone permanently.

Roll up to a daily aggregate rather than retaining raw rows indefinitely (§7).

### 3.8 `leads`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | |
| `property_id` | UUID | nullable — a lead may not be tied to a specific property |
| **`user_id`** | UUID | **nullable, FK → users.** The registered customer this lead belongs to. **NEW in v1.1** |
| **`session_id`** | text | **nullable.** The anonymous session that created it; re-keyed to `user_id` on registration. **NEW in v1.1** |
| **`requirement_profile_id`** | UUID | **nullable, FK → requirement_profiles.** What this person is looking for. **NEW in v1.1** |
| **`chat_conversation_id`** | UUID | **nullable, FK → chat_conversations.** The conversation that produced the lead. **NEW in v1.1** |
| `customer_name` | text | |
| `customer_phone` | text | **NOT NULL** — the field an agent actually uses. A lead with no reachable phone is near-worthless |
| `customer_email` | text | nullable |
| `message` | text | nullable — the visitor's free text. **Rendered in the admin portal → escape on output** (stored-XSS path from an anonymous public form into an admin's browser) |
| `source` | text | `chatbot` · `ai_search_inquiry` · `requirement_form` · `contact_form` · **`property_details`** · `walk_in`. **NOT NULL** |
| `stage` | text | `new` · `contacted` · `site_visit_scheduled` · `negotiation` · `closed_won` · `closed_lost`. **Fixed enum — see §7** |
| `assigned_agent_id` | UUID | FK → users, **NULL on creation** — leads are manually claimed, not auto-assigned. See below |
| **`claimed_at`** | timestamptz | nullable — when an agent claimed it. **NEW in v1.2** |
| **`requested_callback_at`** | timestamptz | **nullable.** The slot requested via `POST /leads/callback-request` (FR6.2), which previously had nowhere to be stored. **NEW in v1.1** |
| **`requested_slot`** | text | **nullable.** `morning` · `afternoon` · `evening` — when the visitor gave a window rather than a time. **NEW in v1.1** |
| **`deal_value`** | numeric | **nullable.** Set on `closed_won`. Without it a "sales report" (FR15.1) can only report *asking* prices, which is not what "sales" means. **NEW in v1.1** |
| **`idempotency_key`** | text | **nullable, `UNIQUE (tenant_id, idempotency_key)`.** Generated client-side when the lead form opens. **NEW in v1.1** |
| `created_at` / `updated_at` / `deleted_at` | timestamptz | |

**Uniqueness:** `UNIQUE (tenant_id, idempotency_key)` where the key is not null.

> ⚠️ **`user_id` / `session_id` close a live data-leak vector.** Without them, "which leads belong to this logged-in customer?" (FR7.1, the Customer Portal's inquiry history) has no correct answer — and the obvious workaround, matching on `customer_email`, is **exploitable**: that field is nullable, unverified, and typed by an anonymous visitor. Register with someone else's email and you would be shown their inquiries. Lead ownership must be established at *creation* time from the JWT or `X-Session-Id`, and migrated on registration alongside `favorites` (`08-auth-roles-spec.md` §4).

> ⚠️ **`source = property_details` was previously a contradiction.** `14-screen-workflows.md` §4 sets it; the v1.0 enum did not contain it. Added — the two docs now agree.

> **Idempotency (FR6.4's "no duplicate lead records for a single submission"):** the unique key is the primary defense; a soft dedupe on `(tenant_id, customer_phone, property_id)` within a short window catches the refresh-and-resubmit case, which carries a *different* key. See `16-customer-spec/15` §6.

### 3.8.1 Lead assignment — manual claim (decided 2026-07-13)

**Leads are not auto-assigned.** A new lead is created with `assigned_agent_id = NULL` and sits in a **shared queue**: the Kanban board's `new` column shows *every* unassigned lead in the tenant to *every* agent. An agent claims a lead by dragging it out of `new` (or pressing Claim), which sets `assigned_agent_id` and `claimed_at`.

Consequences to build for, not around:

- **The board's default filter must be `assigned_to_me OR assigned_agent_id IS NULL`.** A strict "assigned to me" default would render the shared queue invisible and no lead would ever be claimed.
- **Two agents will race for the same lead.** The claim must be an atomic conditional update, not a read-then-write:

  ```sql
  UPDATE leads
     SET assigned_agent_id = :agent, claimed_at = now()
   WHERE id = :lead_id
     AND tenant_id = :tenant
     AND assigned_agent_id IS NULL     -- the guard
  RETURNING id;
  ```

  Zero rows returned = somebody else got there first. The UI must say so ("Anjali just claimed this") and refresh the card, **not** silently overwrite the other agent's claim.
- **An unclaimed lead is nobody's responsibility.** This is the known cost of manual claim (chosen over round-robin): a lead arriving at 9pm Friday is owned by no one until an agent chooses it. The `lead_stale` notification rule (§3.22) is the safety net — configure it to fire on leads sitting in `new` past a threshold, so the queue can't rot silently.
- Claims and reassignments are both recorded in `lead_activities` as `activity_type = 'assignment_change'` (§3.10).

### 3.9 `lead_notes`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `lead_id` | UUID | FK → leads |
| `tenant_id` | UUID | |
| `author_id` | UUID | FK → users |
| `note_text` | text | **Internal only.** Contains candid commercial judgments ("lowballing, not serious"). **Must never appear in any customer-facing API response** — the portal's `LeadOut` schema and the admin's are separate Pydantic models |
| `follow_up_at` | timestamptz | nullable — reminder date |
| `created_at` | timestamptz | |

Append-only. Notes are a CRM audit trail; no editing or deleting.

> **Reminders don't fire on their own.** `follow_up_at` is stored, but nothing reads it. Delivering the reminder requires the job scheduler that `02-architecture.md` doesn't yet provide (§7).

### 3.10 `lead_activities` *(stage **and ownership** change history)*

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `lead_id` | UUID | FK → leads |
| `tenant_id` | UUID | |
| **`activity_type`** | text | `stage_change` · `assignment_change`. **NEW in v1.1** |
| `from_stage` | text | nullable — set when `activity_type = 'stage_change'` |
| `to_stage` | text | nullable — set when `activity_type = 'stage_change'` |
| **`from_agent_id`** | UUID | nullable, FK → users — set when `activity_type = 'assignment_change'`. **NEW in v1.1** |
| **`to_agent_id`** | UUID | nullable, FK → users — set when `activity_type = 'assignment_change'`. **NEW in v1.1** |
| `changed_by` | UUID | FK → users, nullable (NULL when the actor is the system, e.g. round-robin auto-assignment) |
| `changed_at` | timestamptz | |

> ⚠️ **Ownership changes were previously unrecorded**, which made per-agent attribution uncomputable: if Ravi worked a lead for two weeks and Meera closed it, whose conversion rate is it? Every agent-performance metric in FR12.2 depends on this history existing.

**This table is the source of truth for every time-based metric** — conversion rate, response time, time-in-stage. Not `leads.updated_at`.

### 3.11 `requirement_profiles` *(AI Recommendation input)*

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | |
| `user_id` | UUID | nullable — anonymous session allowed pre-registration |
| `session_id` | text | nullable — for anonymous tracking |
| `budget_min` / `budget_max` | numeric | nullable — **NULL means "no constraint", not zero.** A skipped budget step must be excluded from weighting and the remaining weights renormalized |
| `preferred_locations` | jsonb | |
| `property_type` | text | nullable |
| `purpose` | text | `self_use` · `investment` |
| `timeline` | text | `immediate` · `3_months` · `6_months_plus` |
| `must_have_amenities` | jsonb | Array of **amenity codes** from `amenities.code` (§3.18) |
| `alerts_enabled` | boolean | DEFAULT `true` — per-profile notification switch (FR3.4) |
| `last_viewed_at` | timestamptz | nullable — powers the "NEW since last visit" flag on matches |
| `created_at` / `updated_at` / `deleted_at` | timestamptz | Soft delete: deleting a profile must also stop its alerts |

**CHECK:** `user_id IS NOT NULL OR session_id IS NOT NULL` — a profile owned by nobody is unreachable.

### 3.12 `requirement_matches`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `requirement_profile_id` | UUID | FK |
| `property_id` | UUID | FK |
| `tenant_id` | UUID | |
| `match_score` | numeric | |
| `match_reason` | text | plain-language explanation, generated by Bedrock |
| `weights_version` | text | nullable — which `ai_config.recommendation_weights` produced this score. Lets stale matches be detected after a tenant retunes their weights |
| `notified_at` | timestamptz | nullable — **dedupe key: never notify twice about the same property for the same profile** |
| `generated_at` | timestamptz | |

**Uniqueness:** `UNIQUE (requirement_profile_id, property_id)`.

### 3.13 `chat_conversations`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | |
| `user_id` | UUID | nullable (anonymous) |
| `session_id` | text | nullable |
| `status` | text | `active` · `escalated` · `closed` · **`abandoned`** |
| **`escalated_at`** | timestamptz | nullable. **NEW in v1.1** |
| **`assigned_agent_id`** | UUID | nullable, FK → users — who picked up the escalation. **NEW in v1.1** |
| **`flagged`** | boolean | DEFAULT `false` — admin flags a conversation for review (FR13.2, which previously had no column). **NEW in v1.1** |
| **`flag_reason`** | text | nullable. **NEW in v1.1** |
| **`last_message_at`** | timestamptz | Lets a background job mark stale `active` conversations `abandoned`. **NEW in v1.1** |
| `created_at` / `updated_at` | timestamptz | |

> `abandoned` was added because a visitor who closes the tab leaves the conversation `active` **forever** — so the admin chat-log screen could not distinguish "in progress" from "the visitor left three weeks ago", and the conversion funnel was uncomputable.

### 3.14 `chat_messages`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `conversation_id` | UUID | FK → chat_conversations |
| `tenant_id` | UUID | |
| `sender` | text | `user` · `assistant` · `agent` |
| `message_text` | text | **Rendered in the admin transcript viewer → escape on output.** A visitor who types `<script>` must not get script execution in an admin's browser |
| `metadata` | jsonb | Tool calls made, property IDs referenced, model ID, latency, token usage. **This is what makes "never invent property facts" (FR1.3) *verifiable*** — a transcript without tool-call metadata can't prove where a price came from |
| `created_at` | timestamptz | |

### 3.15 `ai_config` *(supports PRD Module 13)*

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | **`UNIQUE`** — exactly one config row per tenant |
| `chatbot_greeting` | text | |
| `chatbot_faq` | jsonb | Q&A pairs. Injected into a **fixed prompt skeleton as data**, never as instructions |
| `escalation_rules` | jsonb | `{"on_explicit_request": true, "on_failed_attempts": 2, "on_frustration": true, "keywords": ["legal","complaint"], "handoff_message": "..."}` — shape was previously undefined |
| `recommendation_weights` | jsonb | e.g. `{"budget": 0.4, "location": 0.3, "amenities": 0.2, "property_type": 0.1}`. Must sum to 1.0 |
| `weights_version` | text | Bumped on each change; stamped onto `requirement_matches.weights_version` |
| `created_at` / `updated_at` | timestamptz | |

**A tenant created without an `ai_config` row has a chatbot with no greeting and a recommendation engine with no weights.** Provision a default row inside the tenant-creation transaction (`17-admin-spec/21` §4.1).

### 3.16 `cms_pages`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | |
| `slug` | text | **`UNIQUE (tenant_id, slug)`** — *not* globally unique. Two tenants both having `/about` is normal and correct |
| `page_type` | text | `page` · `post` — separates static pages from blog posts (FR14.1) |
| `title` | text | |
| `content` | text | Rich text/HTML. **⚠ Stored-XSS surface — see the warning below** |
| `excerpt` | text | nullable — for the blog index |
| `author_id` | UUID | nullable, FK → users |
| `seo_title` | text | |
| `seo_description` | text | |
| `published` | boolean | DEFAULT `false` |
| `published_at` | timestamptz | nullable — orders the blog index |
| `created_at` / `updated_at` / `deleted_at` | timestamptz | Soft delete (was a hard delete in v1.0) |

> ⚠️ **`content` is authored by a tenant admin and rendered on the public site — this is the most dangerous stored-XSS surface in the product.** Sanitize **on write** (strict tag/attribute allowlist: no `<script>`, no `on*` handlers, no `javascript:` URLs, no `<iframe>`) **and on render**. A tenant admin is not a trusted author in a multi-tenant SaaS, and a compromised admin account must not become script execution in every visitor's browser. Use a well-tested sanitizer; do not write your own.

**Reserved slugs** (must be rejected at authoring time — `/:slug` is a catch-all route and a page at `/search` would break the tenant's own property search): `search`, `property`, `portal`, `login`, `register`, `contact`, `requirement-analysis`, `admin`, `api`.

### 3.17 `cms_banners` *(supports FR14.1 — homepage banners)*

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | |
| `image_url` | text | Supabase Storage |
| `headline` | text | nullable |
| `subtext` | text | nullable |
| `cta_label` | text | nullable |
| `cta_url` | text | nullable |
| `sort_order` | int | |
| `is_active` | boolean | DEFAULT `true` |
| `created_at` / `updated_at` | timestamptz | |

FR14.1 requires editable homepage banners. A banner is an image + headline + CTA + order — it **cannot** be represented by `cms_pages` (slug + content blob), so the requirement was previously unbuildable.

### 3.18 `amenities` *(platform-level canonical vocabulary)*

Platform-level lookup — **not** tenant-scoped. Shared by every tenant so that matching is consistent.

| Column | Type | Notes |
|---|---|---|
| `code` | text | **PK.** Machine value, e.g. `swimming_pool`, `gym`, `covered_parking` |
| `label` | text | Display value, e.g. "Swimming pool" |
| `category` | text | `building` · `unit` · `security` · `recreation` · `utility` |
| `synonyms` | jsonb | Array — `["gymnasium", "fitness centre", "fitness center"]`. Used to fuzzy-match values during CSV bulk upload |
| `sort_order` | int | |
| `is_active` | boolean | |

> ⚠️ **This table is why the recommendation engine works at all.** `properties.amenities`, `requirement_profiles.must_have_amenities`, the public search filters, and the property form all previously assumed a shared vocabulary that existed nowhere. Without it, a listing tagged `gymnasium` never matches a buyer asking for `gym` — silently, with no error, degrading the product's flagship feature in a way that is nearly impossible to notice in testing.
>
> `properties.amenities` and `requirement_profiles.must_have_amenities` store **arrays of `amenities.code`**. Values are validated against this table at the service layer on write (jsonb can't carry an FK). Free-text amenities are not permitted.

### 3.19 `favorites` *(pre-login and post-login property saves)*

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | |
| `user_id` | UUID | nullable pre-login |
| `session_id` | text | for anonymous tracking, migrated to `user_id` on login |
| `property_id` | UUID | FK |
| `created_at` | timestamptz | |

**Uniqueness:** `UNIQUE (tenant_id, property_id, COALESCE(user_id::text, session_id))`.
**CHECK:** `user_id IS NOT NULL OR session_id IS NOT NULL`.

> Without the unique constraint, the anonymous-session migration produces **duplicate rows** for anyone who favorited a property anonymously and again after logging in (`16-customer-spec/16` §9).

### 3.20 `notifications` *(delivered notifications — supports FR7.1, FR3.4)*

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | |
| `user_id` | UUID | NOT NULL, FK → users. **Per-user, not per-tenant** — the ownership check is on `user_id` |
| `type` | text | `new_match` · `inquiry_update` · `price_change` · `property_unavailable` · `new_lead` · `lead_escalated` · `lead_stale` · `follow_up_due` · `property_pending_approval` · `listing_expiring` |
| `title` | text | |
| `body` | text | |
| `entity_type` | text | nullable — `property` · `lead` · `requirement_profile` |
| `entity_id` | UUID | nullable — the deep-link target |
| `read_at` | timestamptz | nullable |
| `created_at` | timestamptz | |

Serves **both** audiences: customer notifications (`/portal/notifications`) and staff notifications (the in-app channel of `notification_rules`). Same shape, differentiated by the recipient's role and the `type`.

> ⚠️ **Batch, don't spam.** A bulk upload of 200 properties (FR9.2), each matching a saved requirement profile, would otherwise generate 200 notifications for one customer. Batch per recipient per window ("12 new homes match your requirements"). This is not an edge case — it is what a real tenant onboarding looks like.

### 3.21 `notification_preferences` *(supports FR7.2)*

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | |
| `user_id` | UUID | NOT NULL, FK → users |
| `event_type` | text | Matches `notifications.type` |
| `email_enabled` | boolean | DEFAULT `true` for `new_match`, else `false` |
| `sms_enabled` | boolean | **DEFAULT `false`** — SMS costs money per send |
| `in_app_enabled` | boolean | DEFAULT `true` |
| `created_at` / `updated_at` | timestamptz | |

**Uniqueness:** `UNIQUE (user_id, event_type)`.

**Providers (decided 2026-07-13):** email → **SendGrid**, SMS → **Twilio**, in-app → the `notifications` table. All three ship at MVP. Credentials live in env vars via `core/config.py`; see `10-deployment-devops.md`.

- **SMS defaults off, everywhere.** It costs money per send, and a misconfigured rule ("SMS all agents on every new lead") on a busy tenant is a bill nobody approved. Ship it opt-in, with a per-tenant daily cap.
- **Indian SMS requires DLT registration** (sender ID + pre-approved templates). Twilio supports it, but template approval is a lead-time item — start it early or SMS will be the thing that blocks launch.
- **Unsubscribe links in emails must work without a login** — a signed, single-purpose token, not a session. Requiring a login to unsubscribe is a compliance problem, not just a UX one.
- **Dispatch happens in the jobs worker (§3.26), never inline.** A SendGrid outage must not fail lead creation.

### 3.22 `notification_rules` *(per-tenant staff routing — FR15.2)*

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | |
| `event_type` | text | `new_lead` · `lead_escalated` · `lead_stale` · `lead_assigned` · `follow_up_due` · `property_pending_approval` · `listing_expiring` |
| `channel` | text | `email` · `sms` · `in_app` |
| `recipients` | jsonb | `{"mode": "assigned_agent"}` · `{"mode": "users", "ids": [...]}` · `{"mode": "role", "role": "admin"}` |
| `is_active` | boolean | |
| `created_at` / `updated_at` | timestamptz | |

> ⚠️ **`recipients` is a jsonb blob of user IDs — nothing structurally prevents it naming a user in another tenant.** That would email one tenant's lead data (name, phone, property interest) to another tenant's staff: a cross-tenant leak by email, which is both the worst kind and the hardest to walk back. **Validate recipient IDs against the tenant's own `users` on write *and* re-check on dispatch.**

**Seed a default rule on tenant creation** (`new_lead` → `email` → `assigned_agent`). A tenant with no rules captures leads and tells nobody.

### 3.23 `audit_log` *(append-only — supports FR11.3)*

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | |
| `actor_id` | UUID | nullable, FK → users — NULL only when `actor_type = 'system'` |
| `actor_type` | text | `user` · `system` · `super_admin` |
| `action` | text | `property.publish`, `user.role_change`, `lead.reassign`, `report.export`, … |
| `entity_type` | text | `property` · `lead` · `user` · `ai_config` · `cms_page` · `tenant` |
| `entity_id` | UUID | nullable — the entity may since have been deleted |
| `entity_label` | text | nullable — denormalized name, so the entry stays readable after the entity is gone |
| `changes` | jsonb | nullable — `{"price": {"from": 7800000, "to": 7500000}}`. A diff, **not** a full row snapshot (which would bloat the table and duplicate PII into a second place you must protect) |
| `ip_address` | inet | nullable |
| `created_at` | timestamptz | DEFAULT now() |

**No `updated_at`. No `deleted_at`. Append-only by design.**

> ⚠️ **Enforce append-only at the database level** — `REVOKE UPDATE, DELETE ON audit_log` from the application role. Not merely by declining to write an update endpoint. The application will eventually have a bug; the grant will not. An audit log that the people it audits can edit is theatre.

**What gets logged:** every write in the admin portal — property create/update/publish/approve/reject/status/archive/bulk-import; lead stage change/reassign/note/manual create; **user invite/role change/deactivate** (the highest-value entries); AI config changes; CMS changes; tenant/branding changes; report exports (they carry customer PII out of the system). Ordinary reads are **not** logged — that produces a log too noisy to use.

**Implementation:** one service-layer hook that every mutating service method passes through, **not** a manual `audit_log.write(...)` sprinkled per endpoint — the manual approach is guaranteed to be incomplete within a month, and the gaps will be exactly the endpoints someone added in a hurry. The audit write must be **in the same transaction** as the change it records.

**Failed/denied actions are logged too.** Repeated 403s from one agent against `/admin/users` is precisely the signal an audit log exists to surface, and it is invisible if you only log successes.

**A super_admin's actions on a tenant appear in that tenant's log** (`17-admin-spec/12` §8).

### 3.24 `search_queries` *(AI-search telemetry — supports FR13.4)*

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | |
| `session_id` | text | nullable |
| `user_id` | UUID | nullable |
| `raw_query` | text | **User-generated text from an anonymous visitor, rendered in the admin's browser → escape on output** |
| `parsed_query` | jsonb | The structured parse. **This is the clustering key** — "3bhk under 40 lakhs" and "3 BHK under ₹40L" are the same demand signal and must count as one |
| `result_count` | int | The zero-result queries are the commercially valuable ones |
| `used_fallback` | boolean | DEFAULT `false` — did the AI parse fail and fall back to keyword search (FR2.7)? A rising rate is how you detect the AI layer degrading before customers complain |
| `latency_ms` | int | |
| `model_id` | text | |
| `input_tokens` / `output_tokens` | int | Cost tracking |
| `created_at` | timestamptz | |

Satisfies `.claude/rules/ai.md`'s "log every Bedrock call's latency, token usage, and model ID" **in a queryable form** — ops logs can't answer *"which queries returned nothing this month?"*

> ⚠️ **Must exist before the first AI search runs (Sprint 5).** You cannot backfill searches you never recorded, and this data is what makes the AI improvable.

### 3.25 `bulk_uploads` / `bulk_upload_rows` *(supports FR9.2)*

`bulk_uploads`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | |
| `uploaded_by` | UUID | FK → users |
| `filename` | text | |
| `status` | text | `validating` · `validated` · `importing` · `completed` · `failed` |
| `total_rows` / `valid_rows` / `failed_rows` | int | |
| `created_at` / `updated_at` | timestamptz | |

`bulk_upload_rows`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `bulk_upload_id` | UUID | FK → bulk_uploads |
| `tenant_id` | UUID | |
| `row_number` | int | The row in the user's spreadsheet — **they need to find it in Excel** |
| `raw_data` | jsonb | The parsed row, so failed rows can be re-exported for fixing |
| `status` | text | `valid` · `error` · `imported` |
| `error_column` | text | nullable |
| `error_message` | text | nullable — "price is not a number: 'on request'" |
| `property_id` | UUID | nullable — set once imported |

FR9.2 requires "validation **and error reporting**", which implies a persisted job with per-row results: the admin uploads 142 rows, walks away, comes back. Nothing modeled that.

> ⚠️ **A `tenant_id` column present in the uploaded CSV must be *ignored*, not honored.** A naive "map the CSV columns onto the model" implementation is a trivially exploitable cross-tenant write.

### 3.26 `jobs` *(the async work queue — NEW in v1.2)*

Background work runs as **pg_cron (SQL-only time jobs) + a Python worker polling this table** (decided 2026-07-13). No Celery, no Redis. See `02-architecture.md` §4.4.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | nullable — a few platform-level jobs have no tenant |
| `job_type` | text | `embed_property` · `deindex_property` · `bulk_import` · `dispatch_notification` · `match_new_property` |
| `payload` | jsonb | e.g. `{"property_id": "..."}` |
| `status` | text | `pending` · `running` · `succeeded` · `failed` · `dead` |
| `attempts` | int | DEFAULT 0 |
| `max_attempts` | int | DEFAULT 5 |
| `run_after` | timestamptz | DEFAULT now() — enables backoff and future scheduling |
| `locked_at` | timestamptz | nullable — set when a worker picks it up |
| `locked_by` | text | nullable — worker instance ID |
| `last_error` | text | nullable |
| `created_at` / `updated_at` | timestamptz | |

**Who enqueues:** FastAPI (on publish, on bulk upload, on lead creation) **and** pg_cron (which can `INSERT` into this table even though it can't run Python).

**Claiming a job must be atomic** — the same race as claiming a lead, and with multiple workers it *will* happen:

```sql
UPDATE jobs SET status='running', locked_at=now(), locked_by=:worker, attempts=attempts+1
 WHERE id = (
   SELECT id FROM jobs
    WHERE status='pending' AND run_after <= now()
    ORDER BY run_after
    FOR UPDATE SKIP LOCKED          -- the important part
    LIMIT 1)
RETURNING *;
```

`FOR UPDATE SKIP LOCKED` is what makes a Postgres-backed queue safe with concurrent workers. Without it, two workers embed the same property twice, or send the same SMS twice.

> ⚠️ **You are hand-rolling retry, backoff, and dead-lettering** — that's the accepted cost of avoiding Redis. Get three things right or the queue will quietly lose work: (1) exponential backoff via `run_after`, (2) a `dead` status after `max_attempts` with the error retained, (3) **a stuck-job reaper** — a worker that crashes mid-job leaves a row `running` with a stale `locked_at`, and nothing will ever retry it. pg_cron should reset those.

> ⚠️ **A failed `embed_property` job is invisible in the product.** The property is live on the site and simply never appears in AI search. No error, no broken page — just a listing that silently doesn't exist to the feature the product is sold on. **Alert on `jobs` rows reaching `dead`**, and surface un-indexed published properties in the admin property list.

### 3.27 `site_sessions` *(visitor counting — NEW in v1.2)*

Backs the "site visitors" KPI (FR8.1) with a **self-hosted counter** rather than third-party analytics (decided 2026-07-13) — no vendor, no cookie-consent banner, tenant-scoped by construction.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | |
| `session_id` | text | The `X-Session-Id` we already receive on every public request |
| `first_seen_at` | timestamptz | |
| `last_seen_at` | timestamptz | |
| `page_views` | int | |

**Uniqueness:** `UNIQUE (tenant_id, session_id)`.

> **Label it honestly: this counts *sessions*, not people.** One person on a phone and a laptop is two sessions; one who clears storage is two more. The dashboard card must say "Sessions", not "Visitors" — a KPI that overstates by an unknown factor is worse than no KPI, and FR8.1's original wording ("site visitors") is what we are deliberately *not* claiming.

### 3.28 Rollup tables *(retention — NEW in v1.2)*

`property_views` and `search_queries` are high-volume and grow without bound. Raw rows are purged after 90 days into daily aggregates (§8).

`property_views_daily`

| Column | Type |
|---|---|
| `tenant_id` · `property_id` · `day` (date) · `view_count` (int) |

**Uniqueness:** `UNIQUE (tenant_id, property_id, day)`.

`search_queries_daily`

| Column | Type | Notes |
|---|---|---|
| `tenant_id` · `day` (date) | | |
| `query_cluster` | jsonb | The `parsed_query` shape, used as the clustering key |
| `search_count` | int | |
| `zero_result_count` | int | Preserves the FR13.4 insight after the raw rows are gone |
| `avg_latency_ms` | int | |
| `fallback_count` | int | |

Rolled up nightly by pg_cron. **The insight survives the purge** — an admin can still see "47 people searched for a 3BHK under ₹40L in Indiranagar and found nothing" a year later, without us retaining a year of raw query text.

---

## 4. Row-Level Security (RLS) Pattern

Applied to **every tenant-owned table** — that is, all tables in §3 **except** `tenants` (platform-level) and `amenities` (platform-level lookup).

```sql
-- Example: properties table
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_select ON properties
  FOR SELECT
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

CREATE POLICY tenant_isolation_write ON properties
  FOR ALL
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
  WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

The FastAPI request lifecycle sets `app.current_tenant_id` via `SET LOCAL` at the start of each transaction (implemented in `core/tenancy.py`, per `02-architecture.md`). This is the same pattern repeated per table — **apply it through one reusable migration helper/macro**, reused in each tenant-owned table's migration, rather than hand-writing per-table SQL (`.claude/rules/database.md`).

**Every tenant-owned table added in v1.1/v1.2** (`property_views`, `property_views_daily`, `notifications`, `notification_preferences`, `cms_banners`, `search_queries`, `search_queries_daily`, `audit_log`, `bulk_uploads`, `bulk_upload_rows`, `site_sessions`) **needs the RLS helper applied and an explicit cross-tenant-access test** — a test proving a Tenant A user cannot read or write Tenant B rows, failing at the **DB layer**, not just the API layer.

**`jobs` is the exception, and the dangerous one.** The worker processes jobs across every tenant, so it connects with a role that **bypasses RLS**. It must therefore `SET LOCAL app.current_tenant_id` from `jobs.tenant_id` before touching any tenant data. **A worker that forgets has no tenant isolation whatsoever** — RLS is not there to catch it. This is the highest-risk code path in the system and needs its own cross-tenant test (§7).

### 4.1 Tables outside RLS — and why that's dangerous

| Table | Why it's outside | The consequence |
|---|---|---|
| `tenants` | It's the table `tenant_id` references | **There is no database backstop here.** Every other table has RLS to catch an application bug; this one does not. The `require_role(["super_admin"])` dependency and the "derive the tenant from the authenticated user, never from a request parameter" rule on `PUT /admin/tenant/branding` are the *only* things standing between a tenant admin and another tenant's row. Both need explicit tests |
| `amenities` | A shared, read-only vocabulary | Read-only to tenants; writable only by platform migrations |

### 4.2 User-level isolation is *not* RLS's job

RLS gives **tenant** isolation. It does **not** give **user** isolation within a tenant — nothing in the policy above stops Customer A reading Customer B's `favorites`, `notifications`, `requirement_profiles`, or `leads`, since both rows carry the same `tenant_id`.

**Every `/portal/*` query must additionally filter on `user_id = <authenticated user>` in the repository layer**, and every by-ID fetch (`GET /ai/recommend/{id}`, `DELETE /properties/{id}/favorite`) must verify ownership. This is the most likely IDOR class in the product and it needs its own tests — a tenant-isolation test will pass while user isolation is completely broken.

---

## 5. Indexes (Key Ones)

- `tenants`: `UNIQUE (domain)`.
- `users`: `UNIQUE (auth_user_id, tenant_id)`, index on `(tenant_id, role)`.
- `properties`: `(tenant_id, status)`, `(tenant_id, is_featured)`, `(tenant_id, agent_id)`, GIN on `amenities` (jsonb), and `(tenant_id, expires_at)` for the expiry job.
- `property_embeddings`: `ivfflat` or `hnsw` on `embedding` (pgvector), plus `tenant_id` as a filter column, and `UNIQUE (property_id)`.
- `property_views`: `(tenant_id, property_id, viewed_at)`.
- `leads`: `(tenant_id, stage)`, `(tenant_id, assigned_agent_id)`, **`(tenant_id, user_id)`**, **`(tenant_id, session_id)`**, `UNIQUE (tenant_id, idempotency_key)`.
- `lead_activities`: `(tenant_id, lead_id, changed_at)`.
- `requirement_matches`: `UNIQUE (requirement_profile_id, property_id)`.
- `chat_messages`: `(conversation_id, created_at)`.
- `chat_conversations`: `(tenant_id, status)`.
- `notifications`: `(tenant_id, user_id, read_at)`.
- `notification_preferences`: `UNIQUE (user_id, event_type)`.
- `favorites`: `UNIQUE (tenant_id, property_id, COALESCE(user_id::text, session_id))`.
- `cms_pages`: `UNIQUE (tenant_id, slug)`.
- `audit_log`: `(tenant_id, created_at DESC)`, `(tenant_id, actor_id)`, `(tenant_id, entity_type, entity_id)`.
- `search_queries`: `(tenant_id, created_at DESC)`, `(tenant_id, result_count)` — the zero-result query is the point.
- `jobs`: `(status, run_after)` — the worker's poll query hits this on every tick.
- `site_sessions`: `UNIQUE (tenant_id, session_id)`, `(tenant_id, first_seen_at)`.

> ⚠️ **The pgvector `tenant_id` filter must be *inside* the query, not applied to the results.** Post-filtering the global top-50 neighbours "works" with one tenant and leaks the moment there are two — and it silently returns *fewer* results than requested for a small tenant, because the nearest neighbours are dominated by whichever tenant has the largest inventory. Test it with two tenants holding near-identical listings; a single-tenant test passes either way and proves nothing.

---

## 6. Canonical Metric Definitions

**Conversion rate, active leads, and response time appear on three screens** — the [Dashboard](17-admin-spec/02-dashboard.md), the [Agents leaderboard](17-admin-spec/10-agents.md), and [Reports](17-admin-spec/18-reports.md) — and FR15.1 requires all three to agree. They will not agree if each screen writes its own SQL.

**These definitions are normative. One `metrics_service.py` computes them; all three screens call it.** Nothing else may define them.

| Metric | Definition (decided 2026-07-13) |
|---|---|
| **Conversion rate** | `closed_won ÷ (closed_won + closed_lost)`, over leads that **reached a terminal stage within the period** (by `lead_activities.changed_at`, not `leads.created_at`). It measures *closing effectiveness* and is not skewed by leads still in flight. It deliberately says nothing about open leads |
| **Active leads** | Leads with `stage NOT IN ('closed_won','closed_lost')` and `deleted_at IS NULL` |
| **Response time** | `lead_activities.changed_at` for the first move out of `new`, minus `leads.created_at`. ⚠️ This measures **how fast an agent records contact**, not how fast they contact. An agent who calls and logs nothing scores badly; one who logs without calling scores well. Treat it as a hygiene metric, not a truth |
| **Unclaimed age** | `now() - leads.created_at` where `assigned_agent_id IS NULL`. The number that matters most under manual claim (§3.8.1) — it is how you catch a queue rotting |
| **Sessions** | Distinct `site_sessions` rows in the period. **Sessions, not people** (§3.27) |

**Every metric excludes `deleted_at IS NOT NULL` rows, and is computed in the tenant's `timezone` (§3.1)** — not UTC, not the browser's. Two admins in the same company must see the same number.

Zero denominator → render `—`, never `0%` and never `NaN`.

---

## 7. Background Work: pg_cron + a Python Jobs Worker

Decided 2026-07-13. Full architecture in `02-architecture.md` §4.4.

The split exists because **pg_cron is SQL-only** — it cannot call Bedrock, SendGrid, Twilio, or parse a CSV.

```
┌─ pg_cron (in Postgres, SQL only) ──────────────────────────────┐
│  • mark leads stale            → INSERT INTO jobs (notify)     │
│  • expire listings             → INSERT INTO jobs (notify)     │
│  • mark abandoned chats        (pure SQL, no notify)           │
│  • follow-up reminders due     → INSERT INTO jobs (notify)     │
│  • nightly rollups + purges    (pure SQL)                      │
│  • reap stuck jobs             (reset stale `running` rows)    │
└────────────────────────────────────────────────────────────────┘
                          │ enqueues
                          ▼
                    ┌───────────┐
FastAPI ──enqueue──►│   jobs    │◄──poll (FOR UPDATE SKIP LOCKED)──┐
                    └───────────┘                                   │
                                                        ┌───────────┴──────────┐
                                                        │ Python jobs worker    │
                                                        │  • embed_property     │
                                                        │    (Bedrock/Titan)    │
                                                        │  • deindex_property   │
                                                        │  • match_new_property │
                                                        │  • bulk_import (CSV)  │
                                                        │  • dispatch_notif.    │
                                                        │    (SendGrid/Twilio)  │
                                                        └───────────────────────┘
```

**Reports are synchronous** (decided 2026-07-13) — generated in-request with a row cap, exported by re-running the query. There is no `reports` table and no report job. If a tenant's date range exceeds the cap, tell them to narrow it rather than silently truncating.

**The worker connects with a role that bypasses RLS** (it processes jobs across tenants), so it **must set `app.current_tenant_id` explicitly from `jobs.tenant_id` before touching tenant data.** A worker that forgets is a worker with no tenant isolation at all — this is the single most dangerous piece of code in the system, and it needs a cross-tenant test of its own.

---

## 8. Retention

Decided 2026-07-13. Enforced by nightly pg_cron jobs.

| Data | Retention | Then |
|---|---|---|
| `property_views` | 90 days raw | Rolled up to `property_views_daily`, raw rows purged |
| `search_queries` | 90 days raw | Rolled up to `search_queries_daily` (zero-result insight preserved), raw rows purged |
| `chat_messages` / `chat_conversations` | **24 months** | Purged. These are the most sensitive PII in the product — transcripts contain names, phones, budgets, and personal circumstances |
| `audit_log` | **7 years** | Never rolled up, never purged inside the window. It is the accountability record; that is the whole point of it |
| `lead_activities` | Retained with the lead | Follows the lead's own lifecycle |
| Orphaned anonymous rows (`favorites`, `requirement_profiles`, `chat_conversations` with `user_id IS NULL`) | 90 days | Purged |
| `jobs` (succeeded) | 30 days | Purged. `dead` rows are **kept** — they are a failure record |

> The tension is real and worth naming: **chat transcripts are simultaneously the highest-value debugging data in the product and the most sensitive PII in it.** 24 months is the compromise. If a tenant's market has a stricter statutory requirement, this is the number that changes.

---

## 9. Provisioning a New Tenant

A tenant row on its own is a broken workspace. Creating a tenant must, **in one transaction**, also create:

1. The `tenants` row.
2. A default **`ai_config`** row — without it the chatbot has no greeting and the recommendation engine has no weights.
3. Default **`notification_rules`** (`new_lead` → `email` → `assigned_agent`) — without it, leads arrive and nobody is told.
4. Starter **`cms_pages`** drafts (About, Terms, Privacy) — a site whose footer links 404 looks broken.
5. The first **`users`** row (`role = 'admin'`), invited — a tenant with no admin is a workspace nobody can enter.

A partial failure here leaves a tenant that appears to exist and doesn't work.

---

## 10. Decisions & Remaining Questions

### 10.1 Decisions taken (2026-07-13) — normative, do not re-litigate in code

| # | Decision | Consequence |
|---|---|---|
| 1 | **Pipeline stages are a fixed enum** (6 values) | FR10.1's "configurable stage names" is dropped. `01-prd.md` updated to match |
| 2 | **Leads are manually claimed from a shared queue**, not auto-assigned | `assigned_agent_id` is NULL on creation; the Kanban `new` column is shared; claiming is an atomic conditional update (§3.8.1) |
| 3 | **Four fixed roles**; `roles_permissions` sub-roles deferred | One permission system, not two |
| 4 | **One `users` row per (auth identity, tenant)** | A person can be a customer on one tenant and staff on another. **Every lookup must pass `tenant_id`** |
| 5 | **Reports are synchronous and row-capped** | No `reports` table, no report job (§7) |
| 6 | **pg_cron (SQL jobs) + a Python worker polling `jobs`** | No Celery, no Redis. Retry/backoff/dead-lettering are hand-rolled (§3.26, §7) |
| 7 | **Notifications: in-app + email (SendGrid) + SMS (Twilio)** | SMS opt-in and capped. DLT registration is a lead-time item |
| 8 | **Suspension keeps the public site up and blocks admin login** | We absorb the Bedrock cost of a suspended tenant (§3.1) |
| 9 | **Self-hosted `site_sessions` counter**, not third-party analytics | The KPI is labelled "Sessions", not "Visitors" (§3.27) |
| 10 | **Conversion = won ÷ closed-in-period** | One `metrics_service` for all three screens (§6) |
| 11 | **Match score shown to customers as a raw percentage** | "92% match" on search and recommendation cards |
| 12 | **Agent scope:** read-only on colleagues' leads; may create/edit properties (drafts only); sees the leaderboard; reads transcripts of their own leads | `08-auth-roles-spec.md` §5 updated |
| 13 | **Retention:** 90d raw → rollups; chats 24 months; audit 7 years | Enforced by pg_cron (§8) |

### 10.2 Accepted risks — chosen knowingly, recorded so they resurface

| Risk | What was accepted |
|---|---|
| **Single public Storage bucket for all media, including `document`** | Any uploaded document is world-readable to anyone with the URL. Fine for brochures; **an incident the day someone uploads an ownership paper or ID scan.** Mitigation if that happens: private bucket + signed URLs (§3.5) |
| **No 2FA on the admin portal** | Password-only for `admin` and `super_admin`. One phished password exposes that tenant's entire customer database — names, phones, budgets, chat transcripts. Supabase Auth supports MFA whenever this is revisited |
| **Manual claim leaves leads ownerless** | A lead arriving at 9pm Friday belongs to nobody until an agent picks it up. The `lead_stale` rule is the only safety net — **it must actually be configured**, or the queue rots silently (§3.8.1) |
| **Suspended tenants keep costing us Bedrock spend** | Their public site, search, and chatbot stay live (§3.1) |

### 10.3 Still open — but no longer blocking the schema

- [ ] **SVG logo uploads** (`tenants.branding_logo_url`) — an SVG is executable content and can carry a `<script>`. Either sanitize properly or restrict to PNG/JPG. A one-line decision; not yet made.
- [ ] **Staleness thresholds** for the `lead_stale` rule (§3.8.1) — per stage, per tenant, or a fixed default? This is now load-bearing, because manual claim makes it the only thing preventing unclaimed leads from rotting.
- [ ] **Per-tenant SMS spend cap** — a number is needed (`10-deployment-devops.md`).
- [ ] **Per-tenant SSL provisioning** for custom domains (`10-deployment-devops.md`) — infrastructure, not schema.
- [ ] **DLT template registration** for Indian SMS — a process with lead time, not a code task.

---

## 11. Changelog

### v1.2 (2026-07-13) — applied the MVP product decisions

**New tables:** `jobs` (§3.26 — the async work queue), `site_sessions` (§3.27 — visitor counting), `property_views_daily` + `search_queries_daily` (§3.28 — retention rollups).

**New columns:** `leads.claimed_at`.

**New normative sections:** §6 canonical metric definitions (three screens, one service), §7 the pg_cron + jobs-worker split, §8 retention, §3.1 what each `tenants.status` does, §3.8.1 manual-claim mechanics including the atomic-claim SQL.

**Reversed from v1.1:** the Storage bucket recommendation. v1.1 said `document` needed a private bucket; the decision is a **single public bucket for everything**, now recorded as an accepted risk (§10.2) rather than a recommendation.

**Confirmed from v1.1** (were assumptions, now decisions): fixed pipeline stages, stateless/synchronous reports, deferred `roles_permissions`, `users` unique per `(auth_user_id, tenant_id)`.

### v1.1 → the gap-closing pass

Every change below closes a gap that made a stated requirement **unbuildable or unsafe**. Nothing here is speculative scope.

### New tables

| Table | Closes |
|---|---|
| `amenities` (§3.18) | The canonical vocabulary the wizard, filters, property form, and matcher all assumed existed. Without it, `gymnasium` ≠ `gym`, silently |
| `notifications` (§3.20) | FR7.1 / FR3.4 — `/portal/notifications` had no table |
| `notification_preferences` (§3.21) | FR7.2 — `PUT /portal/notifications/preferences` had nowhere to write |
| `audit_log` (§3.23) | FR11.3 — required by the PRD, the API spec, **and** `.claude/rules/security.md`; existed nowhere |
| `search_queries` (§3.24) | FR13.4 — "queries with no/low results" had no data source |
| `property_views` (§3.7) | FR8.2 — the "property views over time" chart had no data source |
| `cms_banners` (§3.17) | FR14.1 — homepage banners can't be a `cms_pages` row |
| `bulk_uploads` / `bulk_upload_rows` (§3.25) | FR9.2 — "validation and error reporting" implies a persisted job |

### New columns

| Table | Columns | Closes |
|---|---|---|
| `leads` | `user_id`, `session_id` | **The data-leak vector.** FR7.1 inquiry history had no correct implementation, and matching on `customer_email` is exploitable |
| `leads` | `requirement_profile_id`, `chat_conversation_id` | The lead detail panel's most valuable content — *what this person wants* and *what they already told the bot* — was unreachable |
| `leads` | `requested_callback_at`, `requested_slot` | FR6.2's callback slot had nowhere to be stored |
| `leads` | `deal_value` | FR15.1's "sales report" could only report asking prices |
| `leads` | `idempotency_key`, `message` | FR6.4's no-duplicate-leads criterion had no mechanism |
| `leads.source` | `+ property_details` | Resolves the contradiction with `14-screen-workflows.md` §4 |
| `lead_activities` | `activity_type`, `from_agent_id`, `to_agent_id` | Ownership changes were unrecorded → per-agent attribution (FR12.2) was uncomputable |
| `properties` | `created_by` | Agent ownership-scoping was inexpressible |
| `properties` | `expires_at` | FR15.2's `listing_expiring` event could never fire |
| `properties` | `embedding_source_hash` | Avoids re-embedding on every save while catching genuine content changes |
| `chat_conversations` | `flagged`, `flag_reason` | FR13.2's "flagging for review" had no column |
| `chat_conversations` | `status = 'abandoned'`, `last_message_at`, `escalated_at`, `assigned_agent_id` | An abandoned conversation stayed `active` forever |
| `tenants` | `requires_property_approval` | FR9.3's per-tenant approval flag had no home |
| `tenants` | `timezone` | Every dated KPI/report was ambiguous |
| `tenants` | `contact_*`, `business_hours` | The public Contact page had nothing to render |
| `tenants` | `domain_verified_at`, `branding_accent_color` | Domain hijacking was possible; one color isn't a brand |
| `requirement_profiles` | `alerts_enabled`, `last_viewed_at`, `deleted_at` | FR7.3 delete; per-profile alerts; "NEW since last visit" |
| `requirement_matches` | `notified_at`, `weights_version` | Duplicate notifications; stale-score detection |
| `ai_config` | `weights_version`, explicit `escalation_rules` shape | The jsonb blob had no defined structure to build a form against |
| `cms_pages` | `page_type`, `excerpt`, `author_id`, `published_at`, `deleted_at` | A blog index couldn't be listed or ordered; delete was destructive |

### New constraints

- `tenants.domain` **UNIQUE** — ambiguous tenant resolution is a data breach, not a data-quality issue.
- `users` **UNIQUE (auth_user_id, tenant_id)** — one person can legitimately exist in two tenants.
- `favorites` **UNIQUE (tenant_id, property_id, COALESCE(user_id, session_id))** — the session→account migration was creating duplicates.
- `cms_pages` **UNIQUE (tenant_id, slug)** — *not* globally unique; two tenants both having `/about` is correct.
- `requirement_matches` **UNIQUE (requirement_profile_id, property_id)** — dedupe.
- `leads` **UNIQUE (tenant_id, idempotency_key)** — FR6.4.
- `ai_config.tenant_id` **UNIQUE** — one config per tenant.
- `audit_log` — **append-only, enforced by `REVOKE UPDATE, DELETE`** at the database level.

---

**Next document:** `04-api-spec.md` — REST API endpoints for both the public site and admin portal, built directly on these tables.
