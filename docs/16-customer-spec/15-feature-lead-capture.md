# Feature: Lead Capture

> **Appears on:** [Property Details](03-property-details.md) (modal), [Contact](05-contact-page.md) (inline), [Chatbot](14-feature-ai-chatbot.md) (conversational), [Favorites](08-portal-favorites.md) ("Ask about this") · **PRD Module:** 6 · **Component:** `public-site/src/components/shared/LeadForm/`
> Part of [Doc 16 — Customer Spec](README.md).

---

## 1. Purpose & Traceability

**This is where the product makes money.** Every other customer-facing feature — search, chat, recommendations — exists to deliver a visitor to this form. It is one component, rendered in four contexts, and it must behave identically in all of them.

| Requirement | Source |
|---|---|
| FR6.1 Contact form (name, phone, email, message) — modal and inline | `01-prd.md` §7 |
| FR6.2 Callback request with a time-slot picker | `01-prd.md` §7 |
| FR6.3 Confirmation on submit (toast/screen); optional SMS/email confirmation | `01-prd.md` §7 |
| FR6.4 Every submission creates a lead tagged with source page and channel | `01-prd.md` §7 |
| Acceptance: **no duplicate lead records for a single submission (idempotency)**; every lead has a traceable source | `01-prd.md` §7 |

---

## 2. The Four Contexts

| Context | Rendered as | `source` | `property_id` |
|---|---|---|---|
| Property Details → "Schedule Visit" / "Request Callback" | Modal | `property_details` | ✅ set |
| Contact page | Inline | `contact_form` | ✗ null |
| Chatbot → `create_lead` tool | Conversational (the bot asks for fields one at a time) | `chatbot` | ✅ if in context |
| Portal Favorites → "Ask about this" | Modal, pre-filled | `contact_form` | ✅ set |
| *(Requirement wizard → agent follow-up)* | — | `requirement_form` | ✗ |
| *(Admin manually adds)* | Admin portal | `walk_in` | optional |

`leads.source` enum (`03-database-schema.md` §3.7): `chatbot`, `ai_search_inquiry`, `requirement_form`, `contact_form`, `walk_in`.

**Note:** `property_details` is **not** in that enum, but `14-screen-workflows.md` §4 says a Property Details inquiry sets `source = property_details`. **The docs contradict each other.** See §11.

---

## 3. Form Anatomy

```
┌──────────── Schedule a visit ─────────────────── [×] ─┐
│                                                       │
│  Sunview Residences · ₹78,00,000                      │  ← context header:
│  ────────────────────────────────────────────         │    shows WHAT they're
│                                                       │    asking about
│  Your name *                                          │
│  [_________________________________________]          │
│                                                       │
│  Phone *                                              │
│  [_________________________________________]          │  ← the field that
│  We'll call you on this number.                       │    actually matters
│                                                       │
│  Email                                                │
│  [_________________________________________]          │
│                                                       │
│  When works for you?          (callback mode, FR6.2)  │
│  [ Date ▾ ]  [ Morning / Afternoon / Evening ▾ ]      │
│                                                       │
│  Anything we should know?                             │
│  [                                          ]         │
│  [                                          ]         │
│                                                       │
│           [        Request a visit        ]           │
│                                                       │
│  We'll only use this to contact you about             │
│  this property.                                       │
└───────────────────────────────────────────────────────┘
```

**Field count is the conversion lever.** Name + phone are required; everything else is optional. Every additional required field measurably costs leads — and an agent can get the rest on the call.

---

## 4. Workflow

