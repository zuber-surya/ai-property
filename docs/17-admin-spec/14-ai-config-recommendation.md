# Page: AI Configuration — Recommendation Weights

> **Route:** `/admin/ai-config/recommendation` · **PRD Module:** 13 · **App:** `admin-portal/` → `pages/AIConfig/Recommendation`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.
> Spec: `07-ai-recommendation-spec.md`

---

## 1. Purpose & Traceability

Lets a tenant tune what "a good match" means for *their* market. A luxury developer in a single locality cares about amenities and finish; a budget broker across a whole city cares about price and commute. The same scoring weights cannot serve both — so the tenant sets them.

| Requirement | Source |
|---|---|
| FR13.3 Requirement-analysis weighting config (e.g. budget vs. location importance) — per tenant | `01-prd.md` §14 |
| FR3.5 Matching logic is configurable per tenant | `01-prd.md` §4 |
| Acceptance: config changes take effect **without a deployment**; tenant-scoped only | `01-prd.md` §14 |

---

## 2. Entry & Exit Points

**Entry:** sidebar → AI Config → Recommendation tab.

**Exit:** [Search insights](16-ai-config-search-insights.md) (the other "is the AI working?" screen), or the public [requirement wizard](../16-customer-spec/04-requirement-wizard.md) to see the effect.

---

## 3. Layout & Regions

```
┌──────────┬────────────────────────────────────────────────────────────┐
│ SIDEBAR  │  AI Config   [Chatbot] [▪Recommendation] [Logs] [Search]   │
│          │                                                            │
│          │  How should we rank matches for your buyers?               │
│          │                                                            │
│          │  Budget fit                                                │
│          │  ├──────────●───────────────┤   40%                        │
│          │                                                            │
│          │  Location                                                  │
│          │  ├───────●──────────────────┤   30%                        │
│          │                                                            │
│          │  Amenities                                                 │
│          │  ├────●─────────────────────┤   20%                        │
│          │                                                            │
│          │  Property type                                             │
│          │  ├──●───────────────────────┤   10%                        │
│          │                              ────────                      │
│          │                              Total 100%  ✓                 │
│          │                                                            │
│          │  ┌─ PREVIEW ────────────────────────────────────────────┐  │
│          │  │ A sample buyer: 3BHK · ₹50–80L · Whitefield ·        │  │
│          │  │ wants parking + gym                                  │  │
│          │  │                                                      │  │
│          │  │  With your current weights   →  With the new ones    │  │
│          │  │  1. Sunview      92%             1. Palm Grove  89%  │  │
│          │  │  2. Palm Grove   84%             2. Sunview     87%  │  │
│          │  │  3. Lake View    71%             3. Green Acres 80%  │  │
│          │  │                                                      │  │
│          │  │  ↑ THE screen. An abstract slider means nothing;     │  │
│          │  │    a reordered shortlist means everything.           │  │
│          │  └──────────────────────────────────────────────────────┘  │
│          │                                                            │
│          │  [ Reset to defaults ]                        [ Save ]     │
└──────────┴────────────────────────────────────────────────────────────┘
```

| Region | Maps to |
|---|---|
| Sliders | `ai_config.recommendation_weights` (jsonb) — e.g. `{"budget": 0.4, "location": 0.3, "amenities": 0.2, "property_type": 0.1}` |
| Total | Must sum to 100% (§9) |
| **Preview** | The before/after shortlist. Without it this page is four sliders and a leap of faith |

---

## 4. Workflow

