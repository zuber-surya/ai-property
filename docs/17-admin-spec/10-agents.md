# Page: Agent / Broker Management

> **Route:** `/admin/agents` · **PRD Module:** 12 · **App:** `admin-portal/` → `pages/Agents/`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

The sales-manager view of the team: who's carrying what, who's converting, who's slow to respond.

**Note the separation of concerns:** this module is about *performance*; [User & Role Management](11-users-roles.md) is about *access*. Same `users` table, two different questions — and conflating them produces a screen that serves neither.

| Requirement | Source |
|---|---|
| FR12.1 Agent profile: contact info, assigned listings, assigned leads | `01-prd.md` §13 |
| FR12.2 Performance view: leads closed, response time, conversion rate | `01-prd.md` §13 |
| FR12.3 Leaderboard across agents within a tenant | `01-prd.md` §13 |
| Acceptance: **metrics recompute correctly as leads change stage/owner** | `01-prd.md` §13 |

---

## 2. Entry & Exit Points

**Entry:** sidebar; an agent's name anywhere (a lead card, a property row) → their profile.

**Exit:** an agent's assigned leads → the [Lead table](09-leads-table-and-assignment.md), pre-filtered. Their listings → [Properties](03-properties-list.md), pre-filtered.

---

## 3. Layout & Regions

```
┌──────────┬────────────────────────────────────────────────────────────┐
│ SIDEBAR  │  Agents                          [ Leaderboard ] [ List ]  │
│          │                                                            │
│          │  ┌──────────────────────────────────────────────────────┐  │
│          │  │ #│ Agent   │Active│Closed│ Conv. │ Avg. first  │     │  │
│          │  │  │         │leads │(30d) │ rate  │ response    │     │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ 1│ Anjali  │  12  │  8   │ 18.2% │  1h 20m     │  →  │  │
│          │  │ 2│ Meera   │   9  │  5   │ 14.7% │  3h 05m     │  →  │  │
│          │  │ 3│ Ravi    │  14  │  3   │  8.1% │ 🔴 11h 40m  │  →  │  │
│          │  └──────────────────────────────────────────────────────┘  │
│          │                                                            │
│          │  ── Agent profile (Ravi) ────────────────────────────────  │
│          │                                                            │
│          │  ┌────────┐  Ravi Kumar                                    │
│          │  │ avatar │  ravi@tenant.com · +91 98xxx xxxxx             │
│          │  └────────┘  Agent · joined Mar 2026                       │
│          │                                                            │
│          │  ┌─ ASSIGNED LEADS (14) ──┐  ┌─ ASSIGNED LISTINGS (6) ──┐  │
│          │  │ New            5  🔴   │  │ Published            4   │  │
│          │  │ Contacted      6       │  │ Pending approval     2   │  │
│          │  │ Negotiation    3       │  │                          │  │
│          │  │        [ View all → ]  │  │        [ View all → ]    │  │
│          │  └────────────────────────┘  └──────────────────────────┘  │
│          │                                                            │
│          │  ⚠ 5 leads have been in "New" for over 3 days.             │
└──────────┴────────────────────────────────────────────────────────────┘
```

| Region | Contents |
|---|---|
| Leaderboard | Ranked table (FR12.3). Sortable by any metric |
| Agent profile | Contact info + assigned leads (by stage) + assigned listings (FR12.1) |
| Actionable flag | "5 leads stuck in New" — **a metric that tells you what to do beats one that tells you a number** |

---

## 4. Workflow

```
Manager opens /admin/agents
   │
   ▼
GET /admin/agents            → list with summary stats
GET /admin/agents/leaderboard → ranked view
   │
   ▼
Leaderboard renders
   │
   ├─→ Sorts by "Avg. first response" → the slowest agent surfaces.
   │        Response time is the metric that most directly predicts
   │        whether a lead converts — a lead contacted in an hour is
   │        worth several contacted the next day.
   │
   ├─→ Clicks an agent → their profile
   │        │
   │        ▼
   │   GET /admin/agents/{id}
   │   GET /admin/agents/{id}/performance
   │
   ├─→ Clicks "Assigned leads → View all"
   │        → /admin/leads?view=table&agent=<id>
   │
   └─→ Sees "5 leads stuck in New"
            → the lead table, filtered to that agent + stage=new
            → reassigns or nudges
```

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton rows |
| **No agents yet** | "Invite your team →" → [Users](11-users-roles.md). A one-person tenant is a real case; this whole module is then pointless and could reasonably be hidden |
| Agent with no leads | Profile renders; metrics show "—", not "0%". **A new agent with a 0% conversion rate is a slander, not a statistic** |
| Insufficient data | Below N closed leads, show the raw count and suppress the rate. A single closed lead out of one is not "100% conversion" |
| Deactivated agent | Still listed (their history matters for reporting) but visually muted and excluded from the leaderboard |
| `agent` role viewing | **Own performance only** (`08-auth-roles-spec.md` §5.1). An agent must not see the leaderboard or their colleagues' numbers. See §8 |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount | `GET /admin/agents` | List + summary stats. `04-api-spec.md` §11 |
| Leaderboard | `GET /admin/agents/leaderboard` | Ranked |
| Profile | `GET /admin/agents/{id}` | |
| Performance | `GET /admin/agents/{id}/performance` | Leads closed, response time, conversion |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `users` | Read (`role = 'agent'`, tenant-scoped) |
| `leads` | Read (assigned, by stage — the source of every metric) |
| `lead_activities` | Read (**stage-change timestamps — this is where response time and conversion actually come from**) |
| `lead_notes` | Read (activity volume; first-contact timing) |
| `properties` | Read (assigned listings, via `agent_id`) |

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| View **own** performance | ✅ | ✅ | ✅ |
| View **another agent's** performance | ❌ | ✅ | ✅ |
| View the leaderboard | ❌ | ✅ | ✅ |

