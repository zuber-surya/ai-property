# Architecture Decision Records

> **Owns: why.** Every other doc says *what* the system is. This one says why it is that way, and what we gave up.
>
> **Status:** v1.0 · **Last updated:** 2026-07-14

---

## Why this exists

Sixteen significant decisions were made on this project and recorded nowhere but as a parenthetical — *"(decided 2026-07-13)"* — inside the doc they happened to touch. Anyone joining later sees the *what* and not the *why*, and a decision whose reasoning is invisible is a decision that gets quietly reversed by the next person who finds it inconvenient.

Two of the decisions below (ADR-0006, ADR-0007) exist **because** an earlier decision's rationale was lost. That is not a hypothetical failure mode here.

## Format

Each entry: **Context** (the forcing question) · **Decision** · **Consequences** (including what we gave up) · **Status**.

Entries are **immutable**. To change a decision, add a new ADR that supersedes it and mark the old one `Superseded by ADR-XXXX`. Do not edit history — the reasoning is the artifact.

An ADR that grows past a screen graduates to its own file (`adr/0001-slug.md`); until then it lives here.

---

## ADR-0001 — The docs are the source of truth, not the code

**Context.** This system is built incrementally by agents across many sessions, with no shared memory between them. Whatever is not written down does not exist for the next session.

**Decision.** The `docs/` set is authoritative. If a requirement changes, the doc changes *first*, then the implementation. No endpoint, table, or behavior may exist in code that isn't in a spec.

**Consequences.** Slower to start a change; far cheaper to resume one. The failure mode this trades into — docs drifting from each other — is real, and is why ADR-0016 exists. Accepted.

**Status:** Accepted.

---

## ADR-0002 — Modular monolith, not microservices

**Context.** The product has three AI features and a CRM. The temptation is to split the AI layer out as a service.

**Decision.** One FastAPI application. AI features are internal modules behind clean interfaces (`Router → AI Service → AI Client + Repository`).

**Consequences.** A single deploy artifact and no network hop between the CRM and the AI layer — which matters, because chat/search/recommend are latency-sensitive and already pay a Bedrock round-trip. We give up independent scaling of the AI layer. If Bedrock traffic ever needs to scale separately from CRM traffic, this is the decision to revisit first.

**Status:** Accepted.

---

## ADR-0003 — Tenant isolation is enforced at the database layer via Postgres RLS

**Context.** This is multi-tenant SaaS holding one real-estate business's buyer pipeline next to a competitor's. A cross-tenant leak is not a bug, it is an extinction event. Application-level `WHERE tenant_id = ?` filtering is one forgotten clause away from that.

**Decision.** Postgres Row-Level Security is the **primary** safety net. Every tenant-owned table has `tenant_id NOT NULL REFERENCES tenants(id)` and an RLS policy applied through one reusable migration helper. Application-level filtering is a *second* layer, never the only one. Every tenant-owned table requires an explicit test proving Tenant A cannot read Tenant B's rows — **failing at the DB layer**, not the API layer.

**Consequences.** Every query pays a policy check. Every new table costs a migration and a test. Worth it. The `tenants` table itself is the one exception with no RLS backstop — see `03-database-schema.md` §699, which is why `PUT /admin/tenant/branding` must derive the tenant from the JWT and never from a request parameter.

**Status:** Accepted.

---

## ADR-0004 — Claude via Amazon Bedrock, not the Anthropic API directly

**Context.** The three USP features are all LLM calls. Provider choice determines latency, cost, data residency and the compliance story.

**Decision.** Anthropic Claude models through Amazon Bedrock (`boto3` bedrock-runtime). Embeddings: Amazon Titan Text Embeddings V2, 1024 dims.

**Consequences.** Keeps LLM traffic inside AWS, which simplifies the data-handling story for buyer PII. It also **couples the region choice to Bedrock's model availability**, and that has turned into a live problem — see `GAPS.md` I1: this is an India-first product, and if Claude-on-Bedrock isn't in `ap-south-1`, every AI call crosses regions, which was the exact cost this decision was meant to avoid. **Unresolved.**

**Status:** Accepted, with a live consequence (GAPS.md I1).

---

## ADR-0005 — Supabase for Auth and Storage only; SQLAlchemy talks to Postgres directly

**Context.** Supabase offers a data client. Using it would mean writing data access twice — once through Supabase, once through SQLAlchemy for anything complex.

**Decision.** SQLAlchemy connects to the Supabase Postgres connection string directly. The Supabase client is used **only** for Auth (JWT issuance) and Storage (property images). Never for data access.

**Consequences.** One data-access path, one place migrations apply, one place RLS is reasoned about. We give up Supabase's client-side conveniences and accept that the database is on a different provider from the compute (see `10-deployment-devops.md` §1 — the cross-cloud hop is real and under-examined).

