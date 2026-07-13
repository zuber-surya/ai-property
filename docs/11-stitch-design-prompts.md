# Stitch Design Prompts — PropVista CRM

> **Doc 11 of the PropVista CRM documentation set.** Copy-paste-ready prompts for Google Stitch, covering the priority screen set across the public site and admin portal. Built from the wireframe notes in `01-prd.md` and the flows in `02`–`08`.
>
> **Status:** Draft v1.2 · **Last updated:** July 2026

---

## 0. Shared Design Direction

**The design system lives in [`DESIGN.md`](./DESIGN.md) — that file is the base and the single source of truth.** Its YAML token block is canonical: where `DESIGN.md`'s prose and its tokens disagree on a value, **the tokens win**, and the prompts below use token values only.

**How to use this doc:**

1. Paste the **entire contents of `DESIGN.md`** into Stitch first (frontmatter + prose). This establishes the theme for the session.
2. Then paste one screen prompt from below.
3. For subsequent screens in the same session, add *"match the style of the [previous screen]"* to keep Stitch consistent.
4. If a result drifts off-brand, re-paste `DESIGN.md` alongside the screen prompt rather than correcting with a vague follow-up like "make it nicer."

The prompts below deliberately do **not** repeat the design system — they only describe what is unique to each screen. Never fork a copy of the design block into this file; if the design changes, change `DESIGN.md`.

### 0.1 Token vocabulary used by the prompts

Every color, size and radius in the prompts below traces to a `DESIGN.md` token. This table is the mapping — read it once, then the prompts are self-explanatory.

| Role | Token | Value |
|---|---|---|
| Canvas / page background | `background` / `surface` | `#f8f9ff` |
| Card surface | `surface-container-lowest` | `#ffffff` |
| Chip / low-contrast fill | `surface-container` | `#e5eeff` |
| Input fill ("Effortless Field") | `surface-container-low` | `#eff4ff` |
| Hairline border | `outline-variant` | `#c7c4d8` |
| Primary text | `on-surface` | `#0b1c30` |
| Secondary text | `on-surface-variant` | `#464555` |
| **Primary action** | `primary` / `on-primary` | `#3525cd` / `#ffffff` |
| Primary button gradient | `primary` → `secondary` | `#3525cd` → `#0058be` |
| Primary tint (selected/hover) | `primary-fixed` | `#e2dfff` |
| **AI / intelligence layer** | `tertiary` family | `#571ac0`, container `#6f3dd9`, tint `#e9ddff` |
| Dark/inverse surface | `inverse-surface` | `#213145` |
| Error | `error` | `#ba1a1a` |

**Type:** Plus Jakarta Sans throughout — there is **no** mono and **no** serif face in this system. Prices use `headline-md` (24px / 600) in `on-surface`. Headings use `display-lg` (48px / 700) or `headline-lg` (30px / 600). Labels use `label-md` (14px / 600) or `label-sm` (12px / 500).

**Shape:** Cards `rounded.xl` (24px). Buttons and inputs `rounded.md` (12px). Chips and pills `rounded.full`. Large property imagery may go to 32px.

**Depth:** No heavy shadows. One ultra-soft shadow for floating/active elements: `0 10px 30px rgba(11,28,48,0.04)`. Glassmorphism = 20px backdrop blur + `rgba(255,255,255,0.7)` fill, used on nav bars and floating AI surfaces.

**Focus:** A focused input takes a 2px `primary` (`#3525cd`) ring — never tertiary. A focused field is a user action, not a model output.

**Containers:** ⚠️ `*-container` tokens are **saturated fills that take light text** — they invert the Material 3 convention. For a pale tint with dark text (selected chips, hover states, soft badges) use `*-fixed` (`primary-fixed` `#e2dfff`, `tertiary-fixed` `#e9ddff`). See `DESIGN.md` → Colors.

### 0.2 The one rule Stitch gets wrong most often

**`tertiary` is a semantic color, not decoration.** It marks the AI intelligence layer — anything the model generated, predicted, matched, or suggested — and nothing else. `primary` is for high-intent user actions. If Stitch applies `tertiary` to a button, a nav item, or a chart series that isn't AI-derived, correct it explicitly. This distinction is the visual backbone of the product.

> ℹ️ **Note on the AI accent.** `DESIGN.md`'s prose describes the AI layer as "Violet `#8B5CF6`", but no such token exists in its YAML. Since the tokens are the base, the prompts map the AI layer onto the **`tertiary`** family (`#571ac0` / `#6f3dd9` / `#e9ddff`) — the only violet in the token set. If you intended the literal `#8B5CF6`, add it to `DESIGN.md` as a token and this doc follows.

