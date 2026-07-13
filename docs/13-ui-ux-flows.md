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

*Formalizes and expands `11-stitch-design-prompts.md` Section 0 into concrete tokens.*

### 4.1 Color Tokens

| Token | Hex | Usage |
|---|---|---|
| `color-ink` | `#12253B` | Primary text, headers, nav |
| `color-paper` | `#F3F5F6` | Page background |
| `color-brass` | `#C17F3C` | Primary CTA buttons, active/selected states |
| `color-brass-hover` | `#A66A30` | Primary button hover/active |
| `color-teal` | `#1F6F63` | Secondary actions, success states, "Published" badge |
| `color-slate` | `#5B6472` | Secondary/muted text, borders |
| `color-white` | `#FFFFFF` | Card/surface backgrounds |
| `color-amber` (semantic) | `#D9A441` | Warning / "Pending Approval" badge |
| `color-coral` (semantic) | `#C0392B` | Error states, "escalated" flags, destructive actions |

### 4.2 Typography Scale

| Role | Font | Size | Usage |
|---|---|---|---|
| Display | Fraunces (or Newsreader) | 32px | Page titles, property titles |
| Heading | Fraunces | 24px | Section headers |
| Subheading | Fraunces | 20px | Card titles, modal headers |
| Body | Inter (or General Sans) | 16px | Paragraph text, form labels |
| Small | Inter | 14px | Secondary text, table cells |
| Caption | Inter | 12px | Timestamps, helper text |
| Data/Mono | IBM Plex Mono | 14–20px (context-dependent) | Prices, area/measurements, stat figures |

### 4.3 Spacing Scale (4px base grid)

`4 · 8 · 12 · 16 · 24 · 32 · 48 · 64` (px) — component padding uses 8/16/24; section/page-level gaps use 32/48/64.

### 4.4 Component States

| Component | Default | Hover/Focus | Disabled/Error |
|---|---|---|---|
| Primary button | Solid `color-brass`, white text | `color-brass-hover` | 40% opacity, no pointer |
| Secondary button | Outline `color-teal` | Filled `color-teal`, white text | 40% opacity |
| Text link | `color-teal`, no underline | Underline on hover | `color-slate`, no pointer |
| Card (blueprint style) | Hairline border + corner tick marks | Slight lift (2px translate) | n/a |
| Form input | 1px `color-slate` border | 2px `color-brass` focus ring | 1px `color-coral` border + message below |
| Status badge | Pill shape, semantic background at 15% opacity, full-opacity text | n/a (static) | n/a |

### 4.5 Status Badge Colors (Reused Across Property & Lead States)

| State | Color |
|---|---|
| Draft | `color-slate` |
| Pending Approval | `color-amber` |
| Published / Active | `color-teal` |
| Sold / Closed (Won) | `color-ink` |
| Escalated / Closed (Lost) | `color-coral` |

### 4.6 Iconography

Line-style icons (not filled, not rounded/playful) at a consistent 1.5px stroke weight — matches the editorial, precision-oriented feel established in `11-stitch-design-prompts.md`.

### 4.7 Responsive Breakpoints

| Breakpoint | Range | Key Behavior |
|---|---|---|
| Mobile | < 640px | Admin sidebar collapses to a bottom nav or hamburger menu; property grid → single column |
| Tablet | 641–1024px | Property grid → 2 columns; admin sidebar collapses to icon-only |
| Desktop | > 1024px | Full sidebar; 3-column property grid |

### 4.8 Accessibility Notes

- Minimum text contrast ratio 4.5:1 against `color-paper`/`color-white` backgrounds — verify `color-brass` and `color-amber` specifically when used for text (not just backgrounds), as gold/amber tones commonly fail contrast at smaller sizes.
- Minimum touch target 44×44px on mobile (chat bubble launcher, favorite icon, filter chips).
- Form fields always have a visible label — never rely on placeholder text alone as the label, especially in the Requirement Analysis wizard (`01-prd.md` §5.3) and Property Management forms.
- Focus-visible outlines use `color-brass` at 2px, consistent with the form-input focus state (Section 4.4).

---

## 5. Open Questions / Assumptions to Confirm

- [ ] Whether the admin portal's mobile behavior (Section 4.7) needs full parity with desktop, or a deliberately reduced mobile feature set (e.g. view-only on mobile, full editing reserved for desktop) — needs product input, since admin usage patterns (Section 2, Vikram/Anjali flows) may be predominantly desktop-based in practice.
- [ ] Final font licensing/availability check for Fraunces/Newsreader and General Sans if a specific font-hosting approach (self-hosted vs. Google Fonts) is required.
- [ ] Whether dark mode is in scope for any surface — not currently assumed anywhere in this doc set.

---

**This closes out the current documentation set (00–13).** Revisit the "Open Questions" sections across all documents together before or during the first Claude Code build session — several are best resolved empirically once real implementation and load-testing begins.
