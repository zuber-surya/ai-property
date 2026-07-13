# Page: AI Configuration — Search Insights

> **Route:** `/admin/ai-config/search-insights` · **PRD Module:** 13 · **App:** `admin-portal/` → `pages/AIConfig/SearchInsights`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

**Demand data the tenant cannot get anywhere else.** Every failed search is a customer telling the business what it doesn't have: *"3BHK under ₹40L in Indiranagar"* × 47 searches, zero results. That's not a bug report — it's a market signal, and it's worth money.

FR13.4 modestly calls this "basic visibility into AI Search performance." It is more useful than that framing suggests, and it's the cheapest way to make the AI feel like it's working *for* the tenant rather than just running on their site.

| Requirement | Source |
|---|---|
| FR13.4 Basic visibility into AI Search performance (queries with no/low results) | `01-prd.md` §14 |
| Log every Bedrock call's latency, tokens, model ID | `.claude/rules/ai.md` |

---

## 2. Entry & Exit Points

**Entry:** sidebar → AI Config → Search tab.

**Exit:** [Add property](04-property-add-edit.md) — the direct action a zero-result query implies ("47 people wanted this and you don't have one"). Or the [property list](03-properties-list.md), to check whether the inventory really is missing or is just badly described.

---

## 3. Layout & Regions

```
┌──────────┬────────────────────────────────────────────────────────────┐
│ SIDEBAR  │  AI Config   [Chatbot] [Recommendation] [Logs] [▪Search]   │
│          │                                                            │
│          │  ┌── LAST 30 DAYS ────────────────────────────────────┐    │
│          │  │  1,284 searches · 84% returned results ·           │    │
│          │  │  avg 1.4s · 3.2% fell back to keyword search       │    │
│          │  └────────────────────────────────────────────────────┘    │
│          │                                                            │
│          │  ┌── QUERIES WITH NO RESULTS ─────────────────────────┐    │
│          │  │  These buyers wanted something you don't list.     │    │
│          │  │                                                    │    │
│          │  │  "3BHK under 40 lakhs in Indiranagar"      47×     │    │
│          │  │  "villa with a private pool"               31×     │    │
│          │  │  "office space near the metro"             28×     │    │
│          │  │  "1BHK for rent under 15k"                 22×     │    │
│          │  │                                                    │    │
│          │  │  💡 Consider listing in these segments, or         │    │
│          │  │     check whether your listings describe them.     │    │
│          │  └────────────────────────────────────────────────────┘    │
│          │                                                            │
│          │  ┌── QUERIES WITH FEW RESULTS (1–2) ──────────────────┐    │
│          │  │  "gated community with a clubhouse"        19×     │    │
│          │  │  "ready to move, no loan needed"           14×     │    │
│          │  │      ↑ you may HAVE these — but if your listing    │    │
│          │  │        descriptions don't say so, the AI can't     │    │
│          │  │        find them. This is a CONTENT problem, not   │    │
│          │  │        an inventory one, and it's fixable today.   │    │
│          │  └────────────────────────────────────────────────────┘    │
│          │                                                            │
│          │  ┌── HEALTH ──────────────────────────────────────────┐    │
│          │  │  Avg latency      1.4s      ▁▂▃▂▁▂▁                │    │
│          │  │  Fallback rate    3.2%      ▁▁▂▁▁▁▁  ← AI parse    │    │
│          │  │                                        failures    │    │
│          │  │  Est. cost/search ₹0.04                            │    │
│          │  └────────────────────────────────────────────────────┘    │
└──────────┴────────────────────────────────────────────────────────────┘
```

| Region | Value |
|---|---|
| Summary | Search volume, success rate, latency, fallback rate |
| **Zero-result queries** | *Demand you can't serve.* The commercially valuable panel |
| **Low-result queries** | Often a **description** problem, not an inventory problem — and that distinction is the most actionable insight on the page |
| Health | Latency, fallback rate, cost. Watching the fallback rate is how you notice the AI layer degrading before customers complain |

---

## 4. Workflow

