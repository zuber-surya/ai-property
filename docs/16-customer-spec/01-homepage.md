# Page: Homepage

> **Route:** `/` · **PRD Modules:** 2 (AI Search), 4 (Property Listing) · **App:** `public-site/` → `pages/Home/`
> Part of [Doc 16 — Customer Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-customer-page) first — the cross-cutting rules are not repeated here.

---

## 1. Purpose & Traceability

The homepage's single job is to get a visitor into a property result set as fast as possible — by natural-language search (the product's core USP), by a quick filter, or by clicking a featured listing. It is a launchpad, not a content page.

| Requirement | Source |
|---|---|
| FR2.1 Free-text search bar | `01-prd.md` §3 |
| FR2.4 Auto-suggestions while typing | `01-prd.md` §3 |
| FR2.5 Voice input | `01-prd.md` §3 |
| FR4.4 Favorite without login | `01-prd.md` §5 |
| FR1.1 Chat widget present on every public page | `01-prd.md` §2 |
| Screen workflow | `14-screen-workflows.md` §1 |

---

## 2. Entry & Exit Points

**Entry:** direct domain visit (the most common), a marketing link, or the site logo from any other page.

**Exit:**

| Action | Destination |
|---|---|
| Submits a search query | `/search?q=<query>` → [Property Listing](02-property-listing.md) |
| Clicks a quick-filter chip | `/search?<filters>` → Property Listing, pre-filtered |
| Clicks a featured property card | `/property/:id` → [Property Details](03-property-details.md) |
| Clicks "Find my match" / requirement CTA | `/requirement-analysis` → [Requirement Wizard](04-requirement-wizard.md) |
| Opens the chat bubble | Chat overlay — stays on `/` ([feature](14-feature-ai-chatbot.md)) |
| Taps a favorite heart | Stays on `/` (optimistic toggle, [feature](16-feature-favorites-session.md)) |

---

## 3. Layout & Regions

```
┌──────────────────────────────────────────────────────────────┐
│ HEADER  [tenant logo]        Buy  Rent  Contact   [Login]    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  HERO                                                        │
│    "Describe the home you're looking for."                   │
│  ┌────────────────────────────────────────────────┬───┬────┐ │
│  │ 3BHK under 80 lakhs near the tech park…        │ 🎤│ →  │ │
│  └────────────────────────────────────────────────┴───┴────┘ │
│    ┌─ autosuggest dropdown (on type) ───────────────────────┐ │
│    │ 3BHK apartments in Whitefield                          │ │
│    └────────────────────────────────────────────────────────┘ │
│                                                              │
│  QUICK FILTERS                                               │
│   [Buy] [Rent] [Apartment] [Villa] [Plot] [Under ₹50L]       │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  FEATURED PROPERTIES                                         │
│  ┌────────┐  ┌────────┐  ┌────────┐   (3-col desktop,        │
│  │ card ♡ │  │ card ♡ │  │ card ♡ │    2-col tablet,         │
│  └────────┘  └────────┘  └────────┘    1-col mobile)         │
├──────────────────────────────────────────────────────────────┤
│  REQUIREMENT CTA BAND                                        │
│   "Not sure where to start? Answer 5 questions →"            │
├──────────────────────────────────────────────────────────────┤
│  FOOTER   About · Terms · Contact · tenant contact info      │
└──────────────────────────────────────────────────────────────┘
                                              ┌─────┐
                                              │ 💬  │ ← chat launcher
                                              └─────┘
```

| Region | Contents | Notes |
|---|---|---|
| Header | Tenant logo + primary color (from tenant branding), nav, Login/Portal link | Branding comes from the tenant resolved by domain |
| Hero search | Single free-text input + mic button + submit | The visual centerpiece — see [AI Search feature](13-feature-ai-search.md) |
| Autosuggest | Dropdown under the input | **Gap G3** — no endpoint specified yet |
| Quick filters | Chips that bypass AI and go straight to filtered listing | Serves the power user (Raj, `13-ui-ux-flows.md` §2.2) |
| Featured properties | Property cards where `is_featured = true` | Card = image, title, price, beds/area, favorite heart |
| Requirement CTA | Band linking to the wizard | Third USP entry point |
| Footer | Static links, tenant contact | Links resolve to CMS pages ([12](12-static-cms-pages.md)) |
| Chat launcher | Fixed bottom-right bubble | ≥44×44px touch target |

---

## 4. Workflow

```
Page loads
   │
   ├─→ GET /properties?is_featured=true  → featured grid renders
   │
   ▼
Visitor engages the hero search
   │
   ├─ types ──→ autosuggest dropdown appears (debounced ~250ms)   [FR2.4]
   │
   ├─ taps mic ──→ browser speech-to-text fills the input          [FR2.5]
   │                (client-side Web Speech API; no backend call)
   │
   ▼
Submits (Enter, arrow button, or picking a suggestion)
   │
   ▼
Navigate to /search?q=<query>
   │  (the AI Search call itself is made by the Listing page, not here —
   │   so a refresh or a shared link reproduces the same results)
   ▼
Property Listing renders results

Alternate paths (do not leave the page):
   • Tap ♡ on a featured card → optimistic toggle → POST /properties/{id}/favorite
   • Open chat bubble        → chat overlay mounts, conversation starts
```

