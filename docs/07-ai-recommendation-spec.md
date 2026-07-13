# AI Recommendation Specification — PropVista CRM

> **Doc 07 of the PropVista CRM documentation set.** Detailed design for the requirement-analysis matching engine — the third of the platform's core USP features. Covers scoring logic, embedding reuse, match-reason generation, and saved-profile notifications.
>
> **Status:** Draft v1.0 · **Last updated:** July 2026
> Depends on: `01-prd.md` (Module 3), `02-architecture.md` (Section 6.3), `03-database-schema.md` (`requirement_profiles`, `requirement_matches`, `ai_config`), `04-api-spec.md` (Section 3.3), `06-ai-search-spec.md` (embedding approach reused here)

---

## 1. Purpose & Success Definition

Turn a short guided questionnaire into a ranked, explainable shortlist — so a visitor who doesn't want to browse or type a search query still gets to relevant properties fast. Success for MVP = every submission returns either a ranked shortlist or a clear "closest available" fallback (never an empty/broken state, per PRD FR3.2), with a plain-language reason per match.

---

## 2. Input: The Requirement Profile

Captured via the guided wizard (`04-api-spec.md` Section 3.3) into `requirement_profiles`:

| Field | Used For |
|---|---|
| `budget_min` / `budget_max` | Budget-fit scoring |
| `preferred_locations` | Location-fit scoring |
| `property_type` | Type-fit scoring |
| `purpose` (self_use / investment) | Influences which amenities/criteria matter more (Section 4) |
| `timeline` | Not scored directly at MVP — informs agent follow-up urgency in the CRM, not the ranking itself |
| `must_have_amenities` | Amenity-fit scoring |

---

## 3. Pipeline Overview

```
Requirement form submitted
   │
   ▼
[1] Build a composed requirement text (same template idea as property source_text, 06-ai-search-spec.md §4.1)
   │
   ▼
[2] Generate requirement embedding (Titan Embeddings — same model as AI Search, for a shared vector space)
   │
   ▼
[3] Retrieve candidates (parallel)
   ├── Structured filter query on `properties` (budget range, type, location overlap)
   └── Vector similarity query on `property_embeddings` (tenant-scoped)
   │
   ▼
[4] Score & Rank (Section 4) — using ai_config.recommendation_weights
   │
   ▼
[5] Generate match_reason per top result (Claude, Section 5)
   │
   ▼
Store in `requirement_matches`, return ranked shortlist (04-api-spec.md §3.3)
```

Steps 1–3 deliberately mirror AI Search's pipeline (`06-ai-search-spec.md`) — same embedding model, same dual-retrieval pattern — so the two features share infrastructure and stay consistent in what "a good match" means across the product.

---

## 4. Scoring Formula

```
match_score = (w_budget × budget_fit) + (w_location × location_fit)
            + (w_type × type_fit) + (w_amenities × amenities_fit)
            + (w_semantic × semantic_similarity)
```

- Each `w_*` weight comes from `ai_config.recommendation_weights` (per-tenant configurable, PRD Module 13) — defaults set during implementation and tunable by tenant admins.
- **`budget_fit`:** 1.0 if property price is within `[budget_min, budget_max]`; decays smoothly for prices just outside the range rather than a hard cutoff (a property 5% over budget shouldn't vanish entirely).
- **`location_fit`:** 1.0 for exact match against `preferred_locations`; partial credit for proximity if lat/lng distance is available.
- **`type_fit`:** 1.0 exact `property_type` match, 0 otherwise (binary — type mismatches are rarely a "close enough" case).
- **`amenities_fit`:** proportion of `must_have_amenities` present on the property.
- **`semantic_similarity`:** cosine similarity from the vector query (Section 3, Step 3) — catches nuance the structured fields don't capture (e.g. a property described as "family-friendly" matching an implicit need not explicitly ticked as an amenity).
- `purpose` (self_use vs. investment) adjusts which weights matter more as a **preset weight profile** rather than its own scored dimension — e.g. investment-purpose profiles might upweight location/appreciation-relevant signals over amenities. Exact preset differences to be defined during implementation with tenant input.

---

## 5. Match Reason Generation

- For each of the top-N results (N kept small, e.g. top 5–10, to control cost), a short Claude call (via Bedrock, same client as `05-ai-chatbot-spec.md`/`06-ai-search-spec.md`) generates a one-sentence plain-language explanation.
- **Input to the prompt:** the requirement profile fields + the specific property's attributes + its computed sub-scores (budget_fit, location_fit, etc.) — so the explanation is grounded in the actual scoring, not a free-floating guess.
- **Example output:** *"Matches your budget and preferred location; missing your requested gym amenity."*
- This is a single, short, low-token generation per property — batched in one call covering all top-N properties where possible, rather than N separate round-trips, to control latency and cost.

---

## 6. Saved Profiles & Ongoing Matching (FR3.3 / FR3.4)

- Registered users can save/edit their `requirement_profiles` (already modeled — `user_id` set instead of anonymous `session_id`).
- When a **new property is published** (property publish flow, `06-ai-search-spec.md` §4.2 indexing trigger), a background job additionally checks it against **active saved requirement profiles** for that tenant and creates new `requirement_matches` rows above a relevance threshold.
- New qualifying matches trigger a notification (ties into `notification_rules` / Customer Portal notifications, PRD Module 7) — "A new property matching your saved search is available."
- This reuses the same scoring logic (Section 4) — a saved profile is scored against one new property at publish time, rather than re-running the full candidate search.

---

## 7. Fallback Behavior (No Strong Matches)

Per PRD FR3.2, a submission must never return an empty/broken state:
- If no property clears a minimum relevance threshold, return the **closest available** properties anyway, with a match reason that's honest about the gap (e.g. *"Closest match: slightly above your budget, but matches your location and type preferences."*).
- If the tenant genuinely has zero properties matching the general type/location at all, return an empty state with clear messaging (not the same as "found something imperfect") — e.g. "No current listings match this closely; we've notified our team and will alert you when one becomes available."

---

## 8. Multi-Tenant Scoping

- All candidate retrieval (structured + vector) is scoped to `tenant_id`, enforced by RLS as the primary safety net (`03-database-schema.md` Section 4), same as AI Search.
- `recommendation_weights` in `ai_config` are per-tenant — one tenant's weighting tuning never affects another tenant.

---

## 9. Evaluation Approach

- Maintain a **golden requirement-profile set** (representative budget/location/type/amenity combinations) with human-judged "good match" property IDs against a test catalog, similar in spirit to the AI Search golden query set (`06-ai-search-spec.md` §9).
- Evaluate whenever scoring weights, the embedding approach, or the match-reason prompt changes.
- Track live metrics post-launch: shortlist-to-inquiry conversion rate, saved-profile-to-notification-click rate.

---

## 10. Open Questions / Assumptions to Confirm

- [ ] Default values for `w_budget`, `w_location`, `w_type`, `w_amenities`, `w_semantic` — to be tuned against the golden set during implementation.
- [ ] Exact preset weight differences between `self_use` and `investment` purpose profiles.
- [ ] Minimum relevance threshold that distinguishes "closest match fallback" from "no listings at all" (Section 7).
- [ ] Whether match-reason generation batches all top-N properties in one Bedrock call or is capped differently for cost reasons — to be validated with real token/cost measurements during implementation.

---

**Next document:** `08-auth-roles-spec.md` — authentication, tenant isolation enforcement, and role/permission detail.