**Status:** Accepted.

---

## ADR-0006 — `DESIGN.md`'s YAML tokens are canonical; its prose is not

**Context.** `DESIGN.md` contradicted *itself*: the YAML said `primary: #3525cd`, the prose forty lines later said "Primary Indigo `#4F46E5`". The prose also named a violet (`#8B5CF6`) for the AI layer that **had no token at all**. Both halves were being read — the prose by humans, the tokens by tooling — and they disagreed on the single most semantically loaded color in the product.

**Decision.** **The token block wins.** Where prose and tokens disagree, the tokens are correct and the prose is a bug. The prose has been rewritten to match. The AI layer is the **`tertiary`** family (`#571ac0`), the only violet that actually exists in the token set.

**Consequences.** One source of visual truth. `scripts/check_drift.py` now fails on any hex written outside `DESIGN.md`. The cost: `11-stitch-design-prompts.md` §17/§18 must inline a *copy* of the tokens (a single-paste Stitch prompt can't reference a file) — a sanctioned fork, watched by the drift check.

**Status:** Accepted.

---

## ADR-0007 — `tertiary` is the AI intelligence layer, and marks nothing else

**Context.** The product's whole claim is that it is AI-first. If the user can't tell what the model produced, the claim is invisible. But an accent color used "for emphasis" degrades into decoration within one sprint.

**Decision.** The `tertiary` family (`#571ac0`) is **semantic, not decorative**. It marks AI-generated output — the chatbot, AI search results and parsed-query chips, requirement-wizard recommendations, match scores, "similar properties", AI-derived lead sources — **and nothing else.** There are no exceptions.

**Consequences.** Focus rings had to move to `primary` (ADR-0008), because a focused form field is a user action, not a model output — and a color that fires on every input in the CRM cannot also mean "the AI did this". The rule is enforced in every Stitch prompt and stated in `DESIGN.md`, `16-customer-spec/README.md` and `17-admin-spec/README.md`. It will be the first thing a designer under deadline tries to break.

**Status:** Accepted.

---

## ADR-0008 — Focus rings use `primary`, not `tertiary`

**Context.** `DESIGN.md` simultaneously declared tertiary "exclusively for AI" and specified a 2px tertiary focus glow on every input. Both could not be true. The contradiction was inherited from the pre-reconciliation prose and survived a full revision unnoticed.

**Decision.** Focus rings are `primary` `#3525cd`. The exclusivity rule in ADR-0007 has **no exceptions**, including focus and hover states.

**Consequences.** The AI signal stays meaningful. Anyone tempted to add a carve-out should read this entry: the carve-out was already written once ("no tertiary anywhere except the input focus glow"), and that sentence was the tell that the rule was broken — not that it needed an exception.

**Status:** Accepted.

---

## ADR-0009 — A semantic status ramp, separate from the brand colors

**Context.** With only `error` defined, the four property statuses had to borrow `primary` and `secondary` — two blues. "Pending Approval" and "Published" ended up **1.35 : 1 apart**: effectively one color, on the two states an agent most needs to distinguish while scanning two hundred listings.

**Decision.** Add `success` / `warning` / `neutral` alongside `error`. **Status is not brand:** `primary`, `secondary` and `tertiary` already carry meaning and may never be conscripted to mean "approved" or "waiting". Status chips use the `*-container` pair (pale fill, dark text) and always carry a text label as well as a color.

**Consequences.** The semantic containers follow the `error` convention (pale + dark text), while the *accent* containers invert Material 3 (saturated + light text). Two conventions in one file — deliberate, documented in `DESIGN.md`, and exactly the kind of thing that bites in six months if nobody wrote it down.

**Known gap:** the ramp has **no "in progress" color**. Three lead stages, two property statuses and three customer-facing inquiry statuses are all in-progress — not done, not failed, not inert, and *not* a warning. See `GAPS.md` D1.

**Status:** Accepted, incomplete.

---

## ADR-0010 — Tenant branding is post-MVP; one fixed palette ships to every tenant

**Context.** `02-architecture.md` and `rules/frontend.md` both asserted the public site was "tenant-branded". `DESIGN.md` was a single hardcoded palette with no theming hook. The two docs disagreed about whether there was one palette or N, and nothing prevented a tenant's brand color from landing on the AI layer.

**Decision.** MVP ships **one fixed palette** to every tenant. No theming layer, no runtime overrides. Per-tenant branding is deferred (PRD FR16.2). **Nothing is deleted** — the `tenants.branding_*` columns, `PUT /admin/tenant/branding` and the custom-domain infrastructure all remain specced, simply unbuilt.

**Consequences.** A large scope cut. Tenant *resolution* still happens from the request domain (it scopes **data**, not appearance), so subdomains are still needed — but **custom** domains are not, which replaces a per-tenant ACM certificate pipeline with one wildcard cert.

**The forward constraint is fixed now, while it's cheap:** when branding lands, a tenant may override `primary` and its derived ramp **and nothing else**. `tertiary` stays platform-owned — the AI signal is PropVista's, not the tenant's, and must read identically on every site.

**Status:** Accepted.

---

## ADR-0011 — The second design system (`13-ui-ux-flows.md` §4) is deleted

**Context.** Two complete design systems coexisted. `13-ui-ux-flows.md` §4 defined `color-brass` `#C17F3C`, `color-teal`, a Fraunces/Inter/IBM-Plex-Mono type stack, a 4px grid, brass focus rings and teal status badges — and **all 33 per-page specs cited it**, not `DESIGN.md`. It was extracted from an early draft of the Stitch prompts and never reconciled when `DESIGN.md` arrived.

**Decision.** §4.1–§4.5 deleted, replaced by a pointer to `DESIGN.md` and a migration table (old → new). §4.6–§4.8 survive: iconography, **numeric breakpoints** (which `DESIGN.md` does not define) and accessibility.

**Consequences.** 11 citations swept across both spec sets. `scripts/check_drift.py` now fails if any dead token reappears. This is the incident that motivated the entire ownership registry.

**Status:** Accepted.

---

## ADR-0012 — The "AI Insights" panel is dropped from Property Details

**Context.** A Stitch prompt for the Property Details page rendered an AI Insights panel — fair-price estimate, appreciation forecast, rental-yield prediction, buy-vs-rent analysis. It appeared in **no PRD module, no AI spec and no schema**. It had arrived via a mockup.

**Decision.** Dropped. Price prediction is a materially different product claim from search, chat and recommendation — the three features the product actually commits to — and it carries real liability if wrong.

**Consequences.** The prompt was rewritten against the actual FR5.1–FR5.5, which it had *also* been failing to implement: floor plan, price breakdown, nearby landmarks, agent contact and the EMI calculator were all missing. If AI Insights is ever wanted it goes into `01-prd.md` Module 5 first, with a specified source for the numbers.

**Status:** Accepted. Logged in `GAPS.md` §4 so it can't quietly return.

---

## ADR-0013 — Lead pipeline stages are a fixed enum for MVP

**Context.** `01-prd.md` FR10.1 promises configurable pipeline stages. The schema fixes the enum.

**Decision.** Fixed enum for MVP: `new` · `contacted` · `site_visit_scheduled` · `negotiation` · `closed_won` · `closed_lost`. Configurable stages are out of scope.

**Consequences.** FR10.1 is **stale and must be corrected** (`GAPS.md` P2). Customer-facing screens must translate these — `negotiation` must never reach a buyer as the word "negotiation", and `closed_lost` is never "Lost".

**Status:** Accepted; owning doc not yet updated.

---

## ADR-0014 — Leads are claimed manually, with a mandatory staleness alert

**Context.** Auto-assignment was undecided. Manual claim means an unclaimed lead is nobody's responsibility.

**Decision.** Manual claim, with an **atomic** claim operation (two agents claiming simultaneously must not both succeed). Because an unclaimed lead is invisible work, FR10.2b makes the stale-lead alert **mandatory, not optional**.

**Consequences.** That mandatory alert is **buildable**: `02-architecture.md` §4.4 provides `pg_cron` + a `jobs` table + a Python worker, and **`mark_stale_leads()` is listed there by name**.

> ⚠️ **An earlier revision of this ADR said the opposite** — *"the alert cannot be built; there is no scheduler"* — and marked this decision `Accepted, blocked` for a day. **That was false.** The claim came from a stale summary in `CLAUDE.md`, not from `02-architecture.md`. It is preserved here rather than quietly deleted, because an ADR that hides its own errors is worth less than one that admits them. See `GAPS.md` §5A.

**Status:** Accepted.

---

## ADR-0015 — Anonymous-first: login is never a gate for value

**Context.** Requiring registration before a buyer can search or chat kills the funnel.

**Decision.** A visitor may browse, search, chat, favorite, run the requirement wizard and submit an inquiry **without an account**, identified by a client-generated `X-Session-Id`. The registration prompt appears *after* a persist-worthy action, never before it. On register/login, session-owned rows (`favorites`, `requirement_profiles`, `chat_conversations`, `leads`) are re-keyed from `session_id` to `user_id`.

**Consequences.** Every customer-facing table needs both a `user_id` and a `session_id` path, plus a migration contract and a uniqueness constraint (absent this, the migration produces duplicate favorites — a bug we shipped into the spec and had to close). Worth it: it's the difference between a funnel and a wall.

**Status:** Accepted.

---

## ADR-0016 — The drift gate fails on regression, not on zero

**Context.** `scripts/check_drift.py` reports 27 real findings on a codebase with no code. A gate that always fails is a gate everyone learns to `--no-verify` past — and then it catches nothing, including the things it was built for.

**Decision.** Known debt is recorded in `.drift-baseline.json` and explained in `GAPS.md`. The pre-commit hook fails **only when a count goes up**. Reducing drift is re-baselined with `--accept`.

**Consequences.** Existing debt is visible and tracked rather than blocking. The risk is that the baseline becomes a dumping ground — so **lowering it is the only sanctioned direction**, and a false positive gets the *check* fixed, never the baseline raised.

**Status:** Accepted.

---

## ADR-0017 — Agent chat replies reach the visitor by polling, not Supabase Realtime

**Context.** Closing gap G7 (the escalated-chat handoff) meant an agent's reply had to reach a visitor's open chat widget. No delivery channel was specified anywhere. Supabase Realtime is the obvious answer — it is **already in the stack**, it costs nothing extra, and it would deliver the message instantly.

**Decision.** **Poll the existing `GET /ai/chat/history/{conversation_id}` every ~4 seconds while `status = 'escalated'`.** No new customer-facing endpoint, no new channel.

**Why not Realtime.** **ADR-0005 restricts the Supabase client to Auth and Storage — never data access.** Chat is data. Using Realtime here would be a third use of the Supabase client and would require superseding ADR-0005, whose whole point is that there is exactly *one* data-access path (SQLAlchemy), so there is exactly one place migrations apply and one place RLS is reasoned about.

The thing being bought with that architectural exception is **three seconds** — and it is being spent against a **human agent who types with 10–30 seconds of natural latency.** Four-second polling is invisible against a person composing a sentence.

**We do not bend a load-bearing architectural rule to save three seconds on a human's typing speed.**

**Consequences.** Slightly more request volume (one poll per 4s per open escalated conversation — a small number, because escalations are rare by design). One data path preserved. If a genuine realtime requirement ever appears — live agent presence, typing indicators, read receipts — **that** is the moment to revisit ADR-0005 deliberately, with a real requirement behind it, rather than smuggling the exception in through a chat feature.

**Status:** Accepted.

---

## ADR-0018 — `info` is a cyan, and the three in-progress lead stages share it

**Context.** The semantic ramp (ADR-0009) shipped with `success` / `warning` / `error` / `neutral` and **no colour for "in progress"**. Three lead stages (`contacted`, `site_visit_scheduled`, `negotiation`), two property statuses (`on_hold`) and three customer inquiry statuses are all *started but not finished* — not done, not failed, not inert, and emphatically **not a warning**. They rendered `neutral`, which meant an agent could not distinguish *"nobody has touched this"* from *"a site visit is booked"* (gap **D1**).

**Decision.** Add an **`info`** family: `#00668b` / container `#bfe9ff`. **All three in-progress lead stages share it.**

**Why a cyan, when the palette already has indigo, blue and violet.** The constraint that actually applies is narrower than it looks:

> **A status chip only ever appears next to other status chips.**

`info` therefore has to be distinguishable from `success`, `warning`, `error` and `neutral` — **not** from the brand colours, which never render as status ("status is not brand", ADR-0009). That frees the cyan band. Pale cyan against pale mint and pale amber is unambiguous at chip size; against indigo it never has to compete, because they never appear together.

**Why one colour for three stages, not three.** They do not need three. The **text label** distinguishes them — status always carries one — and on the Kanban the *column* already encodes the stage positionally. Three near-identical blues would recreate the exact failure ADR-0009 was written to fix (Pending vs. Published at 1.35 : 1).

**Consequences.** The ramp is now five hues, which is the practical ceiling for at-a-glance discrimination. ⚠️ **The Kanban, leads-table and lead-detail Stitch screens were generated before `info` existed and render those stages `neutral` — they must be regenerated.** That is the cost of designing screens against a design system that wasn't finished.

**Status:** Accepted.

---

## Decisions still open

These are not ADRs yet because nobody has decided. They live in `GAPS.md`:

| | Question | Blocks |
|---|---|---|
| **I1** | Which AWS region — and does Bedrock's Claude availability survive an India-first product? | All provisioning |
| **DLT** | Indian SMS requires DLT registration of entity, sender IDs and templates. Twilio is chosen (`02-architecture.md` §3) — but the registration is a *regulatory* lead time, not an engineering one. **Start it now.** | Notifications, both surfaces |
| **D1** | The missing `info` status color | Kanban, leads table, portal inquiries |
| **G4** | Is "Saved Searches" a real feature or an unscoped persona artifact? | Portal dashboard |