```
Visitor triggers the form (any of the 4 contexts)
   │
   ├─ Logged in? → pre-fill name / phone / email from their profile.
   │               A logged-in customer should never retype their own name.
   │
   ▼
Fills the form
   │
   ▼
Submit
   │
   ├─→ Client validation fails → inline field errors, nothing sent
   │
   ▼
Button disabled + spinner    ← duplicate-guard, layer 1
   │
   ▼
POST /leads              (or /leads/callback-request in callback mode)
   {customer_name, customer_phone, customer_email, message,
    property_id?, source}
   │
   │   Backend:
   │     1. Resolve tenant from the domain (NEVER from the client)
   │     2. Idempotency check          ← duplicate-guard, layer 2 (§6)
   │     3. Insert into `leads`: stage = 'new'
   │     4. Auto-assign to an agent per FR10.2 (or leave unassigned)
   │     5. Fire notification rules (FR15.2) → the agent is told
   │
   ▼
201 Created
   │
   ▼
Confirmation replaces the form in place:                        [FR6.3]
   "Thanks Priya — Anjali will call you on +91 98xxx xxxxx."
   │  · Name the agent if one was assigned. It converts a form
   │    submission into a human commitment.
   ▼
The trigger button becomes a passive "Inquiry sent ✓"
(so a second click can't create a second lead)
   │
   ▼
Lead lands in the admin Lead Pipeline → New column   [→ 17-admin-spec/07]
   │
   ▼
Visible to the customer at /portal/inquiries — IF they're registered
AND the leads↔user linkage exists (⚠ it currently does not — see §8)
```

---

## 5. States

| State | Behavior |
|---|---|
| Default | Empty (or pre-filled if logged in) |
| Validating | Inline, per-field, on blur |
| Submitting | Whole form locked, button spinner |
| Success | Confirmation in place. **Never** navigate away — the visitor loses their place and their sense that anything happened |
| Duplicate detected | Treat as success (`200`, returning the existing lead) — **not** an error. The visitor did nothing wrong; do not punish a double-click with a scary message |
| Validation error (400) | Map to the field. Keep every value |
| Server error (500) | "Couldn't send that — try again." All input preserved. If it fails twice, surface the tenant's phone number as a fallback. Never lose a motivated buyer to a 500 |
| Already inquired (this session, this property) | Form still opens, but notes "You already asked about this on 12 Jul" and offers "Send another message" instead of silently creating a duplicate |

---

## 6. Idempotency — FR6.4's Hard Requirement

*"No duplicate lead records created for a single submission."*

Client-side disabling is **not sufficient** — it doesn't survive a double-tap on a laggy mobile connection, a retry after a timeout that actually succeeded, or a page refresh mid-submit.

**Layered defense:**

| Layer | Mechanism |
|---|---|
| 1. Client | Disable the button on submit; keep it disabled through the response |
| 2. Client | Send an **idempotency key** (a UUID generated when the form opens) with the request. A retry of the same submission carries the same key |
| 3. Server | Reject/absorb a repeat of the same key within a window → return the existing lead with `200`, not a new one with `201` |
| 4. Server | A soft dedupe on `(tenant_id, customer_phone, property_id)` within a short window (say 10 minutes) catches the "user refreshed and resubmitted" case, which carries a *different* key |

**The idempotency key is not in `04-api-spec.md` today.** Add it (as an `Idempotency-Key` header or a body field) before Sprint 4 — this is a stated acceptance criterion with no specified mechanism.

---

## 7. Data Touched

| Table | Access |
|---|---|
| `leads` | **Write** — `tenant_id` (from domain), `property_id`, `customer_name`, `customer_phone`, `customer_email`, `source`, `stage = 'new'`, `assigned_agent_id` |
| `users` | Read (auto-assignment target; pre-fill for logged-in users) |
| `notification_rules` | Read (who to notify on `new_lead`) |
| *(callback slot)* | **Nowhere to store it — see §11** |

---

## 8. Permissions & Tenancy

