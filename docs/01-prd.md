# Product Requirements Document (PRD) — PropVista CRM

> **Doc 01 of the PropVista CRM documentation set.** Written for engineering use — pairs with `00-project-overview.md`. Each module below states purpose, functional requirements, and acceptance criteria so it can be picked up directly as build scope.
>
> **Status:** Draft v1.0 · **Last updated:** July 2026

---

## 1. Module Map

| # | Module | Surface |
|---|---|---|
| 1 | AI Chatbot | Public Site |
| 2 | AI Search | Public Site |
| 3 | AI Recommendation (Requirement Analysis) | Public Site |
| 4 | Property Listing (Browse/Search Results) | Public Site |
| 5 | Property Details | Public Site |
| 6 | Contact / Lead Capture | Public Site |
| 7 | Customer Portal | Public Site (auth) |
| 8 | Admin Dashboard & Analytics | Admin Portal |
| 9 | Property Management | Admin Portal |
| 10 | Lead & CRM Pipeline | Admin Portal |
| 11 | User & Role Management | Admin Portal |
| 12 | Agent/Broker Management | Admin Portal |
| 13 | AI Configuration (Chatbot/Search/Recommendation) | Admin Portal |
| 14 | Content & Website Management (CMS) | Admin Portal |
| 15 | Reports & Notifications | Admin Portal |
| 16 | Tenant & Branding Settings | Admin Portal (super admin) |

---

## 2. Module 1 — AI Chatbot

**Purpose:** Always-available conversational assistant that answers questions, qualifies visitors, and captures leads.

**Functional Requirements:**
- FR1.1 Chat widget available on every public page; persists across page navigation within a session.
- FR1.2 Bot answers FAQs (pricing process, availability, general info) using tenant-specific configured content.
- FR1.3 Bot can look up live property data (price, availability, specs) via backend tool calls, not hallucinated answers.
- FR1.4 Bot can capture visitor contact info mid-conversation and create a lead record.
- FR1.5 Bot can offer to schedule a site visit or callback, writing the result to the CRM.
- FR1.6 Bot supports conversation history within a session (and across sessions for logged-in users).
- FR1.7 Bot escalates to human agent handoff when it cannot resolve a query, or on explicit user request.
- FR1.8 All conversations are logged for admin review (`13-AI Configuration`).

**Acceptance Criteria:**
- A visitor can ask about a specific listed property and receive accurate current data (not stale/hallucinated).
- A visitor can complete a full conversation that ends in a created lead with correct contact info and source = "chatbot".
- Escalation requests are visible to an agent within the CRM in real time or near-real time.

**Dependencies:** Property data API (Module 9), Lead API (Module 10), Bedrock/Claude integration (`05-ai-chatbot-spec.md`).

---

## 3. Module 2 — AI Search

**Purpose:** Natural-language property search replacing/augmenting manual filters.

**Functional Requirements:**
- FR2.1 Single search bar accepts free-text queries (e.g. "3BHK under 80 lakhs near tech park").
- FR2.2 Query is parsed into structured constraints (property type, budget, bedrooms, location, amenities) plus a semantic/vector component for fuzzy intent.
- FR2.3 Results are ranked by combined relevance (structured filter match + semantic similarity). **The match score is displayed to customers as a raw percentage** (*decided 2026-07-13*).
- FR2.4 Auto-suggestions appear as the visitor types.
- FR2.5 Voice input is supported (speech-to-text feeding the same query pipeline).
- FR2.6 Search respects tenant scope — only that tenant's listings are searchable from their site.
- FR2.7 Fallback to standard filter-based search if AI parsing fails or times out.

**Acceptance Criteria:**
- A representative set of natural-language test queries returns property results a human reviewer judges as relevant (target: defined in `06-ai-search-spec.md`).
- Search responds within an acceptable latency budget (defined in `06-ai-search-spec.md`) even under the AI parsing step.
- No cross-tenant data appears in results.

**Dependencies:** Property data + embeddings (Module 9, `03-database-schema.md`), Bedrock model + embedding model (`06-ai-search-spec.md`).

---

## 4. Module 3 — AI Recommendation (Requirement Analysis)

**Purpose:** Guided questionnaire that captures buyer/renter needs and returns a ranked, matched shortlist.

