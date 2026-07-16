# Gap Register — The Single Source of Truth for What's Blocked

> **Part of the PropVista DevOS.** See [`OWNERSHIP.md`](OWNERSHIP.md) and [`.claude/rules/devos.md`](../.claude/rules/devos.md).
>
> **Status:** v1.0 · **Last updated:** 2026-07-14

---

## 1. Rules for this file

1. **This is the only place a gap's state is recorded.** No other file may say "this is blocked" without citing a gap ID from here.
2. **Closing a gap here is not enough.** You must sweep every file that cites it — see `OWNERSHIP.md` §4. This already went wrong once: schema v1.1 closed G1, G2, the `favorites` uniqueness constraint and `leads.user_id`, and three portal specs *still* list them as blocking.
3. **A gap is closed only when the owning doc says so** — not when someone decides it's fine in code. `CLAUDE.md`: *fix the owning doc first, then implement — do not work around a gap in code.*
4. Every gap has an **owner** (the doc that must change) and a **blast radius** (what can't be built until it closes).

---

## 2. Open — blocking

These stop work. Ranked by how much they hold up.

| ID | Gap | Owning doc | Blocks |
|---|---|---|---|
| **G5** | **No public CMS read endpoint.** Admin CRUD exists; nothing serves a page to a visitor. The whole CMS module is inert — the public site cannot render About/Terms/blog. | `04-api-spec.md` | `16-customer-spec/12-static-cms-pages.md` · doc 11 §11 |

---

## 3. Open — needs a decision (not blocking yet)

| ID | Gap | Owning doc | Notes |
|---|---|---|---|
| **G3** | **No autosuggest endpoint.** FR2.4 requires as-you-type suggestions. Must not be a Bedrock call per keystroke. | `04-api-spec.md` | Blocks AI-search polish (Phase 2) |
| **G4** | **"Saved Searches"** appears in Raj's persona flow (`13-ui-ux-flows.md` §2.2) but exists in **no module, table, or endpoint.** Either it's a `requirement_profile` by another name, or it's unscoped scope. | `01-prd.md` | Decide: scope it, or delete it from the persona flow |
| **G8** | **Missing endpoints:** delete a requirement profile (the `deleted_at` column now exists — G6), mark-notification-read, customer follow-up on an inquiry. | `04-api-spec.md` | Portal screens 09/10/11 ship degraded without them |
| **P1** | **Lead auto-assignment is undecided.** Manual claim is specced, with FR10.2b as its safety net — and that safety net **is buildable** (`02-architecture.md` §4.4). | `01-prd.md` | — |
| **P2** | **`01-prd.md` FR10.1 is stale** — still promises configurable pipeline stages; the schema fixes the enum for MVP. | `01-prd.md` | Correct the PRD |
| **P3** | **`04-api-spec.md` §14 is stale** — implies a persisted report with an ID; reports are stateless. | `04-api-spec.md` | Correct the API spec |
| **I1** | **Bedrock region vs. users vs. Supabase.** `10-deployment-devops.md` §1's whole rationale is "co-locate compute with Bedrock." This is an India-first product. If Claude-on-Bedrock isn't in `ap-south-1`, you must choose: co-locate with Bedrock (slow for users + DB) or with users (every AI call crosses regions). **This decides the region, which decides everything else.** Not yet confronted. | `10-deployment-devops.md` | Blocks provisioning |
| **I2** | **Font hosting for Plus Jakarta Sans** — self-hosted vs. Google Fonts. Undecided. | `13-ui-ux-flows.md` §5 | Blocks frontend Sprint 0 |
| **S1** | **SVG logo uploads** (`tenants.branding_logo_url`) — an SVG is executable content and can carry a `<script>`. Sanitize, or restrict to PNG/JPG. A one-line decision, not yet made. | `03-database-schema.md` | Post-MVP with branding, but decide now |
| **S2** | **Session ID: `localStorage` + header vs. HttpOnly cookie.** A cookie is harder to steal via XSS; the API spec commits to `X-Session-Id`. Not urgent — a session ID is not a credential — but worth a deliberate call. | `04-api-spec.md` | — |
| **X1** | **Rate-limit thresholds** for `ai/*` endpoints. Deferred to real pilot data — but *some* limit must ship, or Bedrock cost is unbounded. | `04-api-spec.md` §17 | Ship a conservative default |
| **X2** | **Dark mode** is in scope for nothing, assumed nowhere, and `DESIGN.md` has no dark palette. Confirm it's out. | `13-ui-ux-flows.md` §5 | — |

---

## 4. Scope creep caught — not approved, not built

Things that appeared in a spec or a mockup without ever entering the PRD. Listed so they don't quietly become commitments.

| Item | Where it surfaced | State |
|---|---|---|
| **AI Insights panel** (fair-price estimate, appreciation forecast, rental yield, buy-vs-rent) on Property Details | doc 11 §4 | ❌ **Dropped 2026-07-13.** Price prediction is a materially different product claim from the three USP AI features. Not in any spec. If wanted: add to `01-prd.md` Module 5 first, with a source for the numbers. |
| **Compare view** (side-by-side spec table of 2–3 favorites) | `08-portal-favorites.md` §11 | ⏸ Unscoped. Natural next step for that page and a genuine differentiator — but in no PRD module. |
| **Notification types** beyond `new_match` — `inquiry_update`, `price_change`, `property_unavailable` | `11-portal-notifications.md` §3.1 | ⏸ Only `new_match` is an actual requirement (FR3.4). The rest are proposals. |
| **`/portal/requirements/{id}/matches`** route | `stitch-prompts.md` | ❌ Invented. "Not a separate spec but implied" is not a specification. |

---

## 5. Closed

Kept, not deleted — because **three portal specs still cite these as blocking**, and that's exactly the drift this register exists to kill.

| ID | Gap | Closed by | ⚠️ Sweep still needed |
|---|---|---|---|
| **G1** | No `notifications` table | `03-database-schema.md` v1.1 §3.20 | **YES** — `07-portal-dashboard.md` §6/§7/§11 still calls it open |
| **G2** | No notification-preferences storage | `03-database-schema.md` v1.1 §3.21 | **YES** — `09-portal-requirements.md` still calls it open |
| **G6** | No delete for a requirement profile | `deleted_at` added (§3.11) | Partial — the **column** exists, the **endpoint** does not (→ G8) |
| — | `leads` had no owner (`user_id`) — inquiry history was unbuildable and email-matching was a data-leak vector | v1.1 §3.8 | **YES** — `07-portal-dashboard.md` §8 still calls it "a blocking schema gap" |
| — | `favorites` had no uniqueness constraint — session→account migration created duplicates | v1.1 | **YES** — `08-portal-favorites.md` §11 still calls it open |
| — | No idempotency mechanism despite FR6.4 | `leads.idempotency_key` | — |
| — | No canonical amenity vocabulary (`gymnasium` ≠ `gym`) | `amenities` lookup table §3.18 | — |
| — | `source = property_details` not a valid enum value | Added to `leads.source` | — |
| — | One person couldn't be a customer on one tenant and staff on another | `users` UNIQUE (auth_user_id, tenant_id) | — |
| **DS1** | **Two competing design systems** — `13-ui-ux-flows.md` §4 (brass/teal/Fraunces) vs `DESIGN.md` (indigo/violet); 33 specs cited the dead one | Doc 13 §4.1–4.5 deleted 2026-07-13; 11 citations swept | Done |
| **DS2** | Tenant branding assumed by `02-architecture.md` and `rules/frontend.md`; no theming layer existed | Deferred to post-MVP 2026-07-13; 4 docs amended | Done |
| **G7** | **No agent-reply path for an escalated chat.** `POST /ai/chat/escalate` existed; nothing let the human reply. FR1.7 promised a handoff the system could not perform | **Closed 2026-07-14.** `04-api-spec.md` §12A (4 endpoints: queue / claim / reply / close, + the bot-goes-silent rule) · `05-ai-chatbot-spec.md` §10A (handoff state machine) · `17-admin-spec/22-agent-chat-console.md` (the screen) · ADR-0017 (polling over Realtime). **No migration — the schema already had `sender = 'agent'` and `assigned_agent_id`** | Done — `16-feature-ai-chatbot.md` §222 swept |

| **D1** | **No "in progress" status color.** Three lead stages, two property statuses and three customer inquiry statuses were all *in progress* — not done, not failed, not inert, not a warning — and rendered `neutral`, a placeholder | **Closed 2026-07-14.** `info` family added to `DESIGN.md` (`#00668b` / `#bfe9ff`). A cyan works because **a status chip only ever appears next to other status chips** — it never has to compete with the brand blues | ⚠️ **Stitch screens for Kanban / leads table / lead detail were generated pre-`info` and must be regenerated** |

---

## 5A. ⛔ FALSE GAPS — G9a and G9b never existed

**This is the most important entry in this file. Read it before you trust any gap.**

| ID | The claim | The truth |
|---|---|---|
| ~~**G9a**~~ | *"No job scheduler. `BackgroundTasks` cannot fire on a timer, so FR10.2b (mandatory) is unbuildable."* | **False.** `02-architecture.md` **§4.4** has specified **`pg_cron` + a `jobs` table + a Python worker since 2026-07-13** — and **`mark_stale_leads()` is explicitly listed in it.** FR10.2b was buildable the entire time. |
| ~~**G9b**~~ | *"No email/SMS provider chosen."* | **False.** `02-architecture.md` **§3** names **Email = SendGrid, SMS = Twilio** — decided 2026-07-13, with the Indian DLT registration requirement already noted. |

### How this happened, in three levels

```
02-architecture.md §4.4      DECIDED pg_cron + jobs worker (2026-07-13)
        │                    …but its own §9 open-questions list still said
        │                    "[ ] BackgroundTasks or Celery?" — contradicting itself
        ▼
CLAUDE.md line 33            SUMMARISED it as "no job scheduler"        ← level 1
        ▼
16-customer-spec/README §5   COPIED that summary into a gap table       ← level 2
        ▼
an agent (me)                READ THE SUMMARY, NOT THE OWNING DOC       ← level 3
        ▼
GAPS.md · BACKLOG.md · 22-risk-register.md · 20-operations-runbook.md ·
adr/README.md (ADR-0014) · 05-ai-chatbot-spec.md · 17-admin-spec/22 · doc 11
        ▼
        "A mandatory PRD requirement is unbuildable."   ← confidently, eight times
```

**Nobody lied. Every step was a faithful copy of the step above it.** That is what makes summary-drift so dangerous: it does not look like an error, it looks like agreement.

### What it cost

An entire sprint (`Sprint 4`) was planned as blocked. A "known residual" was written into the G7 closure. A risk-register entry, an ADR consequence, an operations-runbook limitation, and a Stitch prompt warning were all authored around a constraint **that did not exist**.

### The rules this produced

1. **`GAPS.md` is the only place a gap's state is recorded.** Cite the ID; never restate the list. (`OWNERSHIP.md` §3.)
2. **An answered open-question is a lie with a checkbox.** `02-architecture.md` §9 still listed the scheduler as open a day after §4.4 decided it. When you decide something, **close its open-question line in the same commit.**
3. **`scripts/check_drift.py` now has a `false-gap` check** that fails on any resurrection of "no scheduler" or "no email/SMS provider".
4. This is the same failure as `OWNERSHIP.md` §5 #4 (a doc paraphrased the PRD, the paraphrase drifted, a false bug was reported). **It happened twice. The second time it cost a sprint plan.**

---

## 5B. Closed

---

## 6. Untracked files needing a decision

| File | Problem |
|---|---|
| `docs/stitch-prompts.md` | A **third** document competing with `11-stitch-design-prompts.md`. Per `OWNERSHIP.md` §6 it owns no concept, and `devos.md` §7 names it as *the* example of a file that shouldn't exist. **That argument stands. The one below it did not.** **Decide: rename and re-scope it, fold it into doc 16, or delete it.**<br><br>⚠️ **Corrected 2026-07-16.** This row used to read *"it contains **no design system at all**: no colors, no type, no tokens. Anyone following it produces off-brand screens."* **That was false**, and it was very nearly the stated reason for deleting the file. In fact it carries **51 hex values, every one of them a live `DESIGN.md` value**; it is listed in `check_drift.py`'s `GENERATED_PROMPT_DOCS` and **is** watched by the `generated-prompts-stale` check, which reports **0**. Decide its fate on the ownership argument — not on a design-system claim the checker disproves. |
| ~~`SPRINT0_PLAN.md`~~ | **Closed 2026-07-16 — the file is gone** (task `P.4`). It specified `psycopg2-binary` (synchronous) against a `CLAUDE.md` rule that every I/O endpoint is `async`, and listed `@vitejs/plugin-tsx`, which is not a real package. Its content was absorbed into `BACKLOG.md` §4 with both bugs fixed; `async-violation` is now **0**. |