---

## 1. Public Site — Homepage / AI Search Landing

**Purpose:** First screen a visitor sees; the AI search bar is the hero.

**Key elements (from `01-prd.md` §5.1, §5.4):**
- Hero search bar with natural-language placeholder text
- Quick filter chips below the search bar (Buy/Rent, Property Type, Budget, Location)
- Voice search icon inside the search bar
- Featured/recommended property cards below the fold
- Persistent AI chatbot bubble, bottom-right

**Stitch prompt:**

```
Design a real estate homepage for PropVista CRM, following the shared
design direction.

Top navigation bar: glassmorphic (20px backdrop blur, rgba(255,255,255,0.7)
fill) — logo left, links (Buy, Rent, Requirement Analysis, Contact) center,
a "Sign In" text link and a "Register" button (primary #3525cd, white text)
right.

Hero: a full-width section on the #f8f9ff canvas with generous vertical
space (48px stack rhythm). A large search field centered on the page —
56px tall, 12px radius, #eff4ff fill, no border at rest. Because this is
AI-powered natural-language search, give it the AI treatment: a 1px
gradient border from primary #3525cd to tertiary #571ac0, plus a faint
tertiary background glow. Placeholder text reads "Try: 3BHK under 80 lakhs
near tech park". A microphone icon for voice search sits inside the right
edge of the field.

Below the search bar: a row of fully-rounded quick-filter chips with
#e5eeff fill and 14px semibold #464555 text — "Buy", "Rent",
"Property Type", "Budget", "Location".

Below the hero, a "Featured Properties" section: a bento grid of 6 property
cards (3 columns, 24px gutters). Each card is a #ffffff surface, 24px
radius, 24px padding, 1px #c7c4d8 hairline border — containing a 16:9
property photo (32px radius) with a small heart/favorite icon in the photo's
top-right corner; below the photo, the price at 24px semibold in #0b1c30,
then bedrooms/area, then location at 16px in #464555.

Bottom-right corner: a floating circular chat bubble button for the AI
chatbot — glassmorphic fill with a soft tertiary #571ac0 glow ring marking
it as the intelligence layer.

All text in Plus Jakarta Sans. No monospace, no serif.
```

---

## 2. Public Site — AI Chatbot Widget (Expanded)

**Purpose:** The conversational assistant panel, shown expanded mid-conversation.

**Key elements (from `01-prd.md` §5.2, `05-ai-chatbot-spec.md` §5):**
- Expandable chat window anchored bottom-right
- Message bubbles (user vs. assistant, visually distinct)
- Suggested quick-reply buttons
- "Talk to an agent" escalation option always visible
- Typing indicator

**Stitch prompt:**

```
Design the expanded AI chatbot widget panel for PropVista CRM (match the
style of the homepage).

Layout: a rounded panel, roughly 380px wide, anchored bottom-right, floating
above the page content. Because it is an AI surface, use the AI widget
treatment — glassmorphic fill (20px blur, rgba(255,255,255,0.7)), a 1px
gradient border from primary #3525cd to tertiary #571ac0, and a faint
tertiary glow. 24px radius. Only the ultra-soft shadow
0 10px 30px rgba(11,28,48,0.04) — no heavy drop shadow.

Panel header: "PropVista Assistant" at 14px semibold #0b1c30, a small status
dot indicating "online", and a close (X) icon.

Message area — a conversation thread with no borders between messages, just
vertical spacing:
- Assistant message (left-aligned, #eff4ff bubble, #0b1c30 text):
  "Hi! Looking for a home? Tell me what you need."
- User message (right-aligned, primary #3525cd fill, #ffffff text):
  "3BHK under 80 lakhs near tech park"
- Assistant message containing a small embedded property card (photo
  thumbnail, price at 24px semibold, one-line address) recommending a
  matching listing — this card carries a tertiary #571ac0 accent because it
  is an AI recommendation
- A typing indicator (three small dots) below the last message

Below the messages: a row of 3 fully-rounded quick-reply pill buttons with
#e5eeff fill — "Schedule a visit", "See similar properties", "Talk to an
agent".

Footer: a text input (12px radius, #eff4ff fill, border only on focus with a
2px primary #3525cd focus ring) with a send icon in primary #3525cd. Above
the input, a small persistent "Talk to an agent" text link, also primary
#3525cd.

All text in Plus Jakarta Sans.
```

---

## 3. Public Site — Property Listing / Search Results

**Purpose:** Browse/filter/compare screen after a search.