```
Admin opens Search Insights
   │
   ▼
GET /admin/ai-config/search-insights
   │
   ▼
Reads: "3BHK under 40 lakhs in Indiranagar — 47 searches, 0 results"
   │
   ├─→ Interpretation A: they genuinely have no such inventory
   │        → a sourcing signal. Go find stock in that segment.
   │
   ├─→ Interpretation B: they DO have it, but the listings don't
   │   describe it in language that matches how buyers ask
   │        → go improve the descriptions                        [→ 04]
   │        → the embedding regenerates → the property becomes findable
   │        → THIS is the loop that makes AI search improve over time,
   │          and this screen is the only place it's visible.
   │
   └─→ Watches the fallback rate creep from 3% to 15%
            → the AI parse step is failing more often
            → a prompt or model problem, not a tenant problem
            → escalate to the platform team
```

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton |
| **Not enough data** | A new tenant with 12 searches. **Say so** — do not render a "top failed queries" list from three data points and invite them to make inventory decisions on noise |
| No failed queries | "Every search returned results." Genuinely good news; present it as such |
| High fallback rate | Flag it. It's a **platform** problem (the AI parse is failing), not something the tenant can fix, and the copy should say so rather than implying they've done something wrong |
| Zero searches | The public site may not be live yet, or the search bar isn't being used. Link them to check |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount | `GET /admin/ai-config/search-insights` | "Queries with low/no results, for tenant visibility." `04-api-spec.md` §12 |

---

## 7. Data Touched

| Table | Access |
|---|---|
| *search query log* | ⚠ **No table exists.** `03-database-schema.md` has no `search_queries` table |

**This is the gap.** `.claude/rules/ai.md` requires logging every Bedrock call's latency, token usage, and model ID — but that's operational telemetry (logs/metrics), not a queryable table. To render *"'3BHK under 40 lakhs in Indiranagar' — 47 searches, 0 results"*, you need the **query text**, the **result count**, and the **tenant**, aggregatable over time. Nothing stores that. See §11.

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| View search insights | ❌ | ✅ | ✅ |

- Tenant-scoped: an admin sees **their own** site's searches only. Aggregate query data across tenants would be commercially sensitive — a competitor's demand signals are exactly what a rival brokerage would want.
- **Search queries are user-generated text from anonymous visitors.** They can contain anything, including a prompt-injection attempt or a `<script>` tag, and they are rendered **in the admin's browser**. Escape on output. Same class of stored-XSS path as the lead message field.

---

## 9. Validation & Edge Cases

- **Query normalization.** "3bhk under 40 lakhs", "3 BHK under ₹40L", and "three bedroom under 40 lakh" are the same demand signal. Without normalization/clustering, the top-queries list is a long tail of near-duplicates and the "47×" count is meaningless. **The parsed structured query is the natural clustering key** — the AI already turned all three into `{bedrooms: 3, budget_max: 4000000, location: "indiranagar"}`. Cluster on *that*, not the raw string. It's a genuinely nice use of the parse step you're already paying for.
- **PII in queries:** rare, but people type strange things into search boxes. It's tenant-scoped data.
- **Bot/scraper traffic** will pollute the counts. Rate limiting helps; deduplicate by session.
- **"No results" vs. "no results after filters"** are different failures and should be distinguished — the first is an inventory gap, the second may be a UI problem.
- **Retention:** a query log grows quickly. Aggregate and roll up rather than keeping every raw query forever.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-AICONFIG-01 | Zero-result queries are visible to the tenant admin | Sprint 8 |
| TC-TENANT-01 | An admin sees only their own tenant's search queries | Sprint 1 |
| TC-ROLE-01 | An agent cannot access search insights (403) | Sprint 8 |
| — | Similar queries are clustered, so the counts mean something (§9) | FR13.4 |

---

## 11. Open Questions

- [ ] **No table stores search queries**, so FR13.4 cannot be built. Proposed:

  ```
  search_queries                        (tenant-owned)
    id            UUID PK
    tenant_id     UUID NOT NULL REFERENCES tenants(id)
    session_id    text NULL
    raw_query     text NOT NULL
    parsed_query  jsonb NULL     -- the structured parse; the clustering key
    result_count  int  NOT NULL
    used_fallback boolean DEFAULT false   -- did the AI parse fail? (FR2.7)
    latency_ms    int
    model_id      text
    created_at    timestamptz DEFAULT now()

    INDEX (tenant_id, created_at DESC)
    INDEX (tenant_id, result_count)   -- for the zero-result query
  ```

  This also satisfies `.claude/rules/ai.md`'s latency/model logging requirement in a queryable form, which the ops logs don't. **Add to `03-database-schema.md` before Sprint 5** — retroactively, you can't recover searches you never recorded, and this is the data that makes the AI improvable.

- [ ] **Query clustering strategy** (§9) — cluster on `parsed_query`, or on a normalized string?
- [ ] **Is per-search cost shown to tenants?** ("₹0.04/search") It's honest and it builds trust in a way most SaaS doesn't — but it also invites a conversation about pricing, and billing is explicitly out of scope (`00-project-overview.md` §4). Probably drop it for MVP.
- [ ] **Retention / rollup policy** for the query log.
- [ ] Whether the platform team gets a **cross-tenant** version of this screen. They should — it's how you'd notice the search parse quietly regressing for everyone after a prompt change — but it belongs under [super admin](21-superadmin-tenants.md), not here.
