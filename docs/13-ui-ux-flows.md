# UI/UX Flows & Design System — PropVista CRM

> **Doc 13 of the PropVista CRM documentation set.** Persona-based screen-to-screen navigation flows, site maps, and a written-up design system extracted from `11-stitch-design-prompts.md`'s shared design direction — expanded into concrete, engineering-usable tokens.
>
> **Status:** Draft v1.0 · **Last updated:** July 2026
> Depends on: `00-project-overview.md` (personas), `01-prd.md` (wireframe notes), `11-stitch-design-prompts.md` (design direction)

---

## 1. Purpose

`01-prd.md`'s wireframe notes describe what's *on* each screen. This doc describes how a person *moves between* screens, and locks down the visual system (colors, type, spacing, component states) so Stitch output, hand-built components, and Claude Code's implementation all stay consistent with each other.

---

## 2. Persona-Based User Flows

### 2.1 Priya, the First-Time Homebuyer — Discovery to Registered Account

```
Homepage
   │ enters a natural-language query
   ▼
Search Results (AI Search)
   │ opens a listing
   ▼
Property Details
   │ taps the favorite (heart) icon
   ▼
[Not logged in] → Inline prompt: "Sign up to keep this favorite"
   │ registers
   ▼
Customer Portal (favorite now persisted)
   │ returns later, submits an inquiry from Property Details
   ▼
Confirmation screen ("We've received your inquiry")
   │
   ▼
Customer Portal → Inquiries tab shows status updates over time
```

**Key UX principle:** favoriting never blocks on login — the prompt appears *after* the action, not before it, so Priya's momentum isn't interrupted (ties to PRD FR4.4).

### 2.2 Raj, the Repeat Investor — Filter-Heavy Comparison Flow

```
Homepage
   │ skips AI search, clicks "Browse All Properties"
   ▼
Property Listing (filters: price range, type, location)
   │ toggles Map View
   ▼
Property Listing (Map)
   │ opens 2-3 listings in sequence, comparing
   ▼
Property Details (per listing)
   │ registers to save a search
   ▼
Customer Portal → Saved Searches
   │ (later) new matching property published
   ▼
Notification → Property Details (direct deep link)
```

**Key UX principle:** power users bypass AI Search/Requirement Analysis entirely — the filter-first path must remain fully capable on its own, not degraded to push users toward the AI features (ties to PRD FR4.2).

### 2.3 Anjali, the Sales Agent — Lead Response Flow

```
Login → Admin Dashboard
   │ sees "3 new leads" activity item
   ▼
Lead Pipeline (Kanban, filtered to "assigned to me")
   │ opens a lead card
   ▼
Lead Detail Panel (contact info, timeline, notes)
   │ logs a call note, sets follow-up reminder
   ▼
Lead Detail Panel → drags card to "Site Visit Scheduled"
   │ (day of / after the visit)
   ▼
Lead Detail Panel → drags card to "Negotiation" → "Closed"
```

**Key UX principle:** stage changes happen via drag-and-drop on the board itself, not a separate "edit" form — minimizing clicks for a role that repeats this dozens of times a day (ties to `12-srs.md` NFR-USE-2).

### 2.4 Vikram, the Admin/Owner — Oversight Flow

```
Login → Admin Dashboard (KPI overview)
   │ notices a dip in conversion rate
   ▼
Reports → generates a "Leads by Source" report, exports PDF
   │ separately, reviews pending listings
   ▼
Property Management → approves 2 pending listings
   │ notices chatbot escalation rate is high
   ▼
AI Configuration → reviews flagged conversation logs, updates FAQ entries
   │
   ▼
User & Role Management → invites a new agent
```

**Key UX principle:** Vikram's flow is non-linear by nature — the admin portal's left-nav must make every module reachable in one click from anywhere, since owners jump between modules rather than following a fixed sequence.

---

## 3. Site Maps

### 3.1 Public Site

```
/ (Homepage)
├── /search (AI Search results / Property Listing)
├── /property/:id (Property Details)
├── /requirement-analysis (Guided wizard)
├── /contact
├── /login, /register
└── /portal (Customer Portal, authenticated)
    ├── /portal/favorites
    ├── /portal/requirements
    ├── /portal/inquiries
    └── /portal/notifications
```

### 3.2 Admin Portal

```
/admin/dashboard
├── /admin/properties (list, add/edit)
├── /admin/leads (Kanban + table)
├── /admin/agents
├── /admin/users (roles, invites, audit log)
├── /admin/ai-config (chatbot, search insights, recommendation weights)
├── /admin/cms (pages, SEO)
├── /admin/reports
├── /admin/settings (tenant branding)
└── /platform/tenants (super_admin only)
```

---

## 4. Design System

> ## ⚠️ The design system is [`docs/DESIGN.md`](DESIGN.md). It is not here.
>
> **Superseded 2026-07-13.** This section used to define a complete, parallel design system — `color-brass` `#C17F3C`, `color-teal` `#1F6F63`, a Fraunces/Inter/IBM-Plex-Mono type stack, a 4px grid, brass focus rings, and teal/amber status badges. **All of it is dead.** It was extracted from an early draft of `11-stitch-design-prompts.md` and was never reconciled when `DESIGN.md` became the system of record.
>
> Anything still citing "`13-ui-ux-flows.md` §4.1–§4.5" for a color, a font, a spacing value, a component state, or a badge color is citing a **deleted** system. Go to `DESIGN.md`.