- **Auth:** none. This endpoint is public by design and by requirement.
- **Tenant:** stamped from the domain, server-side. A client-supplied `tenant_id` is ignored, not validated (`04-api-spec.md` §1).
- **`leads` has no `user_id`.** A logged-in customer's inquiry is stored exactly like an anonymous one — so it can't be reliably shown back to them at [`/portal/inquiries`](10-portal-inquiries.md), and it can't be migrated on registration. **This is a blocking schema gap** (see [10-portal-inquiries.md](10-portal-inquiries.md) §8). Add `user_id` and `session_id` to `leads`.
- **Abuse:** `POST /leads` is unauthenticated and writes to the DB. Rate-limiting is specified only for `ai/*` (`04-api-spec.md` §1) — **this endpoint needs it too**, plus bot protection (honeypot field / CAPTCHA). Without it, a competitor can flood a tenant's pipeline with junk leads using one line of `curl`, and the agents lose trust in the CRM.

---

## 9. Validation & Edge Cases

| Field | Rule |
|---|---|
| `customer_name` | Required. Trim. 2–100 chars |
| `customer_phone` | **Required.** Lenient format validation (international variance) but reject obvious junk (`0000000000`, all-same-digit). This is the field the agent will actually use |
| `customer_email` | Optional (nullable in schema). If provided, must be well-formed |
| `message` | Optional. Cap at ~2000 chars |
| Callback slot | Must be in the future. Must be within the tenant's business hours (which aren't modeled — see §11) |

**Other cases:**
- **Stored XSS:** `message` is free text from an anonymous public endpoint, and it is rendered **in the admin portal's lead detail view**. Escape on output there. This is a direct anonymous-public → admin-browser script path. Treat it as such.
- **A lead for a sold/unpublished property:** still accept it. The agent can offer alternatives; a motivated buyer is valuable regardless of that one listing's status.
- **Chatbot-created leads:** the bot collects fields conversationally. It must not create a lead until it has at least name + phone (`14-feature-ai-chatbot.md` §8) — a half-empty lead is noise in the pipeline.
- **Auto-assignment (FR10.2):** round-robin vs. manual claim is **unresolved** (`14-screen-workflows.md` §10). Until it is, leads land unassigned, which means they can sit unattended. That's a product decision, not an implementation detail.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-LEAD-01 | A submission from each of the four contexts creates a lead with the correct `source` and `property_id` | Sprint 4 |
| TC-LEAD-02 | **A double submission creates exactly one lead** (FR6.4 idempotency) | Sprint 4 |
| TC-LEAD-03 | The lead appears in the correct tenant's pipeline in the `new` stage | Sprint 4 |
| TC-CHAT-03 | A chatbot conversation ends in a lead with `source = chatbot` | Sprint 6 |
| — | Every lead has a non-null `source` | FR10.4 |
| — | A `<script>` in the message field does not execute in the admin portal | Security test |

---

## 11. Open Questions

- [ ] **`source` enum contradiction.** `03-database-schema.md` §3.7 allows `chatbot | ai_search_inquiry | requirement_form | contact_form | walk_in`. `14-screen-workflows.md` §4 says a Property Details inquiry sets `source = property_details` — **which is not a valid value.** Either add `property_details` to the enum, or map that context to `contact_form` and track the originating page separately. **Fix `03-database-schema.md` and `14-screen-workflows.md` so they agree**, before Sprint 4.
- [ ] **The callback time slot has nowhere to live.** `POST /leads/callback-request` (FR6.2) is specified, but `leads` has no slot/appointment column and there's no `appointments` table. Either add columns to `leads` (`requested_callback_at`, `requested_slot`) or add a table. **Blocking for FR6.2.**
- [ ] **Idempotency mechanism is unspecified** despite being an explicit acceptance criterion (§6). Add an `Idempotency-Key` to `04-api-spec.md` §5.
- [ ] **Rate limiting / bot protection on `POST /leads`** — not specified for non-AI public endpoints.
- [ ] **Auto-assignment rule (FR10.2)** — round-robin, rules-based, or manual claim? Open in `01-prd.md` and `14-screen-workflows.md`.
- [ ] Whether the SMS/email confirmation in FR6.3 ships at MVP — requires a transactional provider, which **has been chosen** (SendGrid for email, Twilio for SMS per 02-architecture.md §3 and 03-database-schema.md §3.21).
