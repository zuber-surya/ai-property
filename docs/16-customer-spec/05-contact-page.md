# Page: Contact

> **Route:** `/contact` · **PRD Module:** 6 · **App:** `public-site/` → `pages/Contact/`
> Part of [Doc 16 — Customer Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-customer-page) first.

---

## 1. Purpose & Traceability

The general, property-agnostic entry into the CRM: a visitor who wants to talk to a human without having picked a listing. It's the lowest-tech path to a lead — and it must stay simple, because the people using it are the ones who bounced off everything cleverer.

| Requirement | Source |
|---|---|
| FR6.1 Contact form (name, phone, email, message) — modal and inline | `01-prd.md` §7 |
| FR6.2 Callback request with time-slot picker | `01-prd.md` §7 |
| FR6.3 Confirmation on submit | `01-prd.md` §7 |
| FR6.4 Every submission creates a lead tagged with source page + channel | `01-prd.md` §7 |

The form mechanics themselves are specified once in [`15-feature-lead-capture.md`](15-feature-lead-capture.md) — this page is the *inline* instance of it. Don't reimplement the form here; reuse the component.

---

## 2. Entry & Exit Points

**Entry:** header nav "Contact"; the footer; the Property Listing empty state; a chatbot handoff ("I'd rather just talk to someone"); a CMS page link.

**Exit:** confirmation state (the visitor stays on the page). No navigation away — a submit that redirects loses the sense that something happened.

---

## 3. Layout & Regions

```
┌──────────────────────────────────────────────────────────────┐
│ HEADER                                                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   Talk to us                                                 │
│   We'll get back to you within one business day.             │
│                                                              │
│  ┌────────────────────────────┐   ┌───────────────────────┐  │
│  │  CONTACT FORM              │   │  TENANT CONTACT INFO  │  │
│  │                            │   │                       │  │
│  │  Name *                    │   │  📍 Office address    │  │
│  │  [______________________]  │   │  📞 +91 80 xxxx xxxx  │  │
│  │                            │   │  ✉  hello@tenant.com  │  │
│  │  Phone *                   │   │                       │  │
│  │  [______________________]  │   │  Mon–Sat, 9:30–18:30  │  │
│  │                            │   │                       │  │
│  │  Email                     │   │  ┌─────────────────┐  │  │
│  │  [______________________]  │   │  │                 │  │  │
│  │                            │   │  │   map embed     │  │  │
│  │  Message                   │   │  │                 │  │  │
│  │  [                      ]  │   │  └─────────────────┘  │  │
│  │  [                      ]  │   └───────────────────────┘  │
│  │                            │                              │
│  │  ○ Send a message          │                              │
│  │  ● Request a callback  ────┼──→ reveals time-slot picker  │
│  │     ┌──────────────────┐   │                              │
│  │     │ Date  [ 14 Jul ▾]│   │                              │
│  │     │ Slot  [ 10–12 ▾] │   │                              │
│  │     └──────────────────┘   │                              │
│  │                            │                              │
│  │      [   Submit   ]        │                              │
│  └────────────────────────────┘                              │
└──────────────────────────────────────────────────────────────┘

Mobile: single column, form first, contact info below.
```

| Region | Contents |
|---|---|
| Contact form | The shared lead-capture component, rendered inline (not as a modal) |
| Mode toggle | "Send a message" (default) vs. "Request a callback" — the latter reveals the slot picker (FR6.2) |
| Tenant contact info | Address, phone, email, hours, map. **Currently has no data source** — see §11 |
| Confirmation | Replaces the form in place on success (FR6.3) |

---

## 4. Workflow

```
Visitor lands on /contact
   │
   ▼
Fills the form (name, phone, email, message)
   │
   ├─→ Mode = "Send a message"      → POST /leads
   │        source = "contact_form"
   │
   └─→ Mode = "Request a callback"  → POST /leads/callback-request  [FR6.2]
            source = "contact_form", plus the requested date/slot
   │
   ▼
Submit clicked
   │
   ├─ Client validation fails → inline field errors, no request sent
   │
   ▼
Button enters a loading state and is disabled (duplicate guard, FR6.4)
   │
   ├─ 400 validation error → map to the offending field, keep all input
   ├─ 500 / network error  → "Couldn't send that. Try again." — the form
   │                          keeps every value. Never make them retype.
   │
   ▼
Success (201)
   │
   ▼
Form is replaced in place by a confirmation panel:              [FR6.3]
   "Thanks, {name}. An agent will call you on {phone}."
   (+ optional SMS/email confirmation, FR6.3 — see §11)
   │
   ▼
Lead lands in the admin Lead Pipeline "New" column
   with source = contact_form                    [→ 17-admin-spec/07]
```