| You want | Go to |
|---|---|
| Color tokens | `DESIGN.md` → token block + **Colors** |
| The AI/intelligence color rule | `DESIGN.md` → **Colors** (`tertiary`, AI output only) |
| Type scale & fonts | `DESIGN.md` → **Typography** (Plus Jakarta Sans — **no mono, no serif**) |
| Spacing & grid | `DESIGN.md` → **Layout & Spacing** (8px base, 4px half-step) |
| Radii | `DESIGN.md` → **Shapes** |
| Elevation, shadow, glassmorphism | `DESIGN.md` → **Elevation & Depth** |
| Buttons, inputs, chips, cards, AI widgets, lists | `DESIGN.md` → **Components** |
| Status badge colors | `DESIGN.md` → **Semantic Status Colors** |

**What changed, in case you have old work in flight:**

| Old (§4, deleted) | New (`DESIGN.md`) |
|---|---|
| `color-brass` `#C17F3C` — primary CTA | `primary` `#3525cd`, gradient to `secondary` `#0058be` |
| `color-brass` 2px focus ring | `primary` `#3525cd` 2px focus ring |
| `color-teal` `#1F6F63` — "Published" badge | `success-container` `#c3f0da` / `#00522f` |
| `color-amber` `#D9A441` — "Pending Approval" | `warning-container` `#ffddb0` / `#2c1700` |
| `color-slate` — "Draft" | `neutral-container` `#e2e1ec` / `#1a1a24` |
| `color-ink` — "Sold" | `inverse-surface` `#213145` / `#eaf1ff` |
| `color-coral` — error/escalated | `error-container` `#ffdad6` / `#93000a` |
| Fraunces / Inter / IBM Plex Mono | **Plus Jakarta Sans only** — prices are `headline-md`, not mono |
| "Blueprint" cards with corner tick marks | Bento cards — white, 24px radius, hairline border, ultra-soft shadow |
| *(nothing)* | **`tertiary` `#571ac0` — the AI intelligence layer.** New, semantic, and reserved: it marks model output and nothing else. |

### 4.6 Iconography

Line-style icons (not filled, not rounded/playful) at a consistent 1.5px stroke weight. This still holds — it suits the Soft Minimalism direction in `DESIGN.md` as well as it suited what preceded it.

### 4.7 Responsive Breakpoints

`DESIGN.md` states that the grid collapses to a single column on mobile and that desktop margins scale 40px → 20px, but it defines **no numeric breakpoints**. They live here, and this table is their source of truth.

| Breakpoint | Range | Key Behavior |
|---|---|---|
| Mobile | < 640px | Admin sidebar collapses to a bottom nav or hamburger menu; property grid → single column |
| Tablet | 641–1024px | Property grid → 2 columns; admin sidebar collapses to icon-only |
| Desktop | > 1024px | Full sidebar; 3-column property grid |

### 4.8 Accessibility Notes

- Minimum text contrast 4.5:1. Two pairs in `DESIGN.md` are known to be tight and must not carry small text: **`tertiary-container` + `on-tertiary-container` = 4.55:1** — nothing below 16px on it.
- Minimum touch target 44×44px on mobile (chat bubble launcher, favorite icon, filter chips).
- Form fields always have a visible label — never rely on placeholder text alone, especially in the Requirement Analysis wizard (`01-prd.md` §5.3) and Property Management forms.
- Focus-visible outlines use **`primary` `#3525cd`** at 2px. **Not `tertiary`** — a focused field is a user action, not model output, and the AI layer must not be diluted by a state that fires on every form field (`DESIGN.md` → Components).
- Status must never be conveyed by color alone — the four listing states are distinguishable by hue *and* carry text labels.

---

## 5. Open Questions / Assumptions to Confirm

- [ ] Whether the admin portal's mobile behavior (Section 4.7) needs full parity with desktop, or a deliberately reduced mobile feature set (e.g. view-only on mobile, full editing reserved for desktop) — needs product input, since admin usage patterns (Section 2, Vikram/Anjali flows) may be predominantly desktop-based in practice.
- [x] ~~Font licensing check for Fraunces/Newsreader and General Sans.~~ **Moot** — those faces were part of the superseded §4 type stack. The system is **Plus Jakarta Sans only** (`DESIGN.md` → Typography). A hosting decision is still needed for *that* face: self-hosted vs. Google Fonts.
- [ ] **Font hosting for Plus Jakarta Sans** — self-hosted (recommended: no third-party request on every page load, no CDN dependency) vs. Google Fonts. Not yet decided.
- [ ] Whether dark mode is in scope for any surface — not currently assumed anywhere in this doc set. `DESIGN.md` defines no dark palette; `inverse-surface` is a single dark accent, not a theme.

---

**This closes out the current documentation set (00–13).** Revisit the "Open Questions" sections across all documents together before or during the first Claude Code build session — several are best resolved empirically once real implementation and load-testing begins.
