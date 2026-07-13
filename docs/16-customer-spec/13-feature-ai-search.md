# Feature: AI Search (USP 1 of 3)

> **Appears on:** [Homepage](01-homepage.md) hero, [Property Listing](02-property-listing.md) header · **PRD Module:** 2 · **Component:** `public-site/src/components/search/`
> Part of [Doc 16 — Customer Spec](README.md). **Full pipeline spec: `06-ai-search-spec.md`** — this file covers the *customer-facing behavior*; that doc covers parsing, embedding, ranking, and the model.

---

## 1. Purpose & Traceability

Replace the filter grid with a sentence. The visitor types *"3BHK under 80 lakhs near the tech park, ready to move"* and gets ranked results — no dropdowns, no price sliders.

The product bet: **filters ask the user to translate their need into our schema; AI search does that translation for them.** Everything below exists to make that translation *visible and correctable*, because an invisible wrong translation is indistinguishable from broken search.

| Requirement | Source |
|---|---|
| FR2.1 Single free-text search bar | `01-prd.md` §3 |
| FR2.2 Parse into structured constraints + a semantic component | `01-prd.md` §3 |
| FR2.3 Rank by combined relevance | `01-prd.md` §3 |
| FR2.4 Auto-suggestions while typing | `01-prd.md` §3 |
| FR2.5 Voice input | `01-prd.md` §3 |
| FR2.6 Tenant-scoped results | `01-prd.md` §3 |
| FR2.7 Fallback to filter search on AI failure | `01-prd.md` §3 |

---

## 2. Component Anatomy

```
components/search/
├── SearchBar.tsx          the input + mic + submit (used on 2 pages)
├── Autosuggest.tsx        the dropdown            (Gap G3)
├── ParsedQueryChips.tsx   "here's what I understood" — the trust layer
├── VoiceInput.tsx         Web Speech API wrapper
├── FilterRail.tsx         the classic filters (must work standalone)
└── ResultsGrid.tsx        cards + match scores
```

```
┌────────────────────────────────────────────────┬─────┬─────┐
│ 3BHK under 80 lakhs near the tech park         │  🎤 │  →  │
└────────────────────────────────────────────────┴─────┴─────┘
   ┌─ Autosuggest ──────────────────────────────────────────┐
   │  ↳ 3BHK apartments in Whitefield                       │
   │  ↳ Properties near Manyata Tech Park                   │
   └────────────────────────────────────────────────────────┘

After submit — the receipt:
   [ 3 BHK × ]  [ ≤ ₹80L × ]  [ near tech park × ]  [ Apartment × ]
      ↑ each chip is removable; removing one re-runs the search
```

---

## 3. Workflow

```
Visitor types
   │
   ├─→ debounce ~250ms → autosuggest (Gap G3 — no endpoint yet)
   │
   ├─→ taps 🎤 → Web Speech API → transcript fills the input
   │              (client-side only; no audio ever hits our backend)
   │
   ▼
Submits
   │
   ▼
POST /ai/search { query, filters, page, page_size }
   │
   │   Backend (06-ai-search-spec.md):
   │     1. Validate/sanitize the query           ← prompt-injection hygiene
   │     2. Bedrock: parse into structured constraints
   │        (a LIGHT model — this is a cheap parsing task, not reasoning)
   │     3. Titan V2: embed the query (1024-dim)
   │     4. pgvector similarity, FILTERED BY tenant_id in the query itself
   │     5. Merge structured matches + semantic matches, rank
   │
   ▼
Response: { items[], parsed_query, total }
   │
   ▼
Render results + the parsed_query chips
   │
   ├─→ Visitor removes a chip → that constraint drops → re-query
   │      (this is how a misparse gets corrected without retyping)
   │
   └─→ Visitor adds a manual filter → merged with the AI query
          → an explicit filter always WINS over a parsed one (FR4.2)
```

### 3.1 Degradation — the path that actually matters (FR2.7)

```
POST /ai/search
   │
   ├─ Bedrock times out ──────┐
   ├─ Bedrock returns garbage ┤
   ├─ 429 rate-limited ───────┤
   └─ any AI-layer error ─────┘
                              │
                              ▼
              Fall back to GET /properties, treating the raw
              query as a keyword/location filter.
                              │
                              ▼
              Show results + a QUIET note: "Showing keyword results."
              ───────────────────────────────────────────────────────
              NOT an error toast. NOT an empty page. NOT a retry modal.
              The visitor asked for houses; give them houses.
```

The fallback is not an edge case to bolt on later — for a latency-sensitive public endpoint calling an LLM, it's a **routine** path. Build it in the same commit as the happy path.

---

## 4. Latency Budget

The visitor is staring at a spinner while we make **two** model calls (parse + embed) plus a vector query. Exact budgets live in `06-ai-search-spec.md`, but the UX rules:

| Elapsed | UI behavior |
|---|---|
| 0–400ms | Spinner in the search bar only |
| 400ms–budget | Skeleton result cards — communicate "results are coming", not "the page is stuck" |
| Over budget | Cut it off and fall back (§3.1). **A slow correct answer is worse than a fast keyword one.** |

