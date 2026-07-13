# AI Search Specification — PropVista CRM

> **Doc 06 of the PropVista CRM documentation set.** Detailed design for natural-language property search — one of the platform's three core USP features. Covers query parsing, embedding/indexing, ranking, and evaluation.
>
> **Status:** Draft v1.0 · **Last updated:** July 2026
> Depends on: `01-prd.md` (Module 2), `02-architecture.md` (Section 6.1), `03-database-schema.md` (`property_embeddings`), `04-api-spec.md` (Section 3.1)
> **Embedding model finalized:** Amazon Titan Text Embeddings V2, 1024 dimensions, via Amazon Bedrock.

---

## 1. Purpose & Success Definition

Replace manual filter-hunting with a single free-text search box that understands intent. Success for MVP = a representative set of natural-language queries (Section 9) returns results a human reviewer judges relevant, within an acceptable latency budget (Section 7), with zero cross-tenant leakage.

---

## 2. Search Pipeline Overview

```
Visitor query (free text)
   │
   ▼
[1] Query Parsing (Claude via Bedrock)
   → structured constraints: property_type, listing_type, bedrooms, budget_min/max, location_hint, amenities[]
   │
   ▼
[2] Query Embedding (Titan Embeddings)
   → 1024-dim vector representing the query's full semantic intent
   │
   ▼
[3] Retrieval (parallel)
   ├── Structured filter query on `properties` (exact/range matches on parsed constraints)
   └── Vector similarity query on `property_embeddings` (pgvector, tenant-scoped)
   │
   ▼
[4] Merge & Rank (Section 4)
   │
   ▼
Ranked results returned to /ai/search (04-api-spec.md, Section 3.1)
```

Both retrieval paths run for every query — structured filtering narrows to plausible candidates cheaply, semantic search catches intent the parser missed or phrased loosely (e.g. "near tech park" with no exact location match).

---

## 3. Query Parsing (Step 1)

- Claude (same Bedrock integration as the chatbot, `05-ai-chatbot-spec.md`) is prompted to extract structured fields from the free-text query, returned as JSON (via Bedrock tool-use / structured output, not free text parsing).
- **Extracted schema:**
  ```json
  {
    "property_type": "apartment | villa | plot | commercial | null",
    "listing_type": "sale | rent | null",
    "bedrooms": "integer | null",
    "budget_min": "number | null",
    "budget_max": "number | null",
    "location_hint": "string | null",
    "amenities": ["string", "..."]
  }
  ```
- If parsing fails or returns malformed output, the pipeline falls back to treating the whole query as a semantic-only search (Step 2 still runs) rather than failing the request (Section 8).
- Parsing is a **single, fast, low-token call** — not a multi-turn conversation — to keep latency low.

---

## 4. Embedding Generation & Indexing

### 4.1 What Gets Embedded

For each property, `source_text` (in `property_embeddings`, per `03-database-schema.md`) is a composed string, not just the raw description:

```
"{title}. {property_type} for {listing_type}. {bedrooms} bedrooms, {area_sqft} sqft.
Located at {location_address}. Amenities: {amenities joined}. {description}"
```

Composing a consistent template (rather than embedding raw free text alone) ensures structured attributes (bedrooms, location, amenities) are captured in the semantic space too, improving recall for loosely-phrased queries.

### 4.2 Indexing Trigger

- On property create/update (admin publishes or edits a listing), a background task (`workers/embed_property.py`, per `02-architecture.md`) regenerates the embedding and upserts it into `property_embeddings`.
- `model_version` column tracks which embedding model/version produced each vector, so a future model upgrade can trigger a controlled re-embedding pass without ambiguity about what's stale.

### 4.3 Query-Time Embedding

- The visitor's raw query (or a lightly cleaned version) is embedded with the same Titan model at search time — model consistency between indexed data and query is required for meaningful similarity scores.

### 4.4 Vector Index

