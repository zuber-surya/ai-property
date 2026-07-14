# Customer Section — Detailed Spec (Index)

> **Doc 16 of the PropVista CRM documentation set.** The full, page-by-page and feature-by-feature specification for the **customer-facing surface** — the public site (anonymous visitors) and the customer portal (registered customers). This is the implementation-level companion to `01-prd.md` (Modules 1–7): where the PRD says *what* must exist, this set says *what each page contains, how it behaves, which endpoints it calls, and which tables it touches*.
>
> **Status:** Draft v1.0 · **Last updated:** July 2026
> Implemented in: `public-site/` (see `02-architecture.md` §5.2)
> Depends on: `01-prd.md`, `03-database-schema.md`, `04-api-spec.md`, `05`/`06`/`07-ai-*.md`, `08-auth-roles-spec.md`, `13-ui-ux-flows.md`, `14-screen-workflows.md`
> Admin counterpart: `docs/17-admin-spec/`

---

## 1. How to Use This Doc Set

One file per **page** (a route the customer can land on) and one file per **feature** (a widget or behavior that spans multiple pages). Open the file for the thing you're building; each is self-contained and traces back to the FR numbers and `TC-*` cases it must satisfy.

**Every page file follows the same 11-section template** so you always know where to look:

| Section | Answers |
|---|---|
| 1. Purpose & Traceability | Why this page exists; PRD module + FR numbers |
| 2. Entry & Exit Points | How the customer gets here, and where they go next |
| 3. Layout & Regions | Wireframe + what each region contains |
| 4. Workflow | The click-by-click interaction sequence |
| 5. States | Loading, empty, error, partial-data, logged-out vs. logged-in |
| 6. API Calls | Every request this page makes, and when |
| 7. Data Touched | Tables read/written (from `03-database-schema.md`) |
| 8. Permissions & Tenancy | Auth requirement, tenant scoping, session handling |
| 9. Validation & Edge Cases | Input rules and the ugly cases |
| 10. Acceptance Criteria | The `TC-*` cases from `docs/15-development-plan.md` |
| 11. Open Questions | Unresolved decisions — **do not guess these, resolve them** |

---

## 2. Page Index

### 2.1 Public Pages (no login required)

| # | File | Route | PRD Module |
|---|---|---|---|
| 01 | [`01-homepage.md`](01-homepage.md) | `/` | 2, 4 |
| 02 | [`02-property-listing.md`](02-property-listing.md) | `/search` | 4 |
| 03 | [`03-property-details.md`](03-property-details.md) | `/property/:id` | 5 |
| 04 | [`04-requirement-wizard.md`](04-requirement-wizard.md) | `/requirement-analysis` | 3 |
| 05 | [`05-contact-page.md`](05-contact-page.md) | `/contact` | 6 |
| 06 | [`06-auth-register-login.md`](06-auth-register-login.md) | `/login`, `/register` | 7 |
| 12 | [`12-static-cms-pages.md`](12-static-cms-pages.md) | `/:slug` | 14 (consumer side) |

### 2.2 Customer Portal (authenticated)

| # | File | Route | PRD Module |
|---|---|---|---|
| 07 | [`07-portal-dashboard.md`](07-portal-dashboard.md) | `/portal` | 7 |
| 08 | [`08-portal-favorites.md`](08-portal-favorites.md) | `/portal/favorites` | 7 |
| 09 | [`09-portal-requirements.md`](09-portal-requirements.md) | `/portal/requirements` | 7, 3 |
| 10 | [`10-portal-inquiries.md`](10-portal-inquiries.md) | `/portal/inquiries` | 7 |
| 11 | [`11-portal-notifications.md`](11-portal-notifications.md) | `/portal/notifications` | 7, 15 |

### 2.3 Cross-Page Features (widgets, not routes)

| # | File | Appears On | PRD Module |
|---|---|---|---|
| 13 | [`13-feature-ai-search.md`](13-feature-ai-search.md) | Homepage, Property Listing header | 2 |
| 14 | [`14-feature-ai-chatbot.md`](14-feature-ai-chatbot.md) | Every public page | 1 |
| 15 | [`15-feature-lead-capture.md`](15-feature-lead-capture.md) | Property Details, Contact, Chatbot | 6 |
| 16 | [`16-feature-favorites-session.md`](16-feature-favorites-session.md) | Homepage, Listing, Details, Portal | 4, 7 |