**Functional Requirements:**
- FR3.1 Multi-step guided form captures: budget range, location preference(s), property type, purpose (self-use/investment), timeline, must-have amenities. Skipping a step means **no constraint on that criterion** — not a zero — and the remaining weights are renormalized.
- FR3.2 On submission, the system generates a ranked shortlist of matching properties with a visible match reason and score. **The score is shown to customers as a raw percentage** ("92% match") — *decided 2026-07-13* — alongside the plain-language ✓/✗ reason lines.
- FR3.3 Registered users can save their requirement profile and revisit/edit/**delete** it.
- FR3.4 Saved profiles trigger notifications when new matching properties are added (ties to Module 7). **Batched per recipient** — a bulk import of 200 matching properties must produce one notification, not 200.
- FR3.5 Matching logic is configurable per tenant (weighting of criteria) — see Module 13.
- FR3.6 **Amenities come from one canonical, platform-wide vocabulary** (`amenities` table). The wizard, the search filters, and the property form all draw from it. Free-text amenities are not permitted — a listing tagged `gymnasium` must not silently fail to match a buyer asking for `gym`.

**Acceptance Criteria:**
- Submitting the form always returns at least a ranked list (even if sparse) or a clear "no matches, here's the closest" fallback — never an empty/broken state.
- Match reasoning is explainable in plain language (e.g. "Matches your budget and location; missing 1 amenity").

**Dependencies:** Property data (Module 9), scoring/matching engine (`07-ai-recommendation-spec.md`).

---

## 5. Module 4 — Property Listing (Browse/Search Results)

**Functional Requirements:**
- FR4.1 Grid and list view toggle; map view toggle showing pinned results.
- FR4.2 Filters: price range, property type, bedrooms, location, amenities; combinable with AI search.
- FR4.3 Sort by: relevance, price (asc/desc), date added, area.
- FR4.4 Favorite/save a property without requiring login (session-based), with a prompt to register to persist favorites.
- FR4.5 Pagination or infinite scroll.

**Acceptance Criteria:** Filters and AI search can be combined in a single query without conflicting; favoriting works pre-login and migrates to the account on registration/login.

---

## 6. Module 5 — Property Details

**Functional Requirements:**
- FR5.1 Full image gallery, floor plan, amenities list, price breakdown, location map, nearby landmarks.
- FR5.2 "Similar properties" recommendations (reuses recommendation engine, Module 3).
- FR5.3 Sticky CTA for "Request Callback" / "Schedule Visit" visible while scrolling.
- FR5.4 Agent/builder contact info displayed.
- FR5.5 EMI/affordability calculator widget.

**Acceptance Criteria:** Page functions correctly with partial data (e.g. missing floor plan doesn't break layout); CTA always visible without obstructing content on mobile.

---

## 7. Module 6 — Contact / Lead Capture

**Functional Requirements:**
- FR6.1 Contact form (name, phone, email, message) available as modal and inline on key pages.
- FR6.2 Callback request with time-slot picker.
- FR6.3 Confirmation shown on submit (toast/screen); optional SMS/email confirmation.
- FR6.4 Every submission creates a lead record tagged with source page and channel.

**Acceptance Criteria:** No duplicate lead records created for a single submission (idempotency); lead always has a traceable source.

---

## 8. Module 7 — Customer Portal

**Functional Requirements:**
- FR7.1 Dashboard showing saved properties, requirement profile, inquiry history, notifications.
- FR7.2 Notification preferences (email/SMS/in-app) for new matches.
- FR7.3 Ability to edit/delete saved requirement profile.

**Acceptance Criteria:** Data shown is scoped strictly to the logged-in user and their tenant.

---

## 9. Module 8 — Admin Dashboard & Analytics

**Functional Requirements:**
- FR8.1 KPI cards: total listings, active leads, conversion rate, **sessions**.
  - *Decided 2026-07-13:* "site visitors" is measured by a **self-hosted session counter** (`site_sessions`), not third-party analytics — no vendor, no cookie-consent banner. It counts **sessions, not people**, and the card must be labelled "Sessions" accordingly. A KPI that overstates by an unknown factor is worse than no KPI.
- FR8.2 Charts: lead source breakdown, property views over time (backed by `property_views`).
- FR8.3 Recent activity feed (new leads, listing changes, chatbot escalations).
- FR8.4 **Unclaimed lead count** — surfaced prominently. Under manual claim (FR10.2), this is the number that tells an owner whether leads are being lost.

**Acceptance Criteria:** All metrics scoped to the logged-in tenant only; numbers reconcile with underlying CRM/lead data **and with the Reports module for the same date range**.

> **Metric definitions are normative and live in `03-database-schema.md` §6.** *Decided 2026-07-13:* **conversion rate = closed_won ÷ (closed_won + closed_lost), over leads that reached a terminal stage within the period.** One `metrics_service` computes it for the Dashboard, the Agents leaderboard, and Reports. Three screens computing "conversion" three ways is the fastest way to make a CRM's numbers untrusted — and once untrusted, nobody looks at them again. All metrics are computed in the tenant's timezone.

---

## 10. Module 9 — Property Management

**Functional Requirements:**
- FR9.1 CRUD for listings with media (photos, video, floor plans, documents).
- FR9.2 Bulk upload via CSV/Excel with validation and error reporting.
- FR9.3 Approval workflow: Draft → Pending Approval → Published (configurable per tenant whether approval is required).
- FR9.4 Status flags: Featured, Sold, On Hold, Archived.
- FR9.5 On save, listing content is embedded/indexed for AI Search (Module 2) automatically.

**Acceptance Criteria:** A newly published property becomes searchable (AI Search) and matchable (Recommendation engine) within a defined sync window (target in `06-ai-search-spec.md`).

---

## 11. Module 10 — Lead & CRM Pipeline

**Functional Requirements:**
- FR10.1 Kanban pipeline: New → Contacted → Site Visit Scheduled → Negotiation → Closed Won / Closed Lost. **Stages are a fixed set** — *decided 2026-07-13; configurable stage names are explicitly out of scope for MVP* (see `03-database-schema.md` §10.1).
- FR10.2 **Leads are manually claimed from a shared queue.** *Decided 2026-07-13: no auto-assignment (not round-robin, not rules-based).* A new lead is created unassigned and appears in a **shared "New" column visible to every agent in the tenant**; an agent claims it by dragging it out of New. Admins may reassign any lead at any time.
  - FR10.2a The claim must be atomic — two agents claiming simultaneously must not both succeed (`03-database-schema.md` §3.8.1).
  - FR10.2b Because an unclaimed lead is nobody's responsibility, a **stale-lead notification rule is mandatory, not optional** (FR15.2): leads sitting unclaimed past a threshold must alert someone. Without it, manual claim loses leads.
- FR10.3 Notes, call logs, and follow-up reminders per lead.
- FR10.4 Lead source tracking (chatbot, AI search inquiry, requirement form, contact form, property details page, walk-in — manually added).
- FR10.5 Table view as an alternative to Kanban. Sortable by **unclaimed age** — the query that surfaces a rotting queue.

**Acceptance Criteria:** Every lead has a non-null source; every lead is either claimed by an agent or visibly sitting in the shared unclaimed queue (never invisible); claims and stage changes are timestamped for reporting; a simultaneous double-claim results in exactly one owner.

---

## 12. Module 11 — User & Role Management

**Functional Requirements:**
- FR11.1 **Four fixed roles: `customer`, `agent`, `admin`, `super_admin`.** *Decided 2026-07-13: granular per-feature sub-roles (Marketing, Support) are deferred past MVP* — a second permission system checked alongside the first is a permission model with holes. The `roles_permissions` table exists but stays unused (`03-database-schema.md` §3.3).
- FR11.2 Invite flow for new admin-portal users. **No self-registration for admin-portal roles**, and a tenant admin can never create a `super_admin`.
- FR11.3 Audit log of admin actions (actor, action, entity, timestamp) — including **denied** actions. Append-only; retained 7 years.
- FR11.4 A person may hold accounts in more than one tenant (e.g. a buyer on one brokerage's site, an agent at another) — one identity, one user record **per tenant**.

**Acceptance Criteria:** A user with a restricted role cannot access or call APIs for features outside their permission set (enforced server-side, not just hidden in UI); a role change takes effect immediately without re-login; a tenant admin cannot escalate anyone to `super_admin`.

> **Accepted risk (2026-07-13): no 2FA at MVP.** The admin portal is password-only for every role, including `super_admin`. One phished admin password exposes that tenant's full customer database. Supabase Auth supports MFA when this is revisited.

---

## 13. Module 12 — Agent/Broker Management

**Functional Requirements:**
- FR12.1 Agent profile: contact info, assigned listings, assigned leads.
- FR12.2 Performance view: leads closed, response time, conversion rate.
- FR12.3 Leaderboard view across agents within a tenant.

**Acceptance Criteria:** Performance metrics recompute correctly as leads change stage/owner.

---

## 14. Module 13 — AI Configuration

**Functional Requirements:**
- FR13.1 Chatbot config: greeting script, FAQ library, escalation rules — per tenant.
- FR13.2 Conversation log viewer with flagging for review.
- FR13.3 Requirement-analysis weighting config (e.g. budget vs. location importance) — per tenant.
- FR13.4 Basic visibility into AI Search performance (e.g. queries with no/low results, for tenant awareness).

**Acceptance Criteria:** Config changes take effect for new conversations/searches without a deployment; changes are tenant-scoped only.

---

## 15. Module 14 — Content & Website Management (CMS)

**Functional Requirements:**
- FR14.1 Edit homepage banners, blog posts, static pages (About, Careers, Terms).
- FR14.2 SEO metadata fields (title, meta description, slug) per page/listing.

**Acceptance Criteria:** Non-technical admin can publish a content change without developer involvement.

---

## 16. Module 15 — Reports & Notifications

**Functional Requirements:**
- FR15.1 Report builder: leads, sales, inventory reports with filters and export (PDF/Excel). **Reports are generated synchronously and row-capped** — *decided 2026-07-13*. There is no saved-report entity; export re-runs the query with the same parameters. If a date range exceeds the cap, the user is told to narrow it rather than being silently given a truncated result.
  - FR15.1a A "sales" report reports **`leads.deal_value`** (set on `closed_won`), not the property's asking price.
- FR15.2 Configurable notification rules (event → channel → recipients).
  - **Channels (decided 2026-07-13): in-app, email (SendGrid), SMS (Twilio).** All three ship at MVP.
  - **SMS is opt-in and capped per tenant** — it costs money per send, and a misconfigured rule on a busy tenant is a bill nobody approved. Indian SMS additionally requires **DLT registration** (sender ID + pre-approved templates), which has real lead time.
  - Events: `new_lead`, `lead_escalated`, **`lead_stale`** (mandatory under FR10.2b), `lead_assigned`, `follow_up_due`, `property_pending_approval`, `listing_expiring`.
  - **A notification dispatch failure must never fail the action that triggered it.** A SendGrid outage cannot block lead creation — dispatch runs in the jobs worker, outside the request.

**Acceptance Criteria:** Exported reports match dashboard figures for the same filter/date range (both call the same `metrics_service`); a bulk import of 200 properties produces **batched** notifications, not 200 per recipient; a provider outage does not prevent lead capture.

---

## 17. Module 16 — Tenant & Branding Settings

**Functional Requirements:**
- FR16.1 Super admin: create/manage tenant accounts, view tenant status/usage.
  - **Tenant status behavior (decided 2026-07-13):**

    | Status | Public site | Admin login | AI endpoints |
    |---|---|---|---|
    | `active` | ✅ | ✅ | ✅ |
    | `trial` | ✅ | ✅ | ✅ (a label, not a behavior — billing is out of scope) |
    | `suspended` | **✅ still serving** | **⛔ blocked** | ✅ still enabled |

    > **Accepted trade-off:** a suspended tenant's buyers see no outage — so we keep serving, and keep paying Bedrock for, a tenant who isn't paying us. Their staff meanwhile cannot log in to work the leads their live site keeps generating. Reactivate promptly.
  - FR16.1a Creating a tenant must also provision, in one transaction: a default `ai_config`, default `notification_rules`, starter CMS page drafts, and the first admin invite. A tenant without these is a workspace that appears to exist and doesn't work.
- FR16.2 Tenant admin: configure branding (logo, colors, custom domain) with live preview. A custom domain must be **DNS-verified before it is routed** — an unverified domain is a hijacking vector.
  - 🕓 **POST-MVP (decided 2026-07-13).** MVP ships a **single fixed palette** for every tenant — the design system in `docs/DESIGN.md`. There is no theming layer, and the public site is **not** tenant-branded at launch.
  - Nothing is removed to support this: the `tenants.branding_logo_url` / `branding_primary_color` / `branding_accent_color` columns (`03-database-schema.md` §2), `PUT /admin/tenant/branding` (`04-api-spec.md` §15), and the custom-domain infrastructure (`10-deployment-devops.md` §8) all stay specced. They are simply not built in the MVP sprints.
  - **Constraint for when this does land:** a tenant may override `primary` and its derived ramp only. The `tertiary` family is PropVista's AI-intelligence signal and stays **platform-owned** — it must read identically across every tenant, so a tenant's brand color must never be able to land on it. See `docs/DESIGN.md` → Colors.

**Acceptance Criteria (post-MVP):** Branding changes apply immediately to that tenant's public site only; no leakage to other tenants; two tenants cannot claim the same domain; a tenant's brand color cannot be applied to the `tertiary` AI layer.

---

## 18. Cross-Cutting Requirements

- **Tenant isolation:** every data query is scoped by tenant ID **at the database layer via RLS**, with API-layer filtering as a second line — not the only one.
- **Mobile responsiveness:** all public-site and customer-portal screens must be usable on mobile viewports. The admin portal is desktop-first; the Kanban board in particular is not a phone experience and falls back to the table view.
- **Latency budgets for AI features:** defined per feature in the respective AI spec docs, since chat/search/recommendation all involve live model calls.
- **Auditability:** admin actions and lead-stage changes are logged with timestamps for reporting and accountability (FR11.3).
- **Background work** runs as **pg_cron** (SQL-only scheduled jobs) plus a **Python worker polling a `jobs` table** (embeddings, bulk import, notification dispatch) — *decided 2026-07-13*. See `02-architecture.md` §4.4.
  - ⚠️ A failed embedding job is **invisible in the product**: the property is live and simply never appears in AI search. No error, no broken page. Failed jobs must alert, and un-indexed published properties must be surfaced to admins.
- **One metrics service.** Conversion rate, active leads, and response time are defined once (`03-database-schema.md` §6) and computed in one place for the Dashboard, Agents, and Reports.

---

## 18a. Decision Log (2026-07-13)

The decisions that closed the blocking gaps found while writing `16-customer-spec/` and `17-admin-spec/`. **These are settled — implement them, don't re-litigate them.** Full detail and rationale in `03-database-schema.md` §10.

| Decision | Where it lands |
|---|---|
| Fixed pipeline stages (no configurability) | FR10.1 |
| Manual lead claim from a shared queue (no auto-assignment) | FR10.2 |
| Four fixed roles; sub-roles deferred | FR11.1 |
| One user record per tenant (a person can exist in two) | FR11.4 |
| Synchronous, row-capped reports | FR15.1 |
| pg_cron + a Python jobs worker | §18 |
| In-app + SendGrid email + Twilio SMS | FR15.2 |
| Suspension: public site up, admin blocked | FR16.1 |
| Self-hosted session counter, not analytics | FR8.1 |
| Conversion = won ÷ closed-in-period | FR8.1 |
| Match score shown as a raw percentage | FR2.3, FR3.2 |
| Agent scope: colleagues' leads read-only, may draft properties, sees leaderboard, reads own leads' transcripts | Module 11 / `08-auth-roles-spec.md` |
| Retention: rollups at 90d, chats 24mo, audit 7yr | `03-database-schema.md` §8 |

**Accepted risks** (chosen knowingly — see `03-database-schema.md` §10.2): a single **public** Storage bucket for all media including documents; **no 2FA** on the admin portal; manual claim can leave leads **ownerless** unless the stale-lead rule is configured.

---

## 19. Out of Scope (Reaffirmed from Project Overview)

- Payment/subscription billing.
- Third-party listing portal syndication.
- Native mobile apps.
- Advanced BI/data-warehouse reporting.

---

## 20. Traceability to Business Plan

This PRD maps directly to Sections 5 and 6 of the original business plan (`Feature Specification — Public Site & Customer Portal` and `Feature Specification — Admin Portal`), rewritten here as testable functional requirements for engineering handoff.

---

**Next document:** `02-architecture.md` — system architecture, multi-tenancy strategy, and folder structure for the FastAPI + React + Supabase stack.
