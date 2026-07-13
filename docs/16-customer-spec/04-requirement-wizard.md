# Page: Requirement Analysis Wizard

> **Route:** `/requirement-analysis` · **PRD Module:** 3 (AI Recommendation) · **App:** `public-site/` → `pages/RequirementAnalysis/`
> Part of [Doc 16 — Customer Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-customer-page) first.
> Spec: `07-ai-recommendation-spec.md`

---

## 1. Purpose & Traceability

For the visitor who **can't articulate a search query** — the first-time buyer who doesn't know what ₹80L buys in which locality. Instead of asking them to search, we ask them five easy questions and hand back a ranked shortlist with a plain-language reason for each match.

This is the third USP. Its output is not "results" — it's an **explained** shortlist.

| Requirement | Source |
|---|---|
| FR3.1 Multi-step form: budget, location, type, purpose, timeline, amenities | `01-prd.md` §4 |
| FR3.2 Ranked shortlist with visible match reason/score | `01-prd.md` §4 |
| FR3.3 Registered users can save and revisit/edit the profile | `01-prd.md` §4 |
| FR3.4 Saved profiles trigger notifications on new matches | `01-prd.md` §4 |
| FR3.5 Matching weights configurable per tenant | `01-prd.md` §4 |
| Screen workflow | `14-screen-workflows.md` §5 |

---

## 2. Entry & Exit Points

**Entry:** the homepage CTA band; the header nav; the empty state on [Property Listing](02-property-listing.md) ("no matches — try telling us what you need"); a chatbot suggestion; or `/portal/requirements` → "Edit profile" (which loads the wizard pre-filled).

**Exit:** the results view → a match card → [Property Details](03-property-details.md). Or registration, to save the profile.

---

## 3. Layout & Regions

```
┌──────────────────────────────────────────────────────────────┐
│ HEADER                                                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   ●━━━━━●━━━━━○━━━━━○━━━━━○     Step 3 of 5                  │
│  Budget Location Type Purpose Amenities                      │
│                                                              │
│         What kind of property are you looking for?           │
│                                                              │
│    ┌───────────┐  ┌───────────┐  ┌───────────┐              │
│    │           │  │           │  │           │              │
│    │ Apartment │  │   Villa   │  │   Plot    │   ← option    │
│    │           │  │           │  │           │     cards     │
│    └───────────┘  └───────────┘  └───────────┘              │
│    ┌───────────┐                                             │
│    │Commercial │                                             │
│    └───────────┘                                             │
│                                                              │
│   [ ← Back ]                              [ Next → ]         │
│                                                              │
│                            Skip this step                    │
└──────────────────────────────────────────────────────────────┘
```

**Results view (after the final step):**

```
┌──────────────────────────────────────────────────────────────┐
│  We found 6 homes that fit.          [ Edit my answers ]     │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ ┌──────┐  Sunview Residences            ★ 92% match     │ │
│  │ │ img  │  ₹78,00,000 · 3BHK · Whitefield                │ │
│  │ └──────┘                                                │ │
│  │  ✓ Within your budget                                   │ │
│  │  ✓ In your preferred location                           │ │
│  │  ✗ No gym  ← honest about the miss                      │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ ...                                              84%    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────── Save this profile ──────────────────────────┐   │
│  │ Create an account and we'll alert you when a new      │   │
│  │ matching home is listed.          [ Sign up ]         │   │
│  └───────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

| Region | Contents |
|---|---|
| Progress bar | 5 steps, current highlighted. Completed steps show a checkmark |
| Question | One question per step — never two |
| Option cards | Large tap targets. Single-select for steps 1–4; multi-select for amenities |
| Back / Next | Back always available (FR3.1). Next disabled until a selection is made, unless the step is skippable |
| Skip | Available on non-essential steps (amenities, timeline) — a wizard you can't skip is a wizard people abandon |
| Match card | Image, title, price, score, and **explicit ✓/✗ reason lines** |
| Save prompt | Post-results, for anonymous users only |

### 3.1 The Five Steps

| Step | Question | Input | Maps to |
|---|---|---|---|
| 1 | What's your budget? | Range cards (e.g. ₹40–60L) + a custom range | `budget_min`, `budget_max` |
| 2 | Where are you looking? | Multi-select locality chips + free text | `preferred_locations` (jsonb) |
| 3 | What type of property? | Single-select cards | `property_type` |
| 4 | Is this to live in, or to invest? | Two cards | `purpose` (`self_use` / `investment`) |
| 4b | When do you want to move? | Cards: Immediately / 3 months / 6 months+ | `timeline` |
| 5 | Any must-haves? | Multi-select amenity chips | `must_have_amenities` (jsonb) |

*(Timeline is folded into step 4's screen to keep the wizard at five perceived steps — six questions, five screens.)*

---

## 4. Workflow

```
Visitor starts the wizard
   │
   ▼