**Key elements (from `01-prd.md` §5.4):**
- Left sidebar filters (collapsible groups)
- Top bar: sort dropdown + grid/list/map view toggle
- Property cards with favorite icon
- Pagination or infinite scroll

**Stitch prompt:**

```
Design a property search results page for PropVista CRM (match the style of
the homepage).

Layout: left sidebar (approx 260px) with collapsible filter groups —
"Price Range" (slider), "Property Type" (checkboxes: Apartment, Villa, Plot,
Commercial), "Bedrooms" (fully-rounded pill buttons 1/2/3/4+, the selected
one filled primary #3525cd with white text), "Amenities" (checkbox list). A
"Clear filters" text link at the bottom. Separate groups with vertical space
and 1px #c7c4d8 hairlines — never heavy rules.

Main content, top bar: "128 properties found" in #464555, a sort dropdown
("Relevance", "Price: Low to High", "Newest"), and a three-way view toggle
(Grid / List / Map icons) as a rounded segmented control with the active
segment tinted #e2dfff.

Below: a responsive bento grid of property cards (3 columns, 24px gutters).
Each card is #ffffff, 24px radius, 24px padding, 1px #c7c4d8 border — a 16:9
photo with a small favorite heart icon top-right; the price at 24px semibold
in #0b1c30; a row of bedroom / bathroom / area icons; location at 16px in
#464555.

On cards that came from an AI search or recommendation, add a small
"AI match: 92%" badge — fully rounded, tertiary-tinted background #e9ddff
with tertiary #571ac0 text. This badge is the only tertiary element on the
card; do not use tertiary anywhere else here.

Pagination at the bottom: numbered page links in Plus Jakarta Sans, the
current page filled primary #3525cd.
```

---

## 4. Public Site — Property Details Page

**Purpose:** Single-listing deep-dive with conversion CTAs.

**Key elements (from `01-prd.md` §5.5):**
- Full image gallery/carousel
- Tabbed sections: Overview, Amenities, Floor Plan, Location, EMI Calculator
- Sticky sidebar with price + CTA buttons
- Similar properties carousel

> ⚠️ **OPEN QUESTION — not a design issue; do not silently guess.** The prompt below renders tabs *Overview / Gallery / Amenities / Location / AI Insights*, which does **not** match the PRD key-elements above — *Floor Plan* and *EMI Calculator* are missing, and *AI Insights* is added. The AI Insights panel (fair-price estimate, appreciation forecast, rental yield, buy-vs-rent) is **not** one of the three USP AI features anywhere in the specs. **Resolve in `01-prd.md` §5.5 first, then update this prompt to match** (see `.claude/rules/workflow.md`). This screen is not paste-ready until then.

**Stitch prompt:**

```
Design a property details page for PropVista CRM (match the style of the
homepage).

Hero: a large-inset image carousel showing 4-5 photos of the property, 32px
radius, indicator dots below. The photography is the protagonist — give it
the full width of the content column.

Below the hero: a sticky glassmorphic bar (20px blur, rgba(255,255,255,0.7))
showing, inline with space between — property type, a "For Sale" chip
(#e5eeff fill), the price at 48px bold in #0b1c30, and a neighbourhood/city
chip.

Lower section: a tabbed interface —
- Overview: description, a features list with checkmark icons, a
  construction-status chip
- Gallery: thumbnail strip + main image viewer
- Amenities: an icon grid grouped under "Essentials", "Comfort", "Safety"
- Location: interactive map with the property pinned + a radius slider for
  nearby schools/hospitals
- AI Insights: rendered as an AI widget — 1px gradient border from primary
  #3525cd to tertiary #571ac0, faint tertiary glow, tertiary #571ac0 accents
  — containing a fair price estimate with a confidence band, projected annual
  appreciation, rental yield prediction, and a buying-vs-renting comparison

Primary CTA: a "Message Agent" button, 56px tall, 12px radius, gradient from
primary #3525cd to secondary #0058be, white text — inline beside the tabs on
desktop, anchored bottom-right as a floating button on mobile.

Below the tabs: a horizontal scroll of "Similar Properties" cards — a smaller
version of the search-results bento card.
```

---

## 5. Public Site — Requirement Analysis Wizard

**Purpose:** Guided multi-step form feeding the AI recommendation engine.

**Key elements (from `01-prd.md` §5.3):**
- Multi-step wizard with progress bar
- Large tappable option cards per step
- Final step: recommended results carousel

**Stitch prompt:**

