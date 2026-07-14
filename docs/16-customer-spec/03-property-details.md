# Page: Property Details

> **Route:** `/property/:id` · **PRD Module:** 5 · **App:** `public-site/` → `pages/PropertyDetails/`
> Part of [Doc 16 — Customer Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-customer-page) first.

---

## 1. Purpose & Traceability

The conversion page. Everything before it is discovery; this is where a visitor becomes a **lead**. Design priority order: (1) can they picture living there, (2) can they afford it, (3) can they contact someone in one tap.

| Requirement | Source |
|---|---|
| FR5.1 Gallery, floor plan, amenities, price breakdown, map, landmarks | `01-prd.md` §6 |
| FR5.2 "Similar properties" | `01-prd.md` §6 |
| FR5.3 Sticky CTA (Request Callback / Schedule Visit) | `01-prd.md` §6 |
| FR5.4 Agent/builder contact info | `01-prd.md` §6 |
| FR5.5 EMI / affordability calculator | `01-prd.md` §6 |
| FR6.4 Every submission creates a traceable lead | `01-prd.md` §7 |
| Screen workflow | `14-screen-workflows.md` §4 |

---

## 2. Entry & Exit Points

**Entry:** a property card on the [Listing](02-property-listing.md) page; a featured card on the [Homepage](01-homepage.md); a property card **inside a chatbot reply**; a match card from the [Requirement Wizard](04-requirement-wizard.md); a notification deep link; the "Similar properties" carousel on another Details page; an external/shared link.

**Exit:** another Details page (via Similar); back to results; or — the goal — a **submitted inquiry** (lead created, confirmation shown, visitor stays on the page).

---

## 3. Layout & Regions

```
┌────────────────────────────────────────────────────────────────┐
│ HEADER                                                         │
├────────────────────────────────────────────────────────────────┤
│ ← Back to results                                              │
│                                                                │
│ ┌──────────────────────────────────────┐  ┌──────────────────┐ │
│ │                                      │  │ STICKY CTA CARD  │ │
│ │        GALLERY (hero image)      ♡  │  │                  │ │
│ │  [▪][▪][▪][▪]  thumbnails            │  │  ₹78,00,000      │ │
│ └──────────────────────────────────────┘  │  ₹6,500 / sqft   │ │
│                                           │                  │ │
│  Sunview Residences, Whitefield           │  ┌────────────┐  │ │
│  3 BHK · 1,200 sqft · Apartment           │  │Schedule    │  │ │
│  [Published]                              │  │Visit       │  │ │
│                                           │  └────────────┘  │ │
│ ┌── TABS ─────────────────────────────┐   │  ┌────────────┐  │ │
│ │ Overview │ Amenities │ Floor Plan │ │   │  │Request     │  │ │
│ │ Location │ EMI Calculator          │   │  │Callback    │  │ │
│ └─────────────────────────────────────┘   │  └────────────┘  │ │
│                                           │                  │ │
│  <active tab content>                     │  ── Agent ──     │ │
│                                           │  [avatar] Anjali │ │
│                                           │  +91 98xxx xxxxx │ │
│                                           └──────────────────┘ │
│                                            (sticky on scroll)  │
├────────────────────────────────────────────────────────────────┤
│  SIMILAR PROPERTIES                                            │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  → carousel               │
│  └──────┘ └──────┘ └──────┘ └──────┘                           │
└────────────────────────────────────────────────────────────────┘

Mobile: CTA card is NOT a sidebar — it becomes a fixed bottom bar
(price + one primary button), per FR5.3's "visible without obstructing".
```

| Region | Contents |
|---|---|
| Gallery | Images from `property_media` (`media_type = 'image'`, ordered by `sort_order`); lightbox on click; favorite heart overlaid |
| Title block | Title, type, beds/baths/area, status badge (colors per `DESIGN.md` → Semantic Status Colors) |
| Tabs | Overview (description + price breakdown), Amenities, Floor Plan, Location (map + landmarks), EMI Calculator |
| Sticky CTA card | Price, per-sqft, **Schedule Visit** (primary) + **Request Callback** (secondary), agent contact |
| Similar properties | Carousel from `GET /properties/{id}/similar` |

---

## 4. Workflow