Step 1 (Budget) → selects → Next
   │      · answers are held in local component state (useReducer)
   │      · NOTHING is sent to the backend until the final submit —
   │        a half-finished wizard should not create a row
   ▼
Steps 2 → 3 → 4 → 5   (Back available throughout, FR3.1)
   │
   ▼
Final step submitted
   │
   ▼
POST /ai/recommend  { budget_min, budget_max, preferred_locations,
                      property_type, purpose, timeline, must_have_amenities }
   │
   │   Backend (per 07-ai-recommendation-spec.md):
   │     1. Persist requirement_profiles (keyed to user_id OR session_id)
   │     2. Score candidate properties using the tenant's configured
   │        weights (ai_config.recommendation_weights, FR3.5)
   │     3. Generate a plain-language match_reason per result (Bedrock)
   │     4. Persist requirement_matches
   │
   ▼
Ranked shortlist renders with ✓/✗ reasons              [FR3.2]
   │
   ├─→ Weak/no matches → closest-match fallback, NEVER an empty state
   │                     ("Nothing matched exactly. These come closest,
   │                      and here's what's different.")
   │
   ├─→ Clicks "Edit my answers" → wizard reopens pre-filled → re-submit
   │                              → PUT /ai/recommend/{id} (updates, no dupe row)
   │
   ├─→ Clicks a match card → /property/:id
   │
   └─→ Anonymous visitor registers here
          │
          ▼
       Session profile is re-keyed to user_id (README §4.2)      [FR3.3]
          │
          ▼
       New matching properties later trigger a notification      [FR3.4]
       (fired by the admin-side publish flow — see 17-admin-spec/04)
```

---

## 5. States

| State | Behavior |
|---|---|
| In progress | Answers survive an accidental back-button *within* the wizard. A page refresh mid-wizard may reset — acceptable for MVP, but persisting to `sessionStorage` is cheap insurance |
| Submitting | Full-view loading state with honest copy ("Matching you against 240 listings…"). This call is slow — it involves scoring plus a Bedrock reasoning call. **Do not** show a 300ms spinner and hope |
| Results — strong matches | Ranked cards with ✓/✗ reasons |
| Results — weak/no matches | Closest-match fallback + a nudge to widen budget or location. **Never an empty state** (FR3.2 acceptance criterion) |
| Results — tenant has almost no inventory | Fallback copy + a lead-capture prompt ("Tell us what you want and we'll find it") — turn a dead end into a lead |
| Bedrock failure (reasoning step) | **Still show the shortlist**, using deterministic scoring only, with generic reasons ("Matches your budget and location"). Losing the *explanation* must not lose the *results* (`.claude/rules/ai.md` — graceful degradation) |
| Rate-limited (429) | Same as above — serve the deterministic list |
| Total failure | Retry, plus a link to the [Listing](02-property-listing.md) with the answers mapped to filters — the visitor's effort is never wasted |
| Logged in | Profile auto-saves; no signup prompt; "Edit" updates the existing profile |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Final step submit | `POST /ai/recommend` | Returns `requirement_profile_id` + `matches[]` with `match_score` and `match_reason`. `04-api-spec.md` §3.3 |
| "Edit my answers" → resubmit | `PUT /ai/recommend/{requirement_profile_id}` | Updates the profile in place; re-runs matching. Does **not** create a second profile |
| Portal → "View my matches" | `GET /ai/recommend/{requirement_profile_id}` | Saved profile + latest matches |
| Delete a profile (FR7.3) | *(none specified)* | **Gap G6** — add to `04-api-spec.md` first |

Rate-limited per session/IP (it's an `ai/*` endpoint).

---

## 7. Data Touched

| Table | Access |
|---|---|
| `requirement_profiles` | Write (create/update; `user_id` **or** `session_id`, never neither) |
| `requirement_matches` | Write (the generated shortlist) |
| `properties` | Read (candidate scoring) |
| `property_embeddings` | Read (semantic component, tenant-scoped) |
| `ai_config` | Read (`recommendation_weights` — FR3.5) |

---

## 8. Permissions & Tenancy

- **Auth:** none. Anonymous visitors get the full experience; login only *persists* it.
- **Tenancy:** candidates come only from the domain's tenant. The weights come from **that tenant's** `ai_config` — a tenant that weights location over budget gets a different ranking, and that's the point (FR3.5).
- **Session:** an anonymous profile is written with `session_id` and no `user_id`; both must never be null simultaneously.

---

## 9. Validation & Edge Cases

- **Budget:** `budget_min ≤ budget_max`; reject a custom range where min > max at the input, not the API.
- **Skipped steps:** a skipped step means *no constraint*, not a zero. Skipping budget must not be scored as "budget = 0" — it must be excluded from the weighting entirely and the remaining weights renormalized.
- **Every step skipped:** effectively "show me anything" → fall back to a generic featured/recent list rather than running a meaningless match.
- **Amenity list must come from the same vocabulary as `properties.amenities`** — if the wizard offers "Gym" and listings store "gymnasium", every match silently misses. **One shared amenity taxonomy, or the feature quietly does not work.** (See §11.)
- **Duplicate submits:** the same anonymous session re-running the wizard should update its existing profile, not accumulate a new profile per attempt.
- **Free-text location:** must be matched against `location_address` semantically, not by exact string equality — "near tech park" is not a value in any column.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-REC-01 | Submitting the wizard returns a ranked shortlist | Sprint 7 |
| TC-REC-02 | A no-match scenario returns the closest-match fallback, never an empty/broken state | Sprint 7 |
| TC-REC-03 | Match reasons are plain-language and accurate to the actual gaps | Sprint 7 |
| TC-TENANT-01 | Recommendations never cross tenants | Sprint 1 |
| — | Tenant weight changes (FR3.5) alter ranking without a deployment | FR13.3 |

---

## 11. Open Questions

- [ ] **Shared amenity taxonomy.** Nothing in the doc set defines the canonical amenity list used by `properties.amenities`, the listing filters, and this wizard. Without it, matching is unreliable. This should be a fixed enum in `03-database-schema.md`, not free text. **Recommend resolving before Sprint 7.**
- [ ] **Gap G6:** no delete endpoint for a requirement profile, though FR7.3 requires it.
- [ ] Whether the visitor can jump back to an arbitrary step by clicking the progress bar, or only sequential Back — flagged as open in `14-screen-workflows.md` §10 too. (Recommendation: allow clicking back to any *completed* step. It's cheap, and the current sequential-only assumption makes editing one answer needlessly painful.)
- [ ] Where localities in step 2 come from. There's no locality table — so the chips are either hardcoded per tenant, derived from distinct `location_address` values, or free text only.
- [ ] Whether match score is shown as a raw percentage to customers (same concern as `02-property-listing.md` §11).