```
Design a multi-step "Find Your Match" requirement analysis wizard for
PropVista CRM (match the style of the homepage).

Layout: a single centered bento card, max-width 600px — #ffffff surface, 32px
padding, 24px radius, 1px #c7c4d8 border — sitting on the quiet #f8f9ff
canvas with generous surrounding space.

Top of the card: a thin fully-rounded progress bar (step 2 of 5 filled in
primary #3525cd, track in #e5eeff) and a "Step 2 of 5" label at 12px medium
in #464555.

Current step: "What's your budget?" as a 30px semibold heading in #0b1c30
with tight letter spacing, followed by a row of large tappable option cards —
"Under 50L", "50L-80L", "80L-1.2Cr", "1.2Cr+". Each option card is generously
padded with a 12px radius and a 1px #c7c4d8 border; the selected one has a
2px primary #3525cd border and a faint #e2dfff tint.

Bottom of the card: a "Back" text button (left, #464555) and a "Next" button
(right, 56px tall, gradient from primary #3525cd to secondary #0058be, white
text).

Include a second smaller mockup below showing the final results step: heading
"Your Matches", then a horizontal carousel of 3 property cards. These are
AI-generated recommendations, so each card gets the AI widget treatment — 1px
primary-to-tertiary gradient border and a faint tertiary glow — plus a short
caption in tertiary #571ac0 beneath the price: "Matches your budget and
location".
```

---

## 6. Admin Portal — Dashboard

**Purpose:** Landing screen for admins after login.

**Key elements (from `01-prd.md` §9):**
- KPI cards (listings, leads, conversion rate, traffic)
- Charts (lead source, property views)
- Recent activity feed

**Stitch prompt:**

```
Design an admin dashboard for PropVista CRM's admin portal. Same tokens,
typography, radii and elevation as the public site, but a more compact,
data-dense layout for daily internal use — 24px card padding rather than
32px, less decorative, more functional. Keep the bento philosophy: modules in
rounded #ffffff containers on the #f8f9ff canvas, 1px #c7c4d8 hairlines, no
heavy shadows.

Left sidebar navigation (icons + labels: Dashboard, Properties, Leads, Agents,
Reports, AI Config, Settings) with the PropVista logo at top and the current
tenant/business name below it in 12px #464555. The active nav item is marked
with a #e2dfff tint and primary #3525cd text.

Main content, top row: four KPI cards side by side — "Total Listings",
"Active Leads", "Conversion Rate" (percentage), "Site Visitors". Each is a
#ffffff bento card with a 14px #464555 label above a large 30px semibold
number in #0b1c30.

Below: a two-column row — left, a line chart titled "Leads Over Time" (30-day
trend) drawn in primary #3525cd; right, a horizontal bar chart titled "Lead
Source Breakdown" (Chatbot, AI Search, Requirement Form, Contact Form,
Walk-in). The two AI-driven sources (Chatbot, AI Search) use tertiary #571ac0
to mark the intelligence layer; the other three use primary #3525cd.

Below that: a "Recent Activity" feed as a borderless list — small icon,
one-line description in #0b1c30, timestamp in #464555. Rows separated by
vertical space with a subtle #eff4ff hover tint, not divider lines. E.g. "New
lead from AI Chatbot — 2 min ago", "Property #204 published — 1 hour ago".
```

---

## 7. Admin Portal — Property Management (List + Add Form)

**Purpose:** Core listing CRUD workflow.

**Key elements (from `01-prd.md` §10):**
- Data table with search/filter, status badges
- Bulk action toolbar
- Multi-step "Add Property" form

> ⚠️ **KNOWN DESIGN GAP — status chips are not properly distinguishable.** `DESIGN.md` defines no semantic status ramp (no success, no warning — only `error`). The four status chips below are fitted to existing tokens, which means **"Pending Approval" (`secondary-container` `#2170e4`) and "Published" (`primary-container` `#4f46e5`) are both blues and will read as near-identical at chip size.** These are the two statuses an agent most needs to tell apart at a glance. The prompt is usable, but **add a semantic status ramp to `DESIGN.md` before this screen is built for real.**

**Stitch prompt:**

