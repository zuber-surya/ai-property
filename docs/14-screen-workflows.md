# Screen Workflows — PropVista CRM

> **Doc 14 of the PropVista CRM documentation set.** Step-by-step interaction workflow for each of the 8 priority screens (matching `11-stitch-design-prompts.md` and the React components already built). Where `13-ui-ux-flows.md` traces navigation *between* screens per persona, this doc traces what happens *inside* each screen, click by click.
>
> **Status:** Draft v1.0 · **Last updated:** July 2026
> Depends on: `01-prd.md` (FR numbers), `13-ui-ux-flows.md` (persona flows)

---

## 1. Homepage

```
Page loads
   │
   ▼
Visitor types or speaks a query in the search bar (FR2.1, FR2.5)
   │
   ├─→ Auto-suggestions appear as they type (FR2.4)
   │
   ▼
Visitor submits query
   │
   ▼
Navigates to → Property Listing (results for that query)

Alternate paths from this screen:
- Clicks a quick-filter chip (Buy/Rent/Type/Budget/Location) → Property Listing, pre-filtered
- Clicks a Featured Property card → Property Details
- Taps the favorite icon on a card → favorited (session-based, no login required, FR4.4)
- Clicks the chat bubble (bottom-right) → Chat Widget opens as an overlay
```

---

## 2. Chat Widget

```
Visitor opens the chat bubble
   │
   ▼
Assistant greeting shown (tenant-configured, per ai_config)
   │
   ▼
Visitor types a message
   │
   ▼
System parses intent, calls a tool if needed (lookup_property / search_properties)
   │
   ▼
Assistant replies — plain text, or text + an embedded property card
   │
   ├─→ Visitor taps a quick reply ("Schedule a visit", "See similar", "Talk to an agent")
   │        │
   │        ▼
   │   If "Schedule a visit" → bot collects name/phone/time → create_lead + schedule_visit_or_callback tools fire
   │        │
   │        ▼
   │   Confirmation message shown in-chat
   │
   └─→ Visitor keeps typing → conversation continues, history retained for the session (FR1.6)

Escalation branch (any point):
Bot uncertain / visitor asks for a human → escalate_to_agent fires → conversation status → "escalated" →
visitor sees a clear handoff message → an agent picks it up from the Lead Pipeline
```

---

## 3. Property Listing

```
Visitor arrives (from Homepage search, a quick-filter chip, or direct nav)
   │
   ▼
Results render (grid view by default)
   │
   ├─→ Adjusts filters in the sidebar (price, type, bedrooms, amenities) → results re-query (FR4.2)
   ├─→ Changes sort order (Relevance / Price / Newest)
   ├─→ Toggles view: Grid ↔ List ↔ Map (FR4.1)
   ├─→ Taps favorite icon on a card → favorited, no login required (FR4.4)
   └─→ Clicks a property card
            │
            ▼
      Navigates to → Property Details

Pagination / infinite scroll loads more results at the bottom of the page.
```

---

## 4. Property Details

```
Visitor arrives (from a property card, chatbot link, or recommendation shortlist)
   │
   ▼
Gallery + Overview tab shown by default
   │
   ├─→ Switches tabs: Overview / Amenities / Floor Plan / Location / EMI Calculator (FR5.1)
   ├─→ Taps favorite icon → favorited
   ├─→ Clicks "Schedule Visit" or "Request Callback" (sticky sidebar CTA, FR5.3)
   │        │
   │        ▼
   │   Contact/Lead Capture form opens (modal) → visitor submits → confirmation shown →
   │   lead created with source = property_details, property_id attached (FR6.1, FR6.4)
   │
   └─→ Scrolls to "Similar Properties" carousel (FR5.2) → clicks another card
            │
            ▼
      Navigates to → Property Details (for the new property) — same workflow repeats
```

---

## 5. Requirement Wizard