---

## 3. Site Map

Authoritative version lives in `13-ui-ux-flows.md` §3.1; repeated here for convenience.

```
/ (Homepage)
├── /search                     Property Listing — AI search results + filters
├── /property/:id               Property Details
├── /requirement-analysis       Guided requirement wizard (AI Recommendation)
├── /contact                    Contact / lead capture
├── /login, /register           Auth
├── /:slug                      CMS static pages (About, Terms, Careers, blog posts)
└── /portal                     Customer Portal (authenticated)
    ├── /portal/favorites
    ├── /portal/requirements
    ├── /portal/inquiries
    └── /portal/notifications

Chat widget: overlays every route above (not a route of its own).
```

---

## 4. Cross-Cutting Rules for Every Customer Page

These apply to all pages below. They are stated once here rather than repeated in each file.

### 4.1 Tenant resolution is server-side, always
The tenant is resolved **from the request's origin domain/subdomain**, never from a client-supplied value (`04-api-spec.md` §1, `.claude/rules/security.md`). The React app never sends a `tenant_id`, and no customer-facing endpoint accepts one. Every list, search, chat, and recommendation is implicitly scoped to the tenant that owns the domain being visited.

### 4.2 Anonymous-first — login is never a gate for value
A visitor can browse, search, chat, favorite, run the requirement wizard, and submit an inquiry **without an account** (`08-auth-roles-spec.md` §4). The registration prompt appears *after* a persist-worthy action, never before it (`13-ui-ux-flows.md` §2.1).

- Anonymous identity = a client-generated `session_id`, sent as the `X-Session-Id` header on every request.
- The session_id is generated once on first visit and stored in `localStorage`.
- On register/login, session-owned rows (`favorites`, `requirement_profiles`, `chat_conversations`) are re-keyed from `session_id` to `user_id`. See `16-feature-favorites-session.md` §5 for the migration contract.

### 4.3 Auth state
Supabase Auth issues the JWT; the Supabase JS client handles refresh (`08-auth-roles-spec.md` §2.4). The app holds auth + tenant branding in React Context (`context/`, per `.claude/rules/frontend.md`) — nothing else is cross-cutting enough for Context.

### 4.4 Error presentation
The backend returns `{"error": {"code": ..., "message": ...}}` (`04-api-spec.md` §1). The UI **never renders a raw error code** to the customer. Map codes to human copy; fall back to a generic "Something went wrong — please try again" for unmapped codes. AI endpoints degrade rather than fail (§4.5).

### 4.5 AI features degrade, they do not break
Per `.claude/rules/ai.md`, every AI surface has a non-AI fallback:

| Feature | On failure/timeout/rate-limit |
|---|---|
| AI Search | Fall back to standard filter search on the raw keywords (FR2.7) |
| AI Chatbot | Show a "connect me to an agent" path; never a dead chat window |
| AI Recommendation | Show closest-match fallback list, never an empty state (FR3.2) |

A rate-limited (`429`) AI response is a *degradation*, not an error toast — public `ai/*` endpoints are rate-limited per session/IP to cap Bedrock cost.

### 4.6 Responsive
Breakpoints per `13-ui-ux-flows.md` §4.7 (mobile <640, tablet 641–1024, desktop >1024). Every customer page must be usable on mobile (PRD §18). Touch targets ≥44×44px — this specifically covers the chat launcher and the favorite heart icon.

### 4.7 Design system
**Colors, type scale, spacing, radii, elevation, component states and status-badge colors all come from [`docs/DESIGN.md`](../DESIGN.md)** — the single source of truth. Do not introduce new tokens in a page implementation.

> ⚠️ `13-ui-ux-flows.md` §4.1–§4.5 used to hold a parallel system (brass/teal/Fraunces). **It is deleted.** If you find a page in this set still citing it for a color or a font, that citation is stale — go to `DESIGN.md`. Doc 13 §4.6–§4.8 (iconography, breakpoints, accessibility) is still live.

Two rules from `DESIGN.md` bite hardest on the customer surface:
- **The `tertiary` family marks AI output and nothing else** — the chatbot, AI-search results, requirement-wizard recommendations, and "similar properties". A focused input, a favorite heart, or a "Just Listed" tag is **not** tertiary. Focus rings are `primary`.
- **One typeface only.** Prices use `headline-md`, not a different face.