```
Visitor arrives at /property/:id
   │
   ├─→ GET /properties/{id}          → page content
   └─→ GET /properties/{id}/similar  → carousel (independent; failure is non-fatal)
   │
   ▼
Overview tab shown by default
   │
   ├─→ Switches tab (Amenities / Floor Plan / Location / EMI)   [FR5.1]
   │      · all tab data arrives in the initial GET — no per-tab fetch
   │      · EMI calculator is 100% client-side arithmetic, no API call
   │
   ├─→ Taps ♡ → optimistic favorite (no login required)         [FR4.4]
   │      · after favoriting, an inline "Save this to your account?" prompt
   │        appears — after the action, never blocking it
   │
   ├─→ Clicks "Schedule Visit" or "Request Callback"            [FR5.3]
   │      │
   │      ▼
   │   Lead-capture modal opens  → see 15-feature-lead-capture.md
   │      │  name, phone, email, message (+ time-slot picker for callback)
   │      ▼
   │   POST /leads  (source = property_details, property_id attached)  [FR6.4]
   │      │
   │      ▼
   │   Confirmation shown in-modal → "An agent will contact you."
   │   Visitor stays on the page. The CTA button switches to a passive
   │   "Inquiry sent ✓" state so they can't double-submit.
   │
   ├─→ Opens chat with this property as context
   │      · property_id is passed to POST /ai/chat/message, so the bot
   │        already knows what they're looking at
   │
   └─→ Clicks a Similar card → /property/:id (workflow repeats)  [FR5.2]
```

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton for gallery + title; sticky CTA renders as soon as price is known |
| **Partial data** (the important one) | The page must not break on missing data. **No floor plan** → hide the tab, don't show an empty one. **No lat/lng** → hide the map, keep the address text. **No amenities** → hide the tab. **No agent assigned** (`agent_id IS NULL`) → show the tenant's general contact instead of an empty agent block. **No images** → branded placeholder, layout intact (FR5.1 acceptance criterion) |
| Not found / soft-deleted (`deleted_at`) | Friendly 404 with "browse similar properties" — not a raw error |
| Unpublished (draft/pending/archived) | Treated as 404 for the public. **Never** reveal that a draft exists |
| **Sold / On Hold** | Page still renders (SEO + the link may be shared), but the status badge says Sold, CTAs are replaced with "This property is no longer available — see similar" |
| Similar fetch fails | Hide the carousel silently. It's an enhancement, not the page |
| Inquiry already submitted this session | CTA shows "Inquiry sent ✓"; the form can be reopened but warns about duplicates |
| Logged in | Favorite persists to the account; the lead form is pre-filled from the user's profile |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount | `GET /properties/{id}` | Public read; returns 404 for non-published. `04-api-spec.md` §4 |
| Mount | `GET /properties/{id}/similar` | Reuses the recommendation engine (`07-ai-recommendation-spec.md`) |
| Heart tap | `POST` / `DELETE /properties/{id}/favorite` | Anonymous-safe |
| Inquiry submit | `POST /leads` | `{customer_name, customer_phone, customer_email, message, property_id, source: "property_details"}` |
| Callback submit | `POST /leads/callback-request` | Includes the chosen time slot |
| Chat opened here | `POST /ai/chat/message` with `property_id` | Gives the bot page context |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `properties` | Read (single, published only) |
| `property_media` | Read (images, floor plans, documents) |
| `property_embeddings` | Read (similar-properties vector query, tenant-scoped) |
| `favorites` | Write |
| `leads` | Write (inquiry / callback) |
| `users` | Read (assigned agent's name/phone — **only** the fields needed for display) |

---

## 8. Permissions & Tenancy

- **Auth:** none required for anything on this page, including submitting an inquiry.
- **Tenancy:** `GET /properties/{id}` must 404 if the property belongs to a different tenant than the request's domain — **not** return it. An ID-guessing visitor on tenant A's domain must not be able to read tenant B's listing (`TC-TENANT-02`).
- **Agent PII:** only expose the agent's display name and business phone. Never the agent's `users.id`, email, or role in the public payload.

---

## 9. Validation & Edge Cases

- **Duplicate lead prevention (FR6.4 acceptance):** a double-click on submit must not create two `leads` rows. Disable the button on submit *and* enforce idempotency server-side (see [feature 15](15-feature-lead-capture.md) §6).
- **Phone validation:** required, and the primary contact field — a lead without a reachable phone number is nearly worthless to an agent. Email optional (`leads.customer_email` is nullable).
- **EMI calculator:** pure client-side. Inputs = loan amount (default: price), interest rate, tenure. Guard against divide-by-zero at 0% interest and cap tenure sanely. It is an *estimate* — label it as one; do not imply a loan offer.
- **Price breakdown:** the schema has a single `properties.price` — there is no base/tax/maintenance breakdown to display. FR5.1's "price breakdown" is therefore **not currently supported by the schema** (see §11).
- **Very large galleries:** lazy-load beyond the first 3–4 images; the hero image gets `fetchpriority=high`.
- **Property changes status while the page is open** (e.g. admin marks it Sold): not handled live in MVP; the state is picked up on the next load. Acceptable — but the *inquiry* POST should still succeed rather than error, since the agent can follow up regardless.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-DETAILS-01 | Details page renders correctly, including with partial data | Sprint 3 |
| TC-LEAD-01 | Submitting the form creates a lead with the correct source and `property_id` | Sprint 4 |
| TC-LEAD-02 | No duplicate lead on double-submit | Sprint 4 |
| TC-REC-03 | Similar properties returns sensible results | Sprint 7 |
| TC-TENANT-02 | A tenant B property ID returns 404 on tenant A's domain | Sprint 1 |
| — | CTA remains visible while scrolling and does not obstruct content on mobile | FR5.3 |

---

## 11. Open Questions

- [ ] **"Price breakdown" (FR5.1) has no schema support.** `properties` has one `price` column. Either drop the requirement, or add structured price components to `03-database-schema.md` first.
- [ ] **"Nearby landmarks" (FR5.1) has no data source.** No column, no endpoint, and no maps-provider integration is specified. Is this manually entered per property, or derived from a Places API (cost + key management)?
- [ ] Whether "Schedule Visit" needs a real availability calendar (agent working hours, slot conflicts) or is just a *requested* time the agent confirms out-of-band. The schema supports only the latter (`leads` has no slot column at all — the requested slot currently has nowhere to live; see [feature 15](15-feature-lead-capture.md) §11).
- [ ] Default EMI interest rate — hardcoded, tenant-configurable, or user-entered only?