**Per `08-auth-roles-spec.md` §5.1, agents get "own performance only".** An endpoint that returns different data depending on who calls it is a bug waiting to happen — prefer either a hard 403 for agents on `/admin/agents/{other_id}/performance`, or a distinct `/admin/agents/me/performance` route. **The ownership check is server-side**; hiding the leaderboard nav item is not a permission.

(Whether a *sales team* should see each other's numbers is a culture question, not a technical one — but the spec says no, so the code says no.)

---

## 9. Validation & Edge Cases — Defining the Metrics

**Every metric on this page is undefined in the doc set.** FR12.2 names three; none is specified. And the acceptance criterion is that they "recompute correctly as leads change stage/owner" — which is impossible to test against an undefined metric.

| Metric | The question nobody has answered |
|---|---|
| **Leads closed** | `closed_won` only, or `closed_won + closed_lost`? (One measures success, the other measures throughput. Both are useful; they are not the same number.) |
| **Conversion rate** | Won ÷ *what*? All leads ever assigned? Leads assigned in the period? Leads *closed* in the period? **Each gives a different number**, and this must match the Dashboard and Reports or the CRM's numbers lose all credibility ([02](02-dashboard.md) §9) |
| **Response time** | From lead creation to... what? The first `lead_notes` entry? The first stage change out of `new`? Neither is really "we called them" — the agent could call and log nothing. **This metric measures what agents record, not what they do** — and agents will learn that |

**Additional traps:**
- **Reassigned leads:** Ravi worked it for two weeks, Meera closed it. Whose conversion? Whose response time? Without ownership-change history (Gap: [09](09-leads-table-and-assignment.md) §9), **you cannot even answer this**.
- **Leaderboards change behavior.** Rank by leads-closed and agents will cherry-pick easy leads and quietly neglect hard ones. That's not a hypothetical; it's what leaderboards do. Consider ranking on response time and activity (things an agent controls) rather than purely on outcomes (which depend on lead quality).
- **Small numbers lie.** Suppress rates below a minimum sample.
- **Timezone** — same unresolved issue as the Dashboard.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| — | Metrics recompute correctly when a lead changes stage or owner (FR12.2 acceptance) | `01-prd.md` §13 |
| — | Agent conversion figures reconcile with the Dashboard and Reports for the same range | Cross-module consistency |
| TC-ROLE-01 | An agent cannot retrieve another agent's performance (403) | Sprint 8 |
| TC-TENANT-01 | The leaderboard only ever contains the caller's tenant's agents | Sprint 1 |

---

## 11. Open Questions

- [ ] **Define every metric in FR12.2 precisely** (§9), in `01-prd.md`, with the **same definitions** used by the Dashboard and Reports. Three screens computing "conversion rate" three ways is the single fastest way to make a CRM's numbers untrusted — and once they're untrusted, nobody looks at them again.
- [ ] **Reassignment history doesn't exist**, so per-agent attribution on a reassigned lead is not computable. Ties to [09](09-leads-table-and-assignment.md) §9.
- [ ] **"Response time" measures logging discipline, not responsiveness** (§9). If the tenant cares about real responsiveness, something has to capture actual first contact — a call-logging integration, or at least a one-tap "I contacted them" action that's easier than not doing it.
- [ ] Whether agents should see the leaderboard (the spec says no; sales teams usually say yes — worth confirming with product rather than silently following either instinct).
- [ ] `properties.agent_id` exists, but nothing in the doc set says who sets it or when. Is a listing assigned at creation? Round-robin? Manually?