```
Visitor starts the wizard (from Homepage nav or a direct prompt)
   │
   ▼
Step 1: Budget → selects a range card → Next
   │
   ▼
Step 2: Location → Step 3: Property Type → Step 4: Purpose → Step 5: Amenities
   (each step: select option card(s) → Next; "Back" available at every step, FR3.1)
   │
   ▼
Final step submitted
   │
   ▼
System generates ranked shortlist with match reasons (FR3.2)
   │
   ├─→ No strong match → closest-match fallback shown, never an empty state (FR3.2, per 07-ai-recommendation-spec.md §7)
   │
   ▼
Visitor clicks a result card → navigates to → Property Details

If registered/logs in at this point:
   │
   ▼
Requirement profile is saved (FR3.3) → future matching properties trigger a notification (FR3.4)
```

---

## 6. Admin Dashboard

```
Admin logs in → lands on Dashboard
   │
   ▼
KPI cards, charts, and activity feed render (tenant-scoped)
   │
   ├─→ Clicks an activity item, e.g. "New lead from AI Chatbot"
   │        │
   │        ▼
   │   Navigates to → Lead Pipeline (deep-linked to that lead)
   │
   ├─→ Clicks an activity item, e.g. "Property #204 published"
   │        │
   │        ▼
   │   Navigates to → Property Management (deep-linked to that listing)
   │
   └─→ Uses the left sidebar to jump directly to any module (non-linear navigation,
        per Vikram's flow in 13-ui-ux-flows.md §2.4)
```

---

## 7. Property Management

```
Admin arrives at the property list (default view)
   │
   ├─→ Searches / filters the table
   ├─→ Selects rows via checkboxes → bulk action toolbar appears
   │        → Approve Selected / Feature Selected / Archive Selected (FR9.1, FR9.4)
   │
   └─→ Clicks "Add Property"
            │
            ▼
      Multi-step form opens: Basic Info → Media → Pricing → Amenities → Location
            │
            ├─→ "Save as Draft" at any step → status = Draft
            │
            ▼
      Final step submitted
            │
            ▼
      If tenant requires approval → status = Pending Approval → a separate admin approves later
      If not → status = Published directly (FR9.3)
            │
            ▼
      On Published: background job generates the embedding and indexes the property
      (per 06-ai-search-spec.md §4.2) — now searchable and recommendable
            │
            ▼
      Saved requirement profiles are checked for a new match (per 07-ai-recommendation-spec.md §6)
```

---

## 8. Lead Pipeline

```
Agent arrives at the Kanban board (filtered to "assigned to me" by default)
   │
   ▼
Clicks a lead card → side detail panel slides in
   │
   ├─→ Logs a call/meeting note (FR10.3)
   ├─→ Sets a follow-up reminder (date picker)
   │
   ▼
Closes the panel, drags the card to the next stage
   (New → Contacted → Site Visit Scheduled → Negotiation → Closed)
   │
   ▼
Stage change recorded with a timestamp (lead_activities, per 03-database-schema.md)
   │
   ▼
Repeats until the lead reaches Closed (Won or Lost) — both outcomes tracked,
feeding the Reports module (PRD Module 15)
```

---

## 9. Cross-Screen Notes

- **Favoriting and inquiries never require login first** — the account prompt appears only when the visitor tries to *persist* something across sessions (Homepage, Property Listing, Property Details), per the UX principle already established in `13-ui-ux-flows.md` §2.1.
- **The chatbot can be opened from any public screen**, not just the Homepage — its workflow (Section 2 above) is identical regardless of entry point, only the initial context (e.g. which property was being viewed) differs.
- **Admin screens are not strictly sequential** — Section 6–8 describe the most common path through each screen, not a forced order; an admin can jump between Dashboard, Property Management, and Lead Pipeline in any order via the sidebar.

---

## 10. Open Questions / Assumptions to Confirm

- [ ] Whether the Requirement Wizard allows jumping back to edit an earlier step directly (e.g. clicking the progress bar) or only sequential "Back" navigation — currently assumed sequential-only for MVP simplicity.
- [ ] Whether bulk actions in Property Management (Approve/Feature/Archive Selected) show a confirmation dialog before applying, given they're irreversible-ish actions on multiple listings at once.
- [ ] Exact auto-assignment vs. manual-claim behavior for new leads landing in the Lead Pipeline "New" column — referenced as open in `01-prd.md` FR10.2 and not yet resolved here either.

---

**This complements `13-ui-ux-flows.md`** — read that doc for *between-screen* persona journeys and the design system; read this one for *within-screen* interaction sequences.
