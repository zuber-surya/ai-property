# Page: Property Listing (Search Results)

> **Route:** `/search` · **PRD Module:** 4 · **App:** `public-site/` → `pages/Search/`
> Part of [Doc 16 — Customer Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-customer-page) first.

---

## 1. Purpose & Traceability

The single results surface for **both** discovery paths: AI natural-language search *and* classic filter browsing. Both must be first-class — a power user who never touches the AI search bar (Raj, `13-ui-ux-flows.md` §2.2) must be able to do everything with filters alone, without the UI nudging them toward the AI.

| Requirement | Source |
|---|---|
| FR4.1 Grid / list / map view toggle | `01-prd.md` §5 |
| FR4.2 Filters (price, type, bedrooms, location, amenities), combinable with AI search | `01-prd.md` §5 |
| FR4.3 Sort: relevance, price asc/desc, date added, area | `01-prd.md` §5 |
| FR4.4 Favorite without login | `01-prd.md` §5 |
| FR4.5 Pagination or infinite scroll | `01-prd.md` §5 |
| FR2.3 Results ranked by combined relevance | `01-prd.md` §3 |
| FR2.7 Fallback to filter search if AI parsing fails | `01-prd.md` §3 |
| Screen workflow | `14-screen-workflows.md` §3 |

---

## 2. Entry & Exit Points

**Entry:**
- Homepage search submit → `/search?q=<query>`
- Homepage quick-filter chip → `/search?property_type=villa`
- Header nav "Buy"/"Rent" → `/search?listing_type=sale|rent`
- A shared/bookmarked results URL (must reproduce the same results — see §4)
- "See similar" from the chatbot

**Exit:** a property card → `/property/:id`. Or the requirement wizard, offered when results are thin (§5).

---

## 3. Layout & Regions

```
┌──────────────────────────────────────────────────────────────────┐
│ HEADER  [logo]   ┌─ search bar (carries the query) ──────┐  [→]  │
├──────────────┬───────────────────────────────────────────────────┤
│ FILTER RAIL  │  RESULT HEADER                                    │
│              │   "24 properties · 3BHK under ₹80L near tech park"│
│ Price   ───  │   [Grid][List][Map]        Sort: [Relevance  ▾]   │
│  ▭▭▭▭▭▭▭▭   │  ┌─ parsed-query chips (AI only) ────────────────┐ │
│              │  │ [3 BHK ×] [≤ ₹80L ×] [near tech park ×]      │ │
│ Type    ───  │  └──────────────────────────────────────────────┘ │
│  ☐ Apartment │                                                   │
│  ☐ Villa     │  ┌────────┐ ┌────────┐ ┌────────┐                │
│  ☐ Plot      │  │ card ♡ │ │ card ♡ │ │ card ♡ │                │
│              │  │ ₹78L   │ │ ₹65L   │ │ ₹80L   │                │
│ Bedrooms ──  │  │ 92%    │ │ 88%    │ │ 84%    │ ← match score  │
│  1 2 3 4+    │  └────────┘ └────────┘ └────────┘   (AI results  │
│              │                                       only)       │
│ Amenities ── │  ┌────────┐ ┌────────┐ ┌────────┐                │
│  ☐ Parking   │  │  ...   │ │  ...   │ │  ...   │                │
│  ☐ Gym       │  └────────┘ └────────┘ └────────┘                │
│              │                                                   │
│ [Clear all]  │              [ Load more / pagination ]           │
└──────────────┴───────────────────────────────────────────────────┘
```

| Region | Contents |
|---|---|
| Header search bar | Pre-filled with the active query; editing it re-runs AI search |
| Filter rail | Price range, property type, bedrooms, location, amenities. Collapses to a "Filters (3)" bottom-sheet on mobile |
| Result header | Result count + the interpreted query in plain language |
| Parsed-query chips | **AI-search-only.** Shows what the model understood, each chip individually removable — this is the trust mechanism for the AI (see §4) |
| View toggle | Grid / List / Map (FR4.1) |
| Sort | Relevance (default for AI results) / Price ↑ / Price ↓ / Newest / Area |
| Result grid | Property cards with a favorite heart; AI results also show a match score |
| Pagination | Load-more or infinite scroll (FR4.5) |

---

## 4. Workflow

```
Arrive at /search with URL params (?q= and/or filters)
   │
   ├── Has ?q=  ────→ POST /ai/search {query, filters, page}
   │                     │
   │                     ├─ success → results + parsed_query
   │                     │             → render chips from parsed_query
   │                     │
   │                     └─ AI parse fails / times out / 429 (FR2.7)
   │                           │
   │                           ▼
   │                     Silently fall back: GET /properties with the raw
   │                     keywords as a location/title filter.
   │                     Show a quiet notice: "Showing keyword results."
   │                     Never show an error page. Never show zero results
   │                     because the AI failed.
   │
   └── No ?q=  ─────→ GET /properties?<filters> (pure filter browse)

Results render (grid by default)
   │
   ├─→ Adjusts a filter        → re-query, URL params update, page resets to 1
   ├─→ Removes a parsed chip   → that constraint drops, re-query
   ├─→ Changes sort            → re-query (server-side sort, not client-side)
   ├─→ Toggles Grid/List/Map   → no re-query; same result set, different render
   ├─→ Taps ♡ on a card        → optimistic toggle, POST /properties/{id}/favorite
   └─→ Clicks a card           → /property/:id
```

**The URL is the state.** Every filter, the query, sort, view, and page live in the query string. This makes results shareable, bookmarkable, refresh-safe, and back-button-correct — and it means there is exactly one source of truth for what's on screen.