### 4.8 Branding — one palette, no theming (MVP)
The public site is **not tenant-branded in the MVP** (decided 2026-07-13, PRD FR16.2). Every tenant's site ships the same `DESIGN.md` tokens. Do not build a theming layer, a `branding` context, or runtime color overrides. Tenant *resolution* (§4.1) still happens — it scopes data, not appearance.

---

## 5. Known Spec Gaps (Blocking or Near-Blocking)

Found while writing this set. **These are documentation gaps, not implementation choices** — resolve them in the owning doc *before* building the affected page (`.claude/rules/workflow.md`).

### ✅ Closed in `03-database-schema.md` v1.1

| # | Gap | Resolution |
|---|---|---|
| G1 | No `notifications` table, yet `GET /portal/notifications` was specified | `notifications` added (§3.20). ⚠️ Email/SMS still have **no provider** — ship the in-app channel only |
| G2 | No notification-preferences storage (FR7.2) | `notification_preferences` added (§3.21) |
| G6 | No delete for a requirement profile (FR7.3) | `requirement_profiles.deleted_at` added (§3.11). **The endpoint is still missing** — see G8 |
| — | **`leads` had no owner** — inquiry history (FR7.1) had no correct implementation, and matching on `customer_email` was a **data-leak vector** | `leads.user_id` + `session_id` added, migrated on registration alongside `favorites` (§3.8) |
| — | `leads` linked to nothing — the lead detail panel couldn't show what the customer wants or what they told the bot | `requirement_profile_id`, `chat_conversation_id` added |
| — | Callback time slot (FR6.2) had nowhere to be stored | `requested_callback_at`, `requested_slot` added |
| — | No idempotency mechanism, despite FR6.4 requiring no duplicate leads | `leads.idempotency_key` + `UNIQUE (tenant_id, idempotency_key)` |
| — | No canonical amenity vocabulary — `gymnasium` silently never matched `gym` | `amenities` lookup table added (§3.18) |
| — | `favorites` had no uniqueness constraint — session→account migration created duplicates | `UNIQUE (tenant_id, property_id, COALESCE(user_id, session_id))` |
| — | `source = property_details` was not a valid enum value | Added to the `leads.source` enum |
| — | One person couldn't be a customer on one tenant and staff on another | `users` is now `UNIQUE (auth_user_id, tenant_id)` |

### ⛔ Still open

| # | Gap | Affects | Owning doc to fix |
|---|---|---|---|
| G3 | **No autosuggest endpoint.** FR2.4 requires as-you-type suggestions; `04-api-spec.md` has no endpoint. Must not be a Bedrock call per keystroke. | `13-feature-ai-search.md` | `04-api-spec.md` |
| G4 | **"Saved Searches" appears in a persona flow** (`13-ui-ux-flows.md` §2.2, Raj) but exists in no PRD module, table, or endpoint. Either it's a `requirement_profile` by another name, or it's unscoped. | `07-portal-dashboard.md`, `09-portal-requirements.md` | `01-prd.md` |
| G5 | **No public endpoint serves CMS pages.** Admin CRUD exists; no public read route, so the public site cannot render About/Terms/blog. The module is inert. | `12-static-cms-pages.md` | `04-api-spec.md` |
| ~~G7~~ | ✅ **CLOSED 2026-07-14.** The agent-reply path now exists: `04-api-spec.md` §12A (queue / claim / reply / close) and `05-ai-chatbot-spec.md` §10A (handoff state machine). The visitor's widget **polls `GET /ai/chat/history` every ~4s while escalated** — see `14-feature-ai-chatbot.md`. | — | — |
| G8 | **Missing endpoints:** delete a requirement profile (the column now exists), mark-notification-read, customer follow-up on an inquiry. | `09`, `10`, `11` | `04-api-spec.md` |
| G9 | **No email/SMS provider chosen**, and **no job scheduler** — so notifications can only be in-app, and nothing fires on a schedule. | `11-portal-notifications.md` | `10-deployment-devops.md`, `02-architecture.md` |

---

## 6. Build Order

Follow `15-development-plan.md`, not this doc's numbering. Roughly: Property Listing + Details + Lead Capture (Phase 1, Sprints 3–4) → AI Search → AI Chatbot → Requirement Wizard (Phase 2, Sprints 5–7) → Customer Portal polish (Phase 3).

The portal pages (07–11) depend on auth (Sprint 1) and on the session-migration contract (`16-feature-favorites-session.md`) being settled first.