- pgvector index type: `hnsw` (preferred for query-time speed at this scale over `ivfflat`) on the `embedding` column, per `03-database-schema.md` Section 5.
- All vector queries include a `tenant_id` filter — enforced both by the query itself and by RLS (`03-database-schema.md` Section 4) as a second layer.

---

## 5. Merge & Ranking (Step 4)

A combined score per candidate property:

```
final_score = (w1 × structured_match_score) + (w2 × semantic_similarity_score)
```

- `structured_match_score`: how well the property satisfies the parsed constraints (e.g. 1.0 if all parsed filters match exactly, partial credit for near-misses like budget slightly over range).
- `semantic_similarity_score`: cosine similarity from the pgvector query, normalized to 0–1.
- `w1`/`w2` weighting: default weighted toward structured match when the parser extracted high-confidence fields (e.g. explicit budget/bedrooms), and weighted toward semantic similarity when the query was vague or the parser returned mostly nulls. Exact default weights to be tuned during implementation using the evaluation set (Section 9).
- Properties are deduplicated (a property appearing in both retrieval paths is scored once, using the combined formula) and sorted descending by `final_score` before pagination.

---

## 6. Auto-Suggest & Voice Search

- **Auto-suggest (typeahead):** As the visitor types, lightweight suggestions are drawn from a fast prefix/fuzzy match against property titles/locations (not a full AI parse+embed round-trip per keystroke, for latency reasons) — debounced client-side, hitting a lightweight `/properties?location_prefix=...`-style lookup rather than `/ai/search` directly.
- **Voice search:** Client-side (or a lightweight backend) speech-to-text converts spoken input to text, which is then submitted through the exact same `/ai/search` pipeline as typed text — no separate voice-specific backend logic needed.

---

## 7. Latency Budget

Target end-to-end response time for `/ai/search`: parsing + embedding + retrieval + ranking should complete within a low-second budget suitable for an interactive search box (specific number to be set after initial load testing — flagged in Section 10). Strategies to stay within budget:
- Run query parsing (Claude call) and query embedding (Titan call) **in parallel**, not sequentially, since they're independent.
- Cache parsed/embedded results for identical repeated queries within a short TTL window (helps with repeated/common queries across visitors on a tenant's site).
- Structured filter query and vector similarity query also run in parallel (Section 2).

---

## 8. Fallback Behavior

| Failure | Fallback |
|---|---|
| Query parsing call fails/times out | Skip structured constraints; run semantic-only search using the raw query embedding |
| Embedding call fails/times out | Fall back to structured-filter-only search (if parsing succeeded) or standard keyword/manual filter search |
| Both AI steps fail | Return standard non-AI filter/keyword search results, never an empty error to the visitor (per PRD FR2.7) |

---

## 9. Evaluation Approach

- Maintain a **golden query set**: representative natural-language queries (budget-driven, location-driven, amenity-driven, vague/loose phrasing, edge cases like typos or mixed languages) with human-judged relevant property IDs per tenant's test catalog.
- Evaluate ranking quality using standard IR metrics (e.g. precision@k, NDCG) against the golden set whenever the parsing prompt, embedding model, or ranking weights change.
- Track live operational metrics post-launch: zero-result-query rate, click-through rate on top results, and refinement rate (visitor re-searching immediately after a search — signals poor relevance).

---

## 10. Open Questions / Assumptions to Confirm

- [ ] Exact `w1`/`w2` ranking weights — to be tuned empirically against the golden query set during implementation.
- [ ] Specific latency target (e.g. "under 2 seconds") — pending initial load testing.
- [ ] Caching TTL and mechanism (in-memory vs. Redis) for repeated query parsing/embedding.
- [ ] Whether auto-suggest needs its own lightweight indexed table (e.g. property titles/locations) for fast prefix search, separate from the main `properties` table query path.

---

**Next document:** `07-ai-recommendation-spec.md` — the requirement-analysis matching engine, which reuses the embedding/indexing approach defined here.