**Chips are the AI's receipt.** When the model parses *"3BHK under 80 lakhs near tech park"* into `{bedrooms: 3, budget_max: 8000000, location_hint: "tech park"}`, the visitor sees exactly that and can correct it. Without this, a misparse looks like broken search.

---

## 5. States

| State | Behavior |
|---|---|
| Loading (first query) | Skeleton cards; filter rail interactive immediately |
| Loading (filter change) | Keep old results visible, dim them, show an inline spinner — do not blank the page on every filter tick |
| Empty (filters too narrow) | "No properties match these filters." + one-click **Clear all** + the loosest constraint suggested for removal ("Try widening your budget") |
| Empty (AI query, no matches) | Never a bare empty state — offer the [Requirement Wizard](04-requirement-wizard.md) and show the closest non-exact matches if the recommendation engine can supply them |
| AI degraded | Results still shown, plus a quiet "Showing keyword results" line. Not an error toast |
| Error (both AI and filter search fail) | Full-page retry state; the chat widget stays available as an escape hatch |
| Map view, no coordinates | Properties missing `location_lat`/`lng` are listed in a "not mapped" sidebar rather than silently dropped |
| Logged out | Hearts are session-scoped; a "Sign up to keep these" prompt appears after the 2nd favorite (not the 1st — don't nag) |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Arrive with `?q=` | `POST /ai/search` | Body: `{query, filters, page, page_size}`. Returns `items[]`, `parsed_query`, `total`. `04-api-spec.md` §3.1 |
| Arrive without `?q=`, or filter/sort change on a non-AI search | `GET /properties?...` | Params: `listing_type, property_type, price_min, price_max, bedrooms, location, amenities[], sort, page, page_size`. `04-api-spec.md` §4 |
| Filter change on an AI search | `POST /ai/search` with `filters` merged | FR4.2 — filters and AI query combine, they don't conflict |
| Favorite toggle | `POST`/`DELETE /properties/{id}/favorite` | See [feature 16](16-feature-favorites-session.md) |

**Rate limiting:** `/ai/search` is rate-limited per session/IP. On `429`, fall back to `GET /properties` (§4) — do not retry in a loop, and do not show the customer a rate-limit message.

---

## 7. Data Touched

| Table | Access |
|---|---|
| `properties` | Read — only `status = 'published'`, `deleted_at IS NULL` |
| `property_media` | Read (card thumbnails) |
| `property_embeddings` | Read (pgvector similarity, scoped by `tenant_id`) — AI path only |
| `favorites` | Write (heart toggle) |

---

## 8. Permissions & Tenancy

- **Auth:** none. Fully functional anonymous.
- **Tenancy:** FR2.6 — only the domain-resolved tenant's listings are searchable. **This is the single highest-risk leak point in the customer surface**, because the AI path queries a vector index rather than a plain filtered table: the pgvector query *must* carry `tenant_id` as a filter, not rely on post-filtering the results (`.claude/rules/ai.md`). RLS is the backstop, not the plan.
- **Draft/pending/archived properties are never visible here**, regardless of tenant.

---

## 9. Validation & Edge Cases

- **`price_min > price_max`:** clamp/swap client-side; the API should also reject with a 400 rather than returning a silently empty list.
- **Conflicting AI + manual filters** (query says "under 80 lakhs", user sets max = ₹1Cr): the **explicit filter wins** over the parsed one, and the corresponding chip updates to reflect it. Never silently apply both and return zero.
- **`page` beyond `total`:** return an empty page, not a 404; the UI shows "no more results".
- **Amenity filters are a jsonb GIN query** — must be an AND (has all selected), not an OR, unless the UI says otherwise.
- **Deep-linked stale filter** (e.g. an amenity that no longer exists): ignore the unknown value rather than erroring the whole query.
- **Map view on mobile:** full-screen with a bottom card carousel; the filter rail becomes a sheet.
- **Sorting AI results by price** discards relevance ranking — that's correct and expected, but the match-score badge should then be de-emphasized to avoid implying the order is by score.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-LIST-01 | Filters return correctly filtered, tenant-scoped results | Sprint 3 |
| TC-LIST-02 | Pagination/sort behave correctly across pages | Sprint 3 |
| TC-SEARCH-01 | A natural-language query returns results a reviewer judges relevant | Sprint 5 |
| TC-SEARCH-02 | Search latency stays within the budget in `06-ai-search-spec.md` | Sprint 5 |
| TC-SEARCH-03 | AI-parse failure falls back to filter search, never an error (FR2.7) | Sprint 5 |
| TC-TENANT-01/02 | No cross-tenant listing appears via either the filter path or the vector path | Sprint 1 |

---

## 11. Open Questions

- [ ] Pagination **or** infinite scroll (FR4.5 allows either). Recommendation: numbered pagination — it's shareable, matches the URL-is-state model, and is far easier to test than scroll virtualization.
- [ ] Whether the match-score badge is shown to customers at all, or is internal-only. A raw "84%" invites "why not 100%?" — a qualitative label ("Strong match") may be better. Ties to `06-ai-search-spec.md` ranking transparency.
- [ ] Map provider (Google Maps / Mapbox / Leaflet+OSM) — not chosen in any doc, and it has cost and API-key implications for `10-deployment-devops.md`.
- [ ] Whether "location" filtering is free-text, a fixed taxonomy, or radius-from-a-point. `properties` has `location_address` + lat/lng but no locality/zone column, so a fixed dropdown isn't currently supported by the schema.