**Design note:** the homepage *navigates* with the query; it does not *execute* the search itself. Keeping the AI Search call on `/search` means the results URL is shareable and refresh-safe, and there is exactly one place that owns search state.

---

## 5. States

| State | Behavior |
|---|---|
| Loading (featured) | Skeleton cards in the grid — hero search is interactive immediately, never blocked on the featured fetch |
| Empty (no featured properties) | Hide the featured section entirely and show "Browse all properties →". Never render an empty grid with a sad face |
| Empty (tenant has zero published properties) | Featured section hidden; hero copy stays; CTA points at `/contact` |
| Error (featured fetch fails) | Hide the section, log to console, do not block the page — the search bar is the page's real purpose |
| Autosuggest unavailable | Input still works; suggestions simply never appear (silent degradation) |
| Voice unsupported (browser) | Hide the mic button entirely rather than showing a broken one |
| Logged in | Header shows "My Portal" instead of "Login"; favorite hearts reflect persisted `favorites` |
| Logged out | Header shows "Login"; hearts reflect session-scoped favorites |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Page mount | `GET /properties?is_featured=true&page_size=6` | `04-api-spec.md` §4. Only `published` properties are returned to the public |
| Typing in search (debounced) | *(none specified)* | **Gap G3** — FR2.4 has no endpoint. Do not invent one; add it to `04-api-spec.md` first |
| Favorite toggle | `POST` / `DELETE /properties/{id}/favorite` | Anonymous-safe; uses `X-Session-Id` |
| Chat launcher opened | `POST /ai/chat/message` | Only on first message, not on open — see [chatbot feature](14-feature-ai-chatbot.md) |

No `tenant_id` is ever sent (README §4.1).

---

## 7. Data Touched

| Table | Access |
|---|---|
| `properties` | Read (featured, `status = 'published'`) |
| `property_media` | Read (card thumbnail — lowest `sort_order` image) |
| `favorites` | Write (heart toggle) |
| `tenants` | Read (branding: logo, primary color) — resolved server-side by domain |

---

## 8. Permissions & Tenancy

- **Auth:** none required. The page is fully functional anonymous.
- **Tenancy:** the featured list is implicitly scoped to the domain's tenant. A visitor on `tenant-a.propvista.com` must never see a tenant B listing — enforced by RLS at the DB layer, with app-level `tenant_id` filtering as the second layer (`.claude/rules/security.md`).
- **Session:** `X-Session-Id` is generated on first load if absent and sent with every request.

---

## 9. Validation & Edge Cases

- **Empty query submit:** do nothing (don't navigate to an empty result page).
- **Very long query:** cap the input at a sane length (e.g. 300 chars) client-side — the query goes into a Bedrock prompt, so unbounded input is both a cost and a prompt-injection surface (`.claude/rules/ai.md`).
- **Query is just whitespace:** treat as empty.
- **Favorite tapped twice quickly:** debounce/optimistic-toggle so the UI can't get out of sync with the server; the last write wins.
- **Tenant branding missing a logo:** fall back to the tenant's `name` as a text wordmark. The header must not collapse.
- **Slow featured fetch:** never delay first paint of the hero.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-LIST-01 | Property browse/listing entry works from the homepage | `15-development-plan.md` |
| TC-SEARCH-01/02 | A natural-language query typed here returns relevant results on `/search` | Sprint 5 |
| TC-CHAT-01 | The chat widget is reachable from this page | Sprint 6 |
| — | Favoriting a featured card with no account persists for the session and survives a page reload | FR4.4 |
| — | No cross-tenant property ever appears in the featured grid | `TC-TENANT-01/02` |

---

## 11. Open Questions

- [ ] **Gap G3:** the autosuggest endpoint (FR2.4). Options: a cheap prefix/trigram query against `properties.title`/`location_address`, or a recent-popular-query cache. It should *not* be a Bedrock call per keystroke — that's a cost problem. Decide and add to `04-api-spec.md`.
- [ ] How many featured properties to show, and what happens when the tenant has marked more than that (most recent? random? admin-ordered?).
- [ ] Whether the homepage shows any CMS-editable hero copy/banner (FR14.1 says admins can edit homepage banners — which implies yes, and implies **Gap G5**, a public CMS read endpoint).
- [ ] Whether voice input (FR2.5) uses the browser's Web Speech API (free, browser-dependent) or a backend transcription service (consistent, costs money). Assumed browser-side for MVP.