---

## 5. States

| State | Behavior |
|---|---|
| Default | Empty form, "Send a message" mode selected |
| Logged in | Name / phone / email pre-filled from the user's profile; only the message is empty |
| Validating | Inline, per-field, on blur — not a summary box at the top |
| Submitting | Button disabled + spinner. The whole form is locked to prevent edits mid-flight |
| Success | Confirmation panel replaces the form. A "send another" link is available but not prominent |
| Error | Error message above the button; all input preserved |
| Already submitted this session | Not blocked, but the confirmation panel notes "You already contacted us today" rather than silently creating a second identical lead |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Submit (message mode) | `POST /leads` | `{customer_name, customer_phone, customer_email, message, source: "contact_form"}`. No `property_id`. `04-api-spec.md` §5 |
| Submit (callback mode) | `POST /leads/callback-request` | Same fields + the requested time slot |
| Page load (tenant contact info) | *(none specified)* | See §11 — there is no endpoint or column for this today |

Both are anonymous endpoints and carry `X-Session-Id`.

---

## 7. Data Touched

| Table | Access |
|---|---|
| `leads` | Write — `source = 'contact_form'`, `stage = 'new'`, `property_id = NULL`, `assigned_agent_id = NULL` (or set by the auto-assignment rule, FR10.2) |
| `tenants` | Read (branding; contact info **if** the schema grows those columns) |

---

## 8. Permissions & Tenancy

- **Auth:** none. This is a public endpoint by design.
- **Tenancy:** the created lead is stamped with the domain-resolved tenant. The client never supplies it.
- **Abuse surface:** `POST /leads` is unauthenticated and writes to the database. It **must** be rate-limited per session/IP the same way the `ai/*` endpoints are, and it needs bot protection — otherwise a tenant's pipeline can be flooded with junk leads by anyone with `curl`. This is currently specified only for `ai/*` (`04-api-spec.md` §1). See §11.

---

## 9. Validation & Edge Cases

- **Required:** name, phone. **Optional:** email (`leads.customer_email` is nullable), message.
- **Phone:** validate format leniently (international variance) but require a plausible number. Reject obvious junk (`0000000000`).
- **Email:** if provided, must be well-formed — a malformed email silently breaks the confirmation email path.
- **Message length:** cap it (e.g. 2000 chars). It's a free-text field written to the DB from an unauthenticated endpoint.
- **Callback slot in the past:** reject client-side and server-side.
- **Double submit:** button disabled on submit + server-side idempotency ([feature 15](15-feature-lead-capture.md) §6).
- **XSS:** the message is rendered later in the **admin portal's** lead detail view. Escape on output there. Do not trust "it's just a lead note" — that's a stored-XSS path from an anonymous, public form straight into an admin's browser.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-LEAD-01 | A contact-form submission creates a lead with `source = contact_form` | Sprint 4 |
| TC-LEAD-02 | Double submission does not create a duplicate lead | Sprint 4 |
| TC-LEAD-03 | The lead appears in the admin pipeline's "New" stage, tenant-scoped | Sprint 4 |
| — | The confirmation is shown on submit (FR6.3) | FR6.3 |

---

## 11. Open Questions

- [ ] **Tenant contact info has no home in the schema.** `tenants` has `name`, `domain`, `branding_logo_url`, `branding_primary_color`, `status` — no address, phone, email, or hours. The right-hand panel of this page therefore has nothing to render. Add the columns to `03-database-schema.md` (and to the admin branding/settings screen, `17-admin-spec/20`), or drop the panel.
- [ ] **The callback time slot has nowhere to be stored.** `leads` has no slot/appointment column, and there is no `appointments` table. `POST /leads/callback-request` (FR6.2) is specified in `04-api-spec.md` with no destination for its core field. Resolve in `03-database-schema.md` before Sprint 4.
- [ ] **Rate limiting / bot protection on `POST /leads`** — currently unspecified for non-AI public endpoints. Recommend a per-IP limit plus a honeypot field or CAPTCHA on this form specifically.
- [ ] Whether the optional SMS/email confirmation (FR6.3) ships at MVP. It requires a transactional email/SMS provider, which is not chosen in `10-deployment-devops.md`.