Never let the AI path hang the page waiting for Bedrock.

---

## 5. Tenant Scoping — the highest-risk surface

`.claude/rules/ai.md`: *always pass `tenant_id` into every embeddings query.*

The dangerous implementation is the intuitive one:

```
❌  vectors = pgvector_similarity(query_embedding, limit=50)
    results = [v for v in vectors if v.tenant_id == current_tenant]   # post-filter
```

That "works" in a demo with one tenant and leaks the moment there are two — and worse, it silently returns *fewer* results than requested for a small tenant, because the top-50 global neighbours are dominated by the largest tenant's inventory. **The `tenant_id` filter must be inside the vector query**, so the ANN index is searched within the tenant's partition:

```
✅  vectors = pgvector_similarity(query_embedding, where tenant_id = :tenant_id, limit=50)
```

This needs its own test with two tenants' properties in the index and near-identical listings (`TC-TENANT-01`). A single-tenant test will pass either way and prove nothing.

---

## 6. Input Validation & Prompt-Injection Hygiene

The query string goes **straight into a Bedrock prompt** from an unauthenticated public endpoint. Per `.claude/rules/ai.md`:

- **Cap the length** (~300 chars). Unbounded input = unbounded token cost, paid by us.
- **Strip/neutralize instruction-shaped content** — `"ignore previous instructions and..."`. The parsing prompt should be structured so the user's text is clearly *data*, not instruction (delimited, and the system prompt should say the content is an untrusted search query).
- **The parse output must be schema-validated** before it touches SQL. The model returns JSON; parse it into a Pydantic model. Never interpolate model output into a query. A model that returns `{"bedrooms": "3; DROP TABLE"}` should fail validation, not reach the database.
- **Rate-limit per session/IP.** This endpoint costs money per call. An unauthenticated, uncapped Bedrock endpoint is a billing incident waiting to happen.

---

## 7. Prompts

Live **only** in `app/ai_clients/prompts/*.py`, versioned in a docstring (`.claude/rules/ai.md`). Never inline a prompt in `search_service.py`. When ranking quality shifts, the first question is "which prompt version?" — and that must be answerable from git.

---

## 8. Data Touched

| Table | Access |
|---|---|
| `properties` | Read (structured filter component) |
| `property_embeddings` | Read (pgvector; `tenant_id` **in** the query) |
| `property_media` | Read (thumbnails) |

Also logged per call (`.claude/rules/ai.md`): latency, token usage, model ID — for cost tracking and quality debugging. Low/no-result queries feed the admin's [Search Insights](../17-admin-spec/16-ai-config-search-insights.md) screen (FR13.4).

---

## 9. Edge Cases

| Case | Behavior |
|---|---|
| Empty / whitespace query | Don't submit |
| Gibberish (`"asdfgh"`) | The parse returns no constraints → falls through to semantic search → likely no results → show the requirement-wizard nudge, not an error |
| Query in another language | Claude handles it; results should still work. Worth a golden-set test case if the tenant's market is multilingual |
| Query that's actually a question (*"what's the cheapest 2BHK?"*) | Parses fine as a search. But this is really a **chatbot** query — consider offering "Ask our assistant instead →" |
| Query naming a specific property | Should surface that exact property first |
| Explicit filter contradicts the parsed query | The explicit filter wins; the chip updates to match |
| Voice unsupported | Hide the mic button (don't render a broken one) |
| Query with an injection attempt | Sanitized; never reaches the model as an instruction |

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-SEARCH-01 | A set of natural-language test queries returns results a human reviewer judges relevant | Sprint 5 |
| TC-SEARCH-02 | Latency stays within the budget in `06-ai-search-spec.md` | Sprint 5 |
| TC-SEARCH-03 | AI-parse failure falls back to filter search — never an error state (FR2.7) | Sprint 5 |
| TC-TENANT-01 | Two tenants with near-identical listings never see each other's results | Sprint 1 |
| — | Bedrock is **mocked** in unit tests; the golden-set eval suite runs separately, not in fast CI | `.claude/rules/testing.md` |

---

## 11. Open Questions

- [ ] **Gap G3 — no autosuggest endpoint** (FR2.4). It must not be a Bedrock call per keystroke. Recommend a cheap Postgres prefix/trigram query over `properties.title` + `location_address`, plus a cached list of popular queries. Add to `04-api-spec.md`.
- [ ] Which Claude model for parsing — `.claude/rules/ai.md` says pick per task with cost/latency in mind and confirm the ID in the AI spec doc. Parsing is a **light** task; don't put the strongest model on it. Confirm in `06-ai-search-spec.md` (and check `/claude-api` for current model IDs before hardcoding).
- [ ] Whether the match score is exposed to customers (see [02](02-property-listing.md) §11).
- [ ] Whether voice uses the browser's Web Speech API (free, inconsistent across browsers) or a backend transcription service (consistent, costs money, and means audio hits our servers — a privacy consideration). **Assumed browser-side.**