```
Admin opens the Recommendation tab
   │
   ▼
GET /admin/ai-config  → current weights
   │
   ▼
Drags a slider (e.g. Location 30% → 50%)
   │
   ▼
Other sliders auto-adjust to keep the total at 100%
   │   (or the total shows red until the admin fixes it — see §9)
   ▼
Preview re-scores a sample requirement profile live
   │   · uses a REAL saved profile from this tenant where one exists —
   │     "here's how your actual buyer's shortlist would change" is far
   │     more persuasive than a synthetic example
   ▼
[ Save ]
   │
   ▼
PUT /admin/ai-config/recommendation-weights
   │
   ▼
Takes effect for NEW recommendations immediately — no deploy  [FR13.3]
   │
   ▼
⚠ EXISTING requirement_matches rows were scored under the OLD weights.
  They are now stale. Three options, and the doc set picks none:
    (a) regenerate every saved profile's matches now (expensive —
        it's a Bedrock reasoning call per profile)
    (b) regenerate lazily, when the customer next views them
    (c) leave them; new matches use the new weights
  See §11. (b) is the sensible default.
```

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton sliders |
| First-time (no config) | Sensible platform defaults: budget 40 / location 30 / amenities 20 / type 10. **Never all-zero, and never an unweighted average** |
| Total ≠ 100% | The total goes red; Save is disabled with an explanation |
| Preview loading | Debounced — re-scoring on every pixel of slider drag is a lot of compute for a UI that's mid-gesture |
| No saved profiles to preview against | Fall back to a synthetic sample buyer, clearly labelled as one |
| Tenant has almost no inventory | Preview is meaningless with 3 properties. Say so rather than showing a confidently reordered list of three |
| Saved | "Live for new recommendations" + an honest note about existing matches (§4) |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount | `GET /admin/ai-config` | `04-api-spec.md` §12 |
| Save | `PUT /admin/ai-config/recommendation-weights` | |
| **Preview** | *(none)* | Same gap as the [chatbot sandbox](13-ai-config-chatbot.md) §11 — needs an admin-only preview endpoint that scores against unsaved weights |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `ai_config` | Read / Write (`recommendation_weights`) |
| `requirement_profiles` | Read (a real sample buyer for the preview) |
| `properties`, `property_embeddings` | Read (preview scoring) |
| `requirement_matches` | ⚠ **stale after a weight change** (§4) |
| *`audit_log`* | Should log weight changes — **doesn't exist (A1)**. When a tenant complains "the matches got worse", this is the first thing to check |

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| View / edit weights | ❌ | ✅ | ✅ |

Admin-only, tenant-scoped. **Tenant A's weights must never affect tenant B's rankings** — the weights are read from the requesting tenant's `ai_config` row on every scoring run (FR3.5, FR13.3 acceptance).

---

## 9. Validation & Edge Cases

- **Weights must sum to 1.0.** Two workable models, and it's worth choosing deliberately:
  - **Auto-normalize** (raise one, the rest shrink proportionally). Frictionless, but it silently changes values the admin didn't touch — which is confusing when they only wanted to raise Location.
  - **Require a manual 100%.** Explicit, but fiddly.
  **Recommend: auto-normalize, and animate the other sliders** so the admin *sees* what happened. Silent adjustment is the worst of both.
- **All weights zero:** reject. Every match would score 0 and the shortlist would be arbitrary.
- **A single weight at 100%:** allow — "I only care about budget" is a legitimate strategy — but warn that the other criteria will be ignored entirely.
- **The weights are only half the score.** `07-ai-recommendation-spec.md` combines deterministic criterion scoring with a semantic/vector component. **Which part do these sliders actually control?** If the semantic component is unweighted and untunable, a tenant who sets budget to 100% will still see semantically-similar-but-over-budget properties in their shortlist — and will reasonably conclude the sliders don't work. **This must be made explicit in `07-ai-recommendation-spec.md`**, and the UI should be honest about what it does and doesn't control.
- **Timeline and purpose** (`self_use` / `investment`) are captured by the wizard but have **no slider here**. Are they scored at all? Unweighted? The four sliders don't cover the six things the wizard asks about.
- **Match reasons must stay consistent with the weights.** If budget is weighted at 10% but the reason text still leads with "Matches your budget", the explanation is misleading.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-AICONFIG-01 | A weight change takes effect for new recommendations without a deployment | Sprint 8 |
| TC-REC-01 | Changing the weights **demonstrably reorders** the shortlist for the same requirement profile | Sprint 7 |
| TC-TENANT-01 | Tenant A's weights have no effect on tenant B's rankings | Sprint 1 |
| TC-ROLE-01 | An agent cannot read or write the weights (403) | Sprint 8 |

---

## 11. Open Questions

- [ ] **What happens to existing `requirement_matches` when the weights change?** (§4). **Recommend lazy regeneration on next view**, with a "scored under your previous settings" note if they're stale. Needs deciding in `07-ai-recommendation-spec.md`.
- [ ] **Do the sliders control the semantic component, or only the deterministic criteria?** (§9). This determines whether the feature does what the admin thinks it does — the most important open question on this page.
- [ ] **Which criteria are weightable?** The wizard captures six things (budget, location, type, purpose, timeline, amenities); this screen weights four. Are the other two scored? Silently? Not at all?
- [ ] **No preview endpoint** — same gap as the chatbot sandbox. A weights UI with no preview is a UI that gets set once, at random, and never touched again.
- [ ] Whether a tenant can weight *individual amenities* (a pool matters more than a lift, in some markets). Out of scope for MVP, but it's the obvious next ask.