```
Design two connected admin screens for PropVista CRM's admin portal, same
sidebar and layout style as the dashboard.

Screen 1 — Property list: a data table inside a #ffffff bento container.
Columns: Photo (rounded thumbnail), Title, Type, Price (24px semibold
#0b1c30), Status, Agent, Actions (edit/delete icons). Status uses fully-
rounded low-contrast chips:
  - Draft            → #dce9ff fill, #464555 text
  - Pending Approval → #2170e4 fill, white text
  - Published        → #4f46e5 fill, white text
  - Sold             → #213145 fill, #eaf1ff text
Avoid heavy row borders — separate rows with spacing and a subtle #eff4ff
hover tint.

Above the table: a search input (12px radius, #eff4ff fill), a filter
dropdown, and an "Add Property" button top-right (56px tall, gradient from
primary #3525cd to secondary #0058be, white text). When rows are checked, a
bulk-action toolbar appears above the table with "Approve Selected", "Feature
Selected", "Archive Selected".

Screen 2 — Add Property form: a multi-step form in a centered #ffffff bento
card (32px padding, 24px radius) with a horizontal step indicator across the
top (Basic Info, Media, Pricing, Amenities, Location) — the current step in
primary #3525cd, completed steps with a check.

Current step "Basic Info" shows fields with #eff4ff fill, 16px text, 16px
vertical padding, 12px radius, and a border that appears only on focus with a
2px primary #3525cd focus ring: Title, Description (textarea), Property Type
(dropdown), Listing Type (Buy/Rent segmented toggle), Bedrooms/Bathrooms
(number steppers).

Bottom of the card: a "Save as Draft" text button (left, #464555) and a "Next"
button (right, primary-to-secondary gradient, white text).

Note: use NO tertiary violet anywhere on either screen — nothing here is
AI-generated.
```

---

## 8. Admin Portal — Lead Pipeline (Kanban)

**Purpose:** Core CRM view for managing leads through stages.

**Key elements (from `01-prd.md` §11):**
- Kanban board across pipeline stages
- Lead cards with key info
- Side panel on click: notes, activity timeline, reminders

**Stitch prompt:**

```
Design a lead pipeline Kanban board for PropVista CRM's admin portal, same
sidebar and layout style as the dashboard.

Layout: five columns across the main content area — "New", "Contacted", "Site
Visit Scheduled", "Negotiation", "Closed". Each column header shows the stage
name at 14px semibold #0b1c30 and a count badge in a fully-rounded #e5eeff
chip. Columns sit on the #f8f9ff canvas with 24px gutters.

Each column holds 2-3 lead cards: a compact #ffffff card, 12px radius, 20px
padding, 1px #c7c4d8 border — customer name at 14px semibold #0b1c30, a small
fully-rounded source chip ("Chatbot", "AI Search", "Requirement Form"), the
property they're interested in (one line, truncated) in #464555, the assigned
agent's small round avatar, and a relative timestamp ("2h ago") at 12px in
#464555.

Leads that originated from an AI surface (Chatbot, AI Search) carry a
tertiary-tinted source chip — #e9ddff fill with tertiary #571ac0 text. The
non-AI sources (Requirement Form, Contact Form, Walk-in) use a neutral #e5eeff
chip with #464555 text. This is the only tertiary on the board.

Show one card mid-drag between "Contacted" and "Site Visit Scheduled" with a
subtle lift — the ultra-soft shadow 0 10px 30px rgba(11,28,48,0.04) and a
slight scale-up — to indicate drag state.

On the right edge, a slide-in detail panel (as if a card was clicked):
glassmorphic backdrop (20px blur, rgba(255,255,255,0.7)), 32px padding, 24px
radius on the leading edge. Top — customer contact info. Then a vertical
activity timeline (thin #c7c4d8 line with dated entries, no heavy borders).
Then a notes textarea (#eff4ff fill, 12px radius). At the bottom, a "Set
follow-up reminder" date picker and a save button in primary #3525cd.
```

---

## 9. Tips for Using These in Stitch

- **Paste `DESIGN.md` first**, then the screen prompt. Every prompt above assumes the theme is already in context.
- **Run the screens in the order above** — Stitch stays more visually consistent within a session when later prompts can reference earlier screens ("match the style of the homepage I just generated").
- **If a result drifts off-brand**, re-paste `DESIGN.md` alongside the screen prompt rather than trying to correct it with a vague follow-up like "make it nicer."
- **Watch the `tertiary` discipline.** If Stitch paints a button, nav item, or non-AI chart series in tertiary violet, correct it explicitly — see §0.2.
- **Watch for mono/serif.** Stitch reaches for a monospace face on prices and numbers by default. There is no mono in this system; if it appears, say "all numerals in Plus Jakarta Sans."
- **Treat these as starting points** — Stitch output is a first draft; expect to iterate 1-2 rounds per screen on spacing and hierarchy before it's ready to hand to engineering as a visual reference.

---

**This is a supplementary doc** (not part of the core 00–10 engineering set) — reference it alongside `01-prd.md`'s wireframe notes when generating visuals, and keep both in sync if the PRD's UI requirements change. The design system itself is owned by [`DESIGN.md`](./DESIGN.md); never fork a copy of it into this file.
