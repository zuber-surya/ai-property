# Stitch Design Prompts — PropVista CRM

> **Doc 11 of the PropVista CRM documentation set.** Copy-paste-ready prompts for Google Stitch, covering the priority screen set across the public site and admin portal. Built from the wireframe notes in `01-prd.md` and the flows in `02`–`08`.
>
> **Status:** Draft v1.6 · **Last updated:** July 2026
>
> **All three surfaces are covered.**
> - **§§1–16** — per-screen prompts, one at a time, for iterating on a single screen.
> - **§17** — one single-paste prompt for the **entire public site** (11 screens: homepage, search, details, wizard, contact, auth, CMS, + the three AI features).
> - **§18** — one single-paste prompt for the **entire customer portal** (5 screens + favorites-session feature).
> - **§19** — one single-paste prompt for the **entire admin portal** (20 screens).
>
> Use a single-paste prompt to establish the world, then the per-screen prompts to iterate on whatever you're actually building.
>
> **Two things are still open and both prompts work around them:**
> 1. **`DESIGN.md` needs an `info` color.** Three lead stages, two property statuses, and three customer-facing inquiry statuses are all *in progress* — none of `success`/`warning`/`error`/`neutral` fits. Currently rendered `neutral` as a placeholder.
> 2. **Gap G5** — no public CMS read endpoint, so §11 can't be served. **Gap G9** — no email/SMS provider and no job scheduler, so §16 and §18's notification-rules screen can only offer in-app.

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
| **Status — success** | `success-container` | `#c3f0da` fill / `#00522f` text |
| **Status — warning** | `warning-container` | `#ffddb0` fill / `#2c1700` text |
| **Status — error** | `error-container` | `#ffdad6` fill / `#93000a` text |
| **Status — neutral** | `neutral-container` | `#e2e1ec` fill / `#1a1a24` text |

**Type:** Plus Jakarta Sans throughout — there is **no** mono and **no** serif face in this system. Prices use `headline-md` (24px / 600) in `on-surface`. Headings use `display-lg` (48px / 700) or `headline-lg` (30px / 600). Labels use `label-md` (14px / 600) or `label-sm` (12px / 500).

**Shape:** Cards `rounded.xl` (24px). Buttons and inputs `rounded.md` (12px). Chips and pills `rounded.full`. Large property imagery may go to 32px.

**Depth:** No heavy shadows. One ultra-soft shadow for floating/active elements: `0 10px 30px rgba(11,28,48,0.04)`. Glassmorphism = 20px backdrop blur + `rgba(255,255,255,0.7)` fill, used on nav bars and floating AI surfaces.

**Focus:** A focused input takes a 2px `primary` (`#3525cd`) ring — never tertiary. A focused field is a user action, not a model output.

**Containers:** ⚠️ The **accent** `*-container` tokens (`primary`, `secondary`, `tertiary`) are **saturated fills that take light text** — they invert Material 3. For a pale accent tint with dark text (selected chips, hover states) use `*-fixed` instead (`primary-fixed` `#e2dfff`, `tertiary-fixed` `#e9ddff`).
**The four *semantic* `*-container` tokens behave normally** — pale fill, dark text — because they follow the `error` convention. See `DESIGN.md` → Colors and → Semantic Status Colors.

**Status:** Never use `primary`, `secondary` or `tertiary` to mean a status. Status has its own ramp: `success` / `warning` / `error` / `neutral`.

### 0.2 The one rule Stitch gets wrong most often

**`tertiary` is a semantic color, not decoration.** It marks the AI intelligence layer — anything the model generated, predicted, matched, or suggested — and nothing else. `primary` is for high-intent user actions. If Stitch applies `tertiary` to a button, a nav item, or a chart series that isn't AI-derived, correct it explicitly. This distinction is the visual backbone of the product.

> ℹ️ **Note on the AI accent.** `DESIGN.md` once described the AI layer with a violet hex that had no matching token. That prose has since been reconciled: the AI layer **is** the **`tertiary`** family (`#571ac0` / `#6f3dd9` / `#e9ddff`), in both the tokens and the prose. Nothing to reconcile here any more — this note remains only so the history is legible.

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

**Key elements — quoted from `01-prd.md` §6 (Module 5), FR5.1–FR5.5:**
- FR5.1 Full image gallery, **floor plan**, amenities list, **price breakdown**, location map, **nearby landmarks**
- FR5.2 "Similar properties" recommendations (reuses the recommendation engine, Module 3)
- FR5.3 **Sticky CTA** for "Request Callback" / "Schedule Visit", visible while scrolling
- FR5.4 **Agent/builder contact info** displayed
- FR5.5 **EMI / affordability calculator** widget

> ✅ **Resolved 2026-07-13 — AI Insights dropped; prompt rewritten against FR5.1–FR5.5.**
>
> An earlier draft of this prompt rendered an **AI Insights** panel (fair-price estimate, appreciation forecast, rental yield, buy-vs-rent) that appeared in **no spec anywhere**. Price prediction is a materially different product claim from the three USP AI features, so it is **not built**. If it is ever wanted, it goes into `01-prd.md` Module 5 first — with a spec for where the numbers come from — before any pixel of it is drawn.
>
> **The one legitimately AI-generated thing on this page is "Similar Properties"** (FR5.2), which reuses the recommendation engine. It is therefore the only element that carries the `tertiary` treatment. Nothing else on this screen does.
>
> *(An earlier audit of mine also claimed a three-way layout conflict on the hero. That was wrong — I had read this doc's own stale summary instead of the PRD. FR5.3 asks only for a **sticky CTA**, and `DESIGN.md` permits imagery "left **or top**", so the stacked hero below is compliant.)*

**Stitch prompt:**

```
Design a property details page for PropVista CRM (match the style of the
homepage).

HERO — a large-inset image carousel, 4-5 photos, 32px radius, indicator dots
below, with a thumbnail strip beneath it. The photography is the protagonist;
give it the full width of the content column.

STICKY HEADER — directly beneath the hero, a glassmorphic bar (20px blur,
rgba(255,255,255,0.7)) that stays pinned while the page scrolls, showing
inline with space between: property type, a "For Sale" chip (#e5eeff fill),
the price at 48px bold in #0b1c30, and a neighbourhood/city chip. On the
right of this bar sit the two sticky CTAs — "Request Callback" (56px tall,
gradient from primary #3525cd to secondary #0058be, white text) and
"Schedule Visit" (56px tall, outlined, 1px #3525cd border, #3525cd text).
These two buttons must remain visible at all times while scrolling. On
mobile they drop to a fixed bar across the bottom of the viewport — pinned
above the content, never covering it.

MAIN COLUMN, in this order:

1. Overview — description paragraph, a features list with checkmark icons,
   and a construction-status chip.

2. Price breakdown — a bento card itemising the cost: base price, parking,
   maintenance/society charges, stamp duty, registration, and a bold total.
   Figures right-aligned in a column, 24px semibold #0b1c30, aligned on the
   digit so they read as a column of numbers.

3. Floor plan — a bento card holding the floor-plan drawing on a white
   surface with a zoom/expand affordance in the corner.

4. Amenities — an icon grid grouped under "Essentials", "Comfort", "Safety".

5. Location & nearby landmarks — an interactive map with the property pinned,
   beside a list of nearby landmarks grouped by category (Schools, Hospitals,
   Transit, Shopping), each row showing name and distance. Borderless list
   rows, separated by spacing and a #eff4ff hover tint.

6. EMI / affordability calculator — a bento card with three "Effortless
   Field" inputs (Loan amount, Interest rate, Tenure in years), each with a
   slider beneath it, and a large computed "Monthly EMI" figure at 48px bold
   in #0b1c30. A small "Apply for pre-approval" text link in primary #3525cd
   beneath it.

SIDEBAR (desktop) / BELOW THE FOLD (mobile) — an agent contact card: agent or
builder photo (round), name, agency, a verified badge, phone and email rows
with icons, and a "Contact Agent" button (outlined, primary #3525cd).

SIMILAR PROPERTIES — a horizontal scroll of smaller property cards at the
foot of the page. These come from the AI recommendation engine, so this
section — and ONLY this section — carries the AI treatment: a 1px gradient
border from primary #3525cd to tertiary #571ac0 on each card, and a section
heading with a small tertiary-tinted "Recommended for you" chip (#e9ddff
fill, #571ac0 text).

IMPORTANT — no tertiary violet anywhere else on this page. The price
breakdown, the EMI figures and the floor plan are ordinary data, not model
output, and must not be styled as AI.

ALSO — the page must survive partial data: show it with the floor plan
section absent, and the layout should close up cleanly with no gap or empty
frame.
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

> ✅ **Resolved 2026-07-13.** `DESIGN.md` now defines a semantic status ramp (`success` / `warning` / `error` / `neutral`), so the chips below no longer borrow from the blues. Pending Approval and Published previously sat at **1.35 : 1** against each other — effectively one color, on the two states an agent most needs to distinguish. They are now amber and green.

**Stitch prompt:**

```
Design two connected admin screens for PropVista CRM's admin portal, same
sidebar and layout style as the dashboard.

Screen 1 — Property list: a data table inside a #ffffff bento container.
Columns: Photo (rounded thumbnail), Title, Type, Price (24px semibold
#0b1c30), Status, Agent, Actions (edit/delete icons). Status uses fully-
rounded, low-contrast chips — pale fill with dark text of the same hue:
  - Draft            → #e2e1ec fill, #1a1a24 text   (neutral — inert)
  - Pending Approval → #ffddb0 fill, #2c1700 text   (warning — needs a human)
  - Published        → #c3f0da fill, #00522f text   (success — live)
  - Sold             → #213145 fill, #eaf1ff text   (dark, filled — terminal)
These four must be unmistakable from each other at a glance across a long
list. Avoid heavy row borders — separate rows with spacing and a subtle
#eff4ff hover tint.

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

---

# Part B — Customer Portal & Remaining Public Pages

> **Screens 9–16.** Written against `docs/16-customer-spec/`, each traced to its FR numbers. Screens 1–5 above cover the public browse/search/AI surface; these cover **auth, contact, CMS, and the five authenticated portal pages**.
>
> **The portal shell (§§12–16) is one component.** Design it once on screen 12 and reference it — "same portal shell as the dashboard" — on 13–16. It is not a separate product: per `02-architecture.md` §5.1 the portal is *an authenticated view of the public site*, so it keeps the same header and the same tokens.

---

## 9. Public Site — Register / Login

**Purpose:** Account creation, entered mostly as a modal *after* a persist-worthy action — never as a gate before one.

**Key elements (from `16-customer-spec/06-auth-register-login.md`, PRD Module 7):**
- Same shell renders as a **modal** (over the page) or a **full page** (`/login`, `/register`)
- **Contextual headline** that names the thing the user is about to keep
- Register: name, email, phone (optional), password + live strength meter
- Login: email, password, "Forgot password?"
- A modal signup **never navigates away** — it closes and the underlying page updates

**Stitch prompt:**

```
Design the register/login modal for PropVista CRM (match the style of the
homepage).

Layout: a centered modal card over a dimmed page — max-width 460px, #ffffff
surface, 32px padding, 24px radius, with the ultra-soft shadow
0 10px 30px rgba(11,28,48,0.04). A close (X) icon top-right. Behind it, the
page is dimmed with a #cbdbf5 scrim at low opacity.

Headline: "Save your favorites" at 30px semibold #0b1c30, with a subhead
beneath in 16px #464555: "Create an account to keep this — it takes 20
seconds." A 1px #c7c4d8 hairline under the subhead.

Fields — stacked, each with a VISIBLE LABEL above it (never a placeholder as
the label), 12px radius, #eff4ff fill, no border at rest, 2px primary #3525cd
ring on focus:
- Full name
- Email
- Phone (optional)  — the word "optional" in the label, in #464555
- Password, with an eye/reveal icon inside the right edge

Below the password: a password-strength meter — four small rounded segments,
the filled ones in primary #3525cd, with the label "Strong enough" at 12px in
#464555.

Primary button, full width: "Create account" — 56px tall, 12px radius,
gradient from primary #3525cd to secondary #0058be, white text.

Below: "Already have an account? Log in" — "Log in" as a primary #3525cd
text link. Then a hairline, then small 12px #464555 legal text: "By
continuing you agree to the Terms and Privacy Policy."

Include a second, smaller mockup beside it: the LOGIN variant of the same
shell — headline "Welcome back", just Email and Password, a "Forgot
password?" text link right-aligned under the password field, a "Log in"
primary button, and "New here? Create one".

No tertiary violet anywhere — signing in is not an AI action.
```

---

## 10. Public Site — Contact / Callback

**Purpose:** The non-property lead capture path, plus the tenant's real-world contact details.

**Key elements (from `16-customer-spec/05-contact-page.md`, PRD Module 6):**
- Two-column: contact form left, tenant contact info + map right
- Mode toggle: "Send a message" vs. **"Request a callback"** — the latter reveals a date + time-slot picker (FR6.2)
- Success **replaces the form in place** (FR6.3), it does not navigate away

> ⚠️ **`16-customer-spec/05-contact-page.md` §11: the tenant contact block has no data source.** Address, phone, hours and map have no table and no endpoint. Design it, but know it cannot be populated until that is specced.

**Stitch prompt:**

```
Design the contact page for PropVista CRM (match the style of the homepage).

Heading: "Talk to us" at 48px bold #0b1c30, with a subhead beneath at 18px
#464555: "We'll get back to you within one business day." Generous space
below before the content.

Two-column layout, 60/40, 24px gutter. On mobile it collapses to one column
with the form FIRST and the contact info below it.

LEFT — the contact form in a #ffffff bento card, 32px padding, 24px radius,
1px #c7c4d8 border. Fields with visible labels above them, #eff4ff fill, 12px
radius, 2px primary #3525cd focus ring:
- Name (required)
- Phone (required)
- Email
- Message (textarea, 4 rows)

Above the submit, a two-option radio group rendered as a segmented control:
"Send a message" (selected by default) and "Request a callback". When
"Request a callback" is chosen, a slot picker is revealed directly beneath it
inside a tinted #eff4ff inset panel — a Date dropdown and a Time-slot
dropdown side by side.

Show the callback option SELECTED, with the slot picker visible.

Submit: "Submit" button, 56px tall, gradient primary #3525cd → secondary
#0058be, white text, full width of the card.

RIGHT — the tenant contact card, #ffffff, 24px radius, 32px padding:
office address, phone, email — each as a row with a 1.5px line-style icon —
then opening hours ("Mon–Sat, 9:30–18:30") in #464555, then a map embed with
a 16px radius filling the bottom of the card.

Include a SECOND small mockup showing the success state: the form card is
replaced in place by a confirmation — a check icon in success #026e4f, the
heading "Thanks — we've got it", and "An agent will call you between 10am and
12pm on 14 July." The page does not navigate away.
```

---

## 11. Public Site — CMS Static Page

**Purpose:** About / Terms / Privacy / blog — the one place where the *content* is the page.

**Key elements (from `16-customer-spec/12-static-cms-pages.md`, PRD Module 14):**
- Title + rich-text body constrained to a readable measure (~65–75ch), **not** full-bleed
- A standard "back into the funnel" CTA band appended to every content page

> ⛔ **BLOCKED — Gap G5.** There is **no public endpoint that serves CMS pages.** Admin CRUD exists; no public read route. The module is inert and the page cannot be served. Fix `04-api-spec.md` first. The prompt is here so the design is ready when the endpoint is.

**Stitch prompt:**

```
Design a CMS content page for PropVista CRM (match the style of the homepage)
— the About page for a tenant called Sharma Estates.

This is the one page on the site where the content IS the page. Set the body
text in a single column constrained to a readable measure of about 68
characters, centered on the #f8f9ff canvas. Do not make it full-bleed and do
not put it in a card — let it sit on the canvas like a printed page.

Title: "About Sharma Estates" at 48px bold #0b1c30, with a 1px #c7c4d8
hairline rule beneath it.

Body: rich text at 18px / 1.6 line-height in #0b1c30 — two or three
paragraphs, a subheading at 30px semibold, a bulleted list, and one inset
image at a 24px radius spanning the measure. Links in primary #3525cd.
Generous 48px vertical rhythm between blocks.

At the foot of the content, a CTA band: a full-measure bento card, #ffffff,
24px radius, 32px padding, holding the line "Looking for a home?" at 24px
semibold and a "Browse properties →" button (56px, primary #3525cd →
secondary #0058be gradient, white text) to its right.

Standard site header and footer above and below.

No tertiary violet — nothing on this page is AI-generated.
```

---

## 12. Customer Portal — Dashboard

**Purpose:** The logged-in home. It answers exactly one question: *"what's happened since I was last here?"*

**Key elements (from `16-customer-spec/07-portal-dashboard.md`, FR7.1):**
- Left portal nav with **counts** — the counts are the point; they tell the user where to look
- "What's new" panel — the reason the page exists
- Saved properties (first 4), My requirements (summary + live match count), Recent inquiries (last 2–3)
- **The first-time empty state is the most common state on day one and must be designed, not defaulted**

**Stitch prompt:**

```
Design the customer portal dashboard for PropVista CRM (match the style of
the homepage — this is an authenticated view of the same site, not a separate
product, so it keeps the same header and tokens).

Top: the standard public-site glassmorphic header, but the right side now
shows a logged-in user chip — round avatar + "Priya ▾".

Left — PORTAL NAV, approx 220px, a #ffffff bento card with 16px radius:
five rows — Overview, Favorites, Requirements, Inquiries, Notifications.
Each row that has items shows a count in a small fully-rounded #e5eeff chip
on the right (Favorites 4, Inquiries 2, Notifications 3). The active row
(Overview) has an #e2dfff tint and primary #3525cd text. No borders between
rows — spacing and a #eff4ff hover tint only.
On mobile this collapses to a horizontal scrolling tab strip under the header.

Main column:

Greeting: "Welcome back, Priya." at 30px semibold #0b1c30.

WHAT'S NEW — a bento card at the top, the most prominent thing on the page.
Two rows, each with a small unread dot in primary #3525cd, a one-line
description, and a text link:
  ● 2 new homes match your requirements   → View matches
  ● An agent replied to your inquiry on Sunview Residences
Because the "new match" row is produced by the AI recommendation engine, give
that row a small tertiary-tinted chip (#e9ddff fill, #571ac0 text) reading
"AI match". The agent-reply row gets no tertiary — a human wrote it.

SAVED PROPERTIES — section heading at 24px semibold with a "See all →" text
link right-aligned in primary #3525cd. Below: a row of 4 compact property
cards (photo, price at 24px semibold, one line of specs) each with a filled
heart in the photo's top-right corner.

MY REQUIREMENTS — heading + "Edit →" link. Below, a single bento card holding
a plain-language summary — "3BHK apartment · ₹50–80L · Whitefield / Self-use ·
within 3 months" — and beneath it "6 current matches" with a "View →" link.
Write it in plain language, never raw values like "self_use".

RECENT INQUIRIES — heading + "See all →". Below, two compact rows: property
name, a status pill, and a relative timestamp ("2d ago"). Status pills use
the semantic ramp — "An agent is on it" and "Received".

Include a SECOND mockup showing the FIRST-TIME EMPTY STATE, which is what
most new accounts actually see: NOT three empty boxes. A single centered
bento card with a warm heading — "Let's find your home" — and two clear
choices: a primary button "Tell us what you're looking for →" (the
requirement wizard) and a secondary outlined button "Browse listings →".
```

---

## 13. Customer Portal — Favorites

**Purpose:** The shortlist. This is a **comparison surface**, not just a saved list — so the rows are larger and more considered than a browse grid.

**Key elements (from `16-customer-spec/08-portal-favorites.md`, FR7.1 / FR4.4):**
- Larger list rows, not a grid — price, specs, status badge, saved date
- Per-row: **Ask about this** (creates a lead) and **Remove**
- Unavailable properties stay in the list, greyed — **never silently deleted**
- The **empty state is seen more often than the populated one** and gets real design attention
- The post-registration "your favorites survived" banner closes the loop that got them to register

**Stitch prompt:**

```
Design the customer portal Favorites page for PropVista CRM — same portal
shell and nav as the dashboard, with "Favorites" active.

Header row: "Saved properties (4)" at 30px semibold #0b1c30, with a sort
dropdown right-aligned ("Recently saved", "Price ↑", "Price ↓").

Below: a vertical list of favorite ROWS — deliberately larger and more
considered than a browse grid card, because this is where a buyer decides.
Each row is a #ffffff bento card, 24px radius, 24px padding, 1px #c7c4d8
border, laid out horizontally:
  - a 4:3 thumbnail at 16px radius on the left
  - title at 24px semibold #0b1c30
  - price at 24px semibold, then "3BHK · 1,200 sqft" and the locality in
    #464555
  - a status pill from the semantic ramp — Published = #c3f0da fill with
    #00522f text
  - "Saved 3 days ago" at 12px in #464555
  - a filled heart icon top-right of the row
  - two actions at the foot of the row: "Ask about this" (primary #3525cd
    outlined button) and "Remove" (text button, #464555)

Show the SECOND row in the UNAVAILABLE state: the whole row is greyed back,
the status pill reads Sold (#213145 fill, #eaf1ff text), the price and specs
are muted, a line reads "No longer available", and the two actions are
replaced by a single "See similar" link. The row is still there — it is not
removed.

Include TWO more small mockups:

(a) THE EMPTY STATE — this is what most new accounts see, so give it real
attention. A centered bento card: a large outline heart icon, the line
"Nothing saved yet", the subline "Tap the ♥ on any listing to keep it here",
and a prominent "Browse properties" button (primary gradient).

(b) THE JUST-MIGRATED BANNER — a one-time confirmation strip above the list,
in a success tint (#c3f0da fill, #00522f text) with a check icon: "Your 2
saved properties are now in your account."

No tertiary violet on this page — a favorite is a human choice, not a model
output.
```

---

## 14. Customer Portal — My Requirements

**Purpose:** The saved requirement profile and its live AI match list. **The matches here are model output — this is the most tertiary-heavy screen in the customer surface.**

**Key elements (from `16-customer-spec/09-portal-requirements.md`, FR7.3 / FR3.4):**
- Profile summary in **plain language**, never raw enum values (`self_use` → "To live in")
- Edit (reopens the wizard pre-filled) / Delete
- Per-profile **alerts toggle** (FR3.4)
- Ranked matches with **✓/✗ reason lines** and a **NEW** flag on matches since last visit
- An honest "Updated 2d ago" — match counts can be stale and must not be presented as live

**Stitch prompt:**

```
Design the customer portal "My requirements" page for PropVista CRM — same
portal shell and nav as the dashboard, with "Requirements" active.

Heading: "My requirements" at 30px semibold #0b1c30.

PROFILE CARD — a #ffffff bento card, 24px radius, 32px padding, with "Edit"
and "Delete" text buttons top-right (Edit in primary #3525cd, Delete in
#464555). Inside, a label/value list in two columns, no dividers:
  Budget      ₹50L – ₹80L
  Location    Whitefield, Marathahalli
  Type        Apartment
  Purpose     To live in
  Timeline    Within 3 months
  Must-haves  Parking, Gym
Labels at 14px semibold #464555, values at 16px #0b1c30. Write everything in
plain language — never raw values like "self_use".

At the foot of the profile card, a tinted inset strip (#eff4ff) with a bell
icon: "Alerts on — we'll notify you when a new match is listed." and a "Turn
off" text link right-aligned.

MATCHES — heading "Your matches (6)" at 24px semibold, with "Updated 2 days
ago" right-aligned at 12px in #464555. Be honest about staleness; this is not
a live count.

Below: a vertical list of match rows. These come from the AI recommendation
engine, so EACH ROW gets the AI treatment — a 1px gradient border from
primary #3525cd to tertiary #571ac0 and a faint tertiary glow. Each row has:
  - thumbnail, title, price at 24px semibold, specs
  - a match-score badge — "92%" in a tertiary-tinted chip (#e9ddff fill,
    #571ac0 text)
  - a "NEW" flag on the first row (small, primary #3525cd) for matches found
    since the last visit
  - a reason line beneath, showing WHY it matched: a green check + "Budget",
    a green check + "Location", a muted ✗ + "No gym". Use success #026e4f for
    the checks and #464555 for the misses — these are facts about the match,
    not statuses.
  - an outline heart icon to favorite it

This is the most AI-dense screen in the customer surface. The tertiary
gradient borders and match badges belong here — but the profile card at the
top does NOT get them. The customer wrote that; the model didn't.
```

---

## 15. Customer Portal — My Inquiries

**Purpose:** What the customer asked about, and what's happened since. **The single most important thing on this screen is that the internal pipeline stage is never shown to the customer.**

**Key elements (from `16-customer-spec/10-portal-inquiries.md`, FR7.1):**
- The property, the customer's own message, when and how it was sent
- **A translated status pill** — never the raw `leads.stage` enum
- A timeline derived from `lead_activities`, heavily filtered
- Inquiries with no property (general contact form) render without a property block

**The stage translation is mandatory** (spec §5). It is written by and for agents and must never reach a customer:

| `leads.stage` (internal) | Shown to the customer |
|---|---|
| `new` | **Received** |
| `contacted` | **An agent is on it** |
| `site_visit_scheduled` | **Visit scheduled** |
| `negotiation` | **In discussion** — never the word "negotiation" |
| `closed_won` | **Completed** |
| `closed_lost` | **Closed** — never "Lost", and never say why |

> ⚠️ **OPEN — the semantic ramp has no "in progress" color.** `DESIGN.md` defines `success` / `warning` / `error` / `neutral`. Three of the six customer-facing statuses above ("An agent is on it", "Visit scheduled", "In discussion") are **in progress** — not done, not failed, not inert, and *not* a warning. None of the four fits. The prompt below uses `neutral` for them as an honest placeholder and flags it. **Resolve by adding an `info` family to `DESIGN.md`** (a hue distinct from `primary` indigo and `secondary` blue) before this screen is built.

> ⚠️ **"Send a follow-up" has no endpoint (Gap G8).** `POST /admin/leads/{id}/notes` is admin-only and must stay that way. Per spec §4, the button is **hidden for MVP**. The prompt omits it.

**Stitch prompt:**

```
Design the customer portal "My inquiries" page for PropVista CRM — same
portal shell and nav as the dashboard, with "Inquiries" active.

Heading: "My inquiries (2)" at 30px semibold #0b1c30.

Below: a vertical list of inquiry cards. Each is a #ffffff bento card, 24px
radius, 32px padding, 1px #c7c4d8 border.

FIRST CARD — expanded:
- A property block at the top: 4:3 thumbnail at 16px radius, title at 24px
  semibold, price at 24px semibold, "3BHK · Whitefield" in #464555
- A label/value block: "Status", "Sent", "Via" — with the status shown as a
  pill reading "An agent is on it" (neutral-container: #e2e1ec fill, #1a1a24
  text), then "12 Jul 2026" and "Property page"
- "Your message:" followed by the customer's own words in an inset tinted
  panel (#eff4ff, 12px radius, italic): "Is this available for a Nov move-in?"
- A TIMELINE: a thin vertical #c7c4d8 line with dated entries. Completed
  steps have a filled primary #3525cd dot; future steps have a hollow
  #c7c4d8 dot and muted #464555 text:
      ● 12 Jul   Inquiry received
      ● 13 Jul   Anjali picked this up
      ○          Site visit
- One action at the foot: "View property" (outlined, primary #3525cd).

SECOND CARD — collapsed: just the property name "Palm Grove Villa" and a
status pill reading "Received" (neutral-container #e2e1ec / #1a1a24), with a
relative timestamp.

Include TWO small mockups:

(a) AN INQUIRY WITH NO PROPERTY — from the general contact form. The card
renders with no property block at all; the customer's message IS the content.

(b) THE EMPTY STATE — "You haven't asked about anything yet." with a "Browse
properties" primary button.

Use the customer-facing status words exactly as written above. Never show an
internal pipeline stage name. No tertiary violet — an inquiry is a human
conversation, not model output.
```

---

## 16. Customer Portal — Notifications & Preferences

**Purpose:** What changed, and control over how much of it reaches you.

**Key elements (from `16-customer-spec/11-portal-notifications.md`, FR7.2):**
- Notification list, newest first — unread = a dot + bolder weight; **every row deep-links to its subject**
- "Mark all as read" — one click, no confirmation
- A preferences grid: event type × channel

> ⚠️ **Email and SMS cannot be delivered (Gap G9).** No email/SMS provider is chosen and there is **no job scheduler** — so the in-app channel is the only one that works. The prompt renders the Email and SMS columns **disabled with a "Coming soon" note** rather than offering switches that silently do nothing. Fix `10-deployment-devops.md` and `02-architecture.md` before enabling them.

> ⚠️ **Only `new_match` is an actual PRD requirement** (FR3.4). `inquiry_update`, `price_change` and `property_unavailable` are proposals in the spec and **must be added to `01-prd.md` before being built.** They are drawn below; do not read that as approval.

**Stitch prompt:**

```
Design the customer portal Notifications page for PropVista CRM — same portal
shell and nav as the dashboard, with "Notifications" active and showing an
unread count of 3.

Header row: "Notifications" at 30px semibold #0b1c30, with a "Mark all as
read" text button right-aligned in primary #3525cd.

NOTIFICATION LIST — borderless rows separated by spacing and a #eff4ff hover
tint, never divider lines. Each row is a link. Unread rows carry a small
filled dot in primary #3525cd at the left and slightly bolder text; read rows
have no dot and are set in #464555.

  ● 2 new homes match your requirements
    Sunview Residences + 1 more                              2h ago
  ● An agent replied to your inquiry
    Sunview Residences                                       1d ago
    Price dropped on a saved property
    Palm Grove Villa · ₹1.2Cr → ₹1.1Cr                       4d ago

The FIRST row is produced by the AI recommendation engine — give it a small
tertiary-tinted "AI match" chip (#e9ddff fill, #571ac0 text). The other two
are not AI output and get no tertiary.

PREFERENCES — below a 1px #c7c4d8 hairline and a "Preferences" heading at
24px semibold. A grid: rows are event types, columns are channels.

                        In-app     Email        SMS
  New matches            [on]      [disabled]  [disabled]
  Inquiry updates        [on]      [disabled]  [disabled]
  Price changes          [on]      [disabled]  [disabled]

The In-app toggles are live — rounded switches, filled primary #3525cd when
on. The Email and SMS columns are DISABLED and visibly so: greyed switches at
40% opacity, with a small note beneath the grid in #464555 reading "Email and
SMS notifications are coming soon." Do not render them as working switches —
they would silently do nothing.

A "Save preferences" button (primary gradient) at the foot.

Include a small mockup of the EMPTY STATE: "You're all caught up." with a
quiet check icon in #464555 — calm, not celebratory.
```

---

## 17. Single-Paste Prompt — The Entire Public Site

> **What this is.** One self-contained prompt covering **all 11 public-facing screens** (homepage, property search/details, requirement wizard, contact, auth, CMS pages, plus the three AI-powered features: search, chatbot, lead capture) in a single paste. Unlike §§1–16, it does **not** require pasting `DESIGN.md` first — a condensed token block is inlined so the whole thing works as one block of text.
>
> ⚠️ **This section is a generated artifact, not a source of truth.** The tokens below are *copied* from `DESIGN.md`. **If `DESIGN.md` changes, regenerate this section** — do not edit the tokens here.
>
> **Honest trade-off:** one prompt across 11 screens gets you a coherent *system* fast, but shallower output *per screen* than the individual prompts in §§1–11. Use this to establish the world, then use the per-screen prompts to iterate on whichever screen matters.

**Stitch prompt:**

```
Design the complete public-facing surface for PropVista CRM — a real
estate platform that visitors can browse and search without logging in. 11 screens, one consistent design system. Read the system first, then build every screen in it.

═══════════════════════════════════════════════════════════════
PART 1 — THE DESIGN SYSTEM (applies to every screen)
═══════════════════════════════════════════════════════════════

CONCEPT: "Effortless Intelligence." Soft Minimalism with glassmorphic
accents. Calm, spacious, premium — a concierge, not a database. Bento-box
layouts: content in rounded white containers on a soft canvas. Generous
negative space. Property photography is the protagonist.
  Canvas / page background      #f8f9ff
  Card surface                  #ffffff
  Input fill                    #eff4ff
  Chip fill (tags)              #e5eeff
  Hairline border               #c7c4d8
  Primary text                  #0b1c30   (deep slate, never black)
  Secondary text                #464555
  PRIMARY — high-intent actions #3525cd   (buttons, focus rings, links)
  Button gradient               #3525cd → #0058be
  Primary tint (selected)       #e2dfff
  TERTIARY — the AI layer       #571ac0   (tint #e9ddff)
  Dark / terminal               #213145   (text on it: #eaf1ff)
  Status: success               #c3f0da fill / #00522f text
  Status: warning               #ffddb0 fill / #2c1700 text
  Status: error                 #ffdad6 fill / #93000a text
  Status: neutral               #e2e1ec fill / #1a1a24 text

THE ONE RULE THAT MATTERS MOST:
  #571ac0 tertiary violet marks AI-GENERATED OUTPUT AND NOTHING ELSE —
  the chatbot, AI search results, requirement-wizard recommendations,
  match scores, "similar properties". It is a semantic color, not a
  decorative one. A focus ring, a favorite heart, a nav item, or a "Just
  Listed" tag is NOT tertiary. Focus rings are PRIMARY #3525cd.

TYPE: Plus Jakarta Sans throughout. THERE IS NO MONOSPACE AND NO SERIF —
  prices and all numerals are Plus Jakarta Sans like everything else.
  Display 48px/700  ·  Heading 30px/600  ·  Price & subhead 24px/600
  Body 16-18px/400/1.6  ·  Label 14px/600  ·  Caption 12px/500
  Headlines get tight letter-spacing; body gets 1.6 line-height.

SHAPE: Cards 24px radius. Buttons and inputs 12px. Chips and pills fully
  rounded. Large property imagery up to 32px. Nothing sharp, anywhere.

SPACE: 12-column grid, 24px gutters, max-width 1440px. 8px base rhythm.
  Card padding 24-32px. 40px desktop margins (20px mobile). Be generous —
  cramping is the failure mode.

DEPTH: No heavy shadows. One ultra-soft shadow for floating/active
  elements: 0 10px 30px rgba(11,28,48,0.04). Glassmorphism (20px backdrop
  blur + rgba(255,255,255,0.7) fill) on nav bars and AI surfaces only.
  Borders are 1px #c7c4d8 hairlines, used only where necessary.

COMPONENTS:
  Buttons — 56px tall, 12px radius. Primary = #3525cd→#0058be gradient,
    white text. Secondary = outlined, 1px #3525cd border, #3525cd text.
    Text button = #464555, no border.
  Inputs ("Effortless Fields") — 16px text, 16px vertical padding, #eff4ff
    fill, NO border at rest, 2px #3525cd ring on focus. Every field has a
    VISIBLE LABEL above it — never a placeholder as the label.
  Bento card — #ffffff, 24px radius, 24-32px padding, 1px #c7c4d8 border.
  AI widget — distinct from a card: 1px gradient border #3525cd → #571ac0
    plus a faint tertiary glow. Used ONLY for model output.
  Lists — no dividers between rows. Vertical spacing + a #eff4ff hover tint.
  Icons — line style, 1.5px stroke. Not filled, not playful.

═══════════════════════════════════════════════════════════════
PART 2 — SHARED FURNITURE (build once, reuse on every screen)
═══════════════════════════════════════════════════════════════

HEADER (every screen): glassmorphic bar — logo left; links (Buy, Rent,
  Requirement Analysis, Contact) center; right side shows either "Sign In" +
  a primary "Register" button (logged out) OR a round avatar + "Priya ▾"
  (logged in).

FOOTER (public screens): quiet, multi-column — links, tenant contact,
  legal. Muted #464555 on the canvas.

CHAT LAUNCHER (every public screen): a floating circular button, fixed
  bottom-right, glassmorphic with a soft tertiary #571ac0 glow ring —
  because it is the AI entry point. Touch target at least 44x44px.

PROPERTY CARD (used on 5 screens): bento card holding a 16:9 photo (32px
  radius) with a heart icon top-right of the photo; below it the price at
  24px semibold #0b1c30, then beds/area, then locality in #464555.
  When a card came from AI search or recommendation it ALSO gets a match
  badge — "AI match: 92%" in a tertiary chip (#e9ddff fill, #571ac0 text).

PORTAL SHELL (screens 8-12): the same header, plus a left nav card
  (~220px, #ffffff, 16px radius) with five rows — Overview, Favorites,
  Requirements, Inquiries, Notifications — each showing a COUNT in a small
  #e5eeff chip. The counts are the point: they tell the user where to look.
  Active row = #e2dfff tint + #3525cd text. On mobile the nav collapses to
  a horizontal scrolling tab strip under the header.

═══════════════════════════════════════════════════════════════
PART 3 — THE 12 SCREENS
═══════════════════════════════════════════════════════════════

── PUBLIC ──────────────────────────────────────────────────────

SCREEN 1 — HOMEPAGE (/)
Hero: a large natural-language search bar, 56px tall, centered, with the AI
widget treatment (gradient border + violet glow) because it is AI-powered.
Placeholder: "Try: 3BHK under 80 lakhs near tech park". A mic icon inside
the right edge. Below it, pill quick-filter chips: Buy, Rent, Property
Type, Budget, Location. Below the hero: "Featured Properties" — a 3-column
grid of 6 property cards. Then a CTA band: "Not sure where to start?" with
a "Find your match →" button to the wizard.

SCREEN 2 — SEARCH RESULTS (/search)
Left filter rail (260px): Price Range slider, Property Type checkboxes,
Bedrooms pill buttons, Amenities list, "Clear filters" link. Main area:
"128 properties found", a sort dropdown, and a Grid/List/Map segmented
toggle. Below: a 3-column grid of property cards. When the results came
from an AI query, show a row of removable PARSED-QUERY CHIPS above the grid
in tertiary tint (#e9ddff / #571ac0) — "3 BHK", "under ₹80L", "near tech
park" — each with an ×, showing how the AI understood the sentence. Those
chips and the match badges are the only tertiary on this screen.

SCREEN 3 — PROPERTY DETAILS (/property/:id)
Large-inset image carousel (32px radius, indicator dots, thumbnail strip).
Beneath it a STICKY glassmorphic bar that stays pinned while scrolling:
property type, a "For Sale" chip, the price at 48px bold, a locality chip,
and on the right two persistent CTAs — "Request Callback" (primary
gradient) and "Schedule Visit" (outlined). On mobile these drop to a fixed
bottom bar that sits ABOVE content, never covering it.
Main column, in order: Overview (description, feature list with check
icons, construction-status chip) · Price breakdown (a card itemising base
price, parking, maintenance, stamp duty, registration, and a bold total,
figures right-aligned in a column) · Floor plan (a card with a zoom
affordance) · Amenities (icon grid grouped Essentials / Comfort / Safety) ·
Location (map with the property pinned, beside a list of nearby landmarks
grouped by Schools / Hospitals / Transit / Shopping, each with a distance).
· EMI calculator (a card with three fields — Loan amount, Interest rate,
Tenure — each with a slider, and a large computed "Monthly EMI" at 48px).
Sidebar: an agent contact card — round photo, name, agency, verified badge,
phone and email rows, "Contact Agent" outlined button.
Foot: "Similar Properties" — a horizontal scroll of smaller cards. These
come from the recommendation engine, so THIS SECTION ONLY gets the AI
treatment (gradient border, tertiary "Recommended for you" chip). The price
breakdown and the EMI figures are ordinary data — do NOT style them as AI.
The page must survive partial data: show it once with the floor plan absent
and the layout closing cleanly.

SCREEN 4 — REQUIREMENT WIZARD (/requirement-analysis)
A centered bento card, max 600px, on the quiet canvas. A thin progress bar
(step 2 of 5, filled #3525cd) and a "Step 2 of 5" label. Heading "What's
your budget?" at 30px semibold. A row of large tappable option cards —
"Under 50L", "50L–80L", "80L–1.2Cr", "1.2Cr+" — the selected one with a 2px
#3525cd border and #e2dfff tint. "Back" text button left, "Next" primary
button right.
Second mockup — THE RESULTS STEP: heading "Your matches", then a carousel
of 3 property cards. These ARE model output, so each gets the full AI
widget treatment plus a reason line beneath the price showing WHY it
matched: a green check + "Within your budget", a green check + "Whitefield",
a muted ✗ + "No gym".

SCREEN 5 — CONTACT (/contact)
"Talk to us" at 48px bold, subhead "We'll get back to you within one
business day." Two columns, 60/40. Left: a form card — Name (required),
Phone (required), Email, Message textarea. Above the submit, a segmented
control: "Send a message" / "Request a callback". Show the CALLBACK option
selected, revealing a Date + Time-slot picker in a tinted #eff4ff inset
panel. Right: a tenant contact card — address, phone, email (each with a
line icon), opening hours, and a map at the foot.
Second mockup — the SUCCESS state: the form is replaced IN PLACE by a
confirmation with a check icon in #026e4f: "Thanks — we've got it. An agent
will call you between 10am and 12pm on 14 July." It does not navigate away.

SCREEN 6 — REGISTER / LOGIN (modal)
A centered modal, max 460px, over a dimmed page. Contextual headline "Save
your favorites" with subhead "Create an account to keep this — it takes 20
seconds." Fields with visible labels: Full name, Email, Phone (optional),
Password with a reveal icon. Below the password, a 4-segment strength meter
filled in #3525cd with the label "Strong enough". Full-width "Create
account" primary button. "Already have an account? Log in". Small legal line
at the foot.
Second, smaller mockup — the LOGIN variant: headline "Welcome back", Email +
Password, a "Forgot password?" link, "Log in" button, "New here? Create one".

SCREEN 7 — CMS CONTENT PAGE (/:slug)
The one page where the CONTENT is the page. A single column constrained to
a readable measure (~68 characters), centered on the canvas — NOT in a card,
NOT full-bleed. Title "About Sharma Estates" at 48px bold with a hairline
rule beneath. Body at 18px / 1.6: paragraphs, a subheading, a bulleted list,
one inset image at 24px radius. Links in #3525cd. At the foot, a CTA band
card: "Looking for a home?" with a "Browse properties →" primary button.
No tertiary anywhere on this screen.

── THE AI CHATBOT (overlays every public screen) ───────────────

SCREEN 8 — CHAT WIDGET (expanded)
A 380px panel anchored bottom-right, floating over the page. It is an AI
surface, so it gets the full treatment: glassmorphic fill, 1px #3525cd →
#571ac0 gradient border, faint tertiary glow, 24px radius.
Header: "PropVista Assistant", an online status dot, a close ×.
Thread (no dividers, just spacing):
  · Assistant, left, #eff4ff bubble: "Hi! Looking for a home? Tell me what
    you need."
  · User, right, #3525cd fill with white text: "3BHK under 80 lakhs near
    tech park"
  · Assistant, with a small embedded property card (thumbnail, price,
    one-line address) carrying a tertiary accent
  · A typing indicator — three dots
Below: 3 quick-reply pills — "Schedule a visit", "See similar properties",
"Talk to an agent". Footer: an input with a #3525cd send icon, and a
persistent "Talk to an agent" text link above it.

═══════════════════════════════════════════════════════════════
FINAL CHECKS — the three things most likely to go wrong
═══════════════════════════════════════════════════════════════
1. TERTIARY VIOLET #571ac0 appears ONLY on AI output: the chat widget, AI
   search parsed-query chips and match badges, wizard results, "similar
   properties", and the embedded cards within chatbot messages. NOWHERE
   ELSE. Not on focus rings, not on nav, not on hearts, not on buttons.
2. NO MONOSPACE AND NO SERIF. Every price and every numeral is Plus Jakarta
   Sans.
3. EMPTY STATES ARE DESIGNED, NOT DEFAULTED. The empty result after a
   search, the empty chatbot window, and the "no match" requirement wizard
   results all deserve real design attention.
```

---

## 18. Single-Paste Prompt — The Entire Customer Portal

> **What this is.** One self-contained prompt covering **all 5 customer portal pages** (dashboard, favorites, requirements, inquiries, notifications) plus the favorites-session feature in a single paste. Same structure as §17: a condensed token block is inlined so it works as a single block of text.
>
> ⚠️ **Generated artifact — regenerate from `DESIGN.md` if the design changes.** Do not edit the tokens here.
>
> **Honest trade-off:** one prompt across 5 portal screens gets you a coherent system fast, but shallower output *per screen* than the individual prompts in §§12–16. Use this to establish the world, then use the per-screen prompts to iterate on whichever screen matters.

**Stitch prompt:**

```
Design the customer portal surface for PropVista CRM — the authenticated part of the public site where registered customers manage their favorites, requirements, and inquiries. 5 screens, one consistent design system. 

THE PORTAL SHARES THE SAME DESIGN SYSTEM as the public site (see §17). This is not a separate product — it's an authenticated view of the same site, so it keeps the same header, the same tokens, and the same family of components. The difference is purely in layout and data shown. Copy-paste DESIGN.md first, then this prompt.

═══════════════════════════════════════════════════════════════
PART 1 — SHARED FURNITURE (reuse from the public site)
═══════════════════════════════════════════════════════════════

HEADER (every portal screen): glassmorphic bar (same as public site) — logo
left; links (Buy, Rent, Requirement Analysis, Contact) center; right side
shows a logged-in user chip — round avatar + "Priya ▾" (not "Sign In" any
more).

PORTAL SHELL (every screen): a two-column layout. LEFT: a fixed nav card
(~220px, #ffffff, 16px radius) with five rows — Overview, Favorites,
Requirements, Inquiries, Notifications. Each row that has items shows a count
chip on the right in #e5eeff (Favorites 4, Inquiries 2, Notifications 3).
The active row carries an #e2dfff tint and #3525cd text. On mobile this
collapses to a horizontal scrolling tab strip under the header. RIGHT: the
main content column.

PROPERTY CARD (reused throughout): a bento card holding a 16:9 photo (32px
radius) with a heart icon top-right; below it the price at 24px semibold
#0b1c30, then beds/area, then locality in #464555.

═══════════════════════════════════════════════════════════════
PART 2 — THE 5 PORTAL SCREENS
═══════════════════════════════════════════════════════════════

── THE AUTHENTICATED PORTAL ────────────────────────────────────

SCREEN 1 — PORTAL DASHBOARD (/portal)
Greeting "Welcome back, Priya." at 30px semibold.
WHAT'S NEW — the most prominent card on the page. Two rows, each with an
unread dot in primary #3525cd: "2 new homes match your requirements → View
matches" and "An agent replied to your inquiry on Sunview Residences". The
FIRST row is recommendation-engine output, so it gets a small tertiary "AI
match" chip (#e9ddff / #571ac0). The second does NOT — a human wrote it.
SAVED PROPERTIES — heading + "See all →", then 4 compact property cards.
MY REQUIREMENTS — heading + "Edit →", then one card with a plain-language
summary: "3BHK apartment · ₹50–80L · Whitefield / Self-use · within 3
months", and "6 current matches → View". Plain language ALWAYS — never raw
values like "self_use".
RECENT INQUIRIES — heading + "See all →", then two rows: property name, a
status pill, a relative timestamp.
Second mockup — THE FIRST-TIME EMPTY STATE, which most new accounts see
on day one. NOT three empty boxes. One centered card: "Let's find your
home", a primary "Tell us what you're looking for →" button and an outlined
"Browse listings →" button. This state is seen more often than the
populated one, so give it real design attention.

SCREEN 2 — PORTAL FAVORITES (/portal/favorites)
"Saved properties (4)" + a sort dropdown. Below, a vertical list of large
favorite ROWS — deliberately bigger than a browse card, because this is
where a buyer decides. Each row: 4:3 thumbnail left, title, price 24px
semibold, specs, a status pill, "Saved 3 days ago", a filled heart, and
two actions — "Ask about this" (outlined) and "Remove" (text).
Show the SECOND row UNAVAILABLE: greyed back, status "Sold" (#213145 /
#eaf1ff), the line "No longer available", actions replaced by a single "See
similar". The row STAYS in the list — never silently deleted.
Two more mockups: (a) THE EMPTY STATE — a large outline heart, "Nothing
saved yet", "Tap the ♥ on any listing to keep it here", and a "Browse
properties" primary button. (b) A success banner: check icon in success
#026e4f: "Your 2 saved properties are now in your account."

SCREEN 3 — PORTAL REQUIREMENTS (/portal/requirements)
Heading "My requirements".
PROFILE CARD — "Edit" and "Delete" top-right. A two-column label/value list,
no dividers: Budget ₹50L–₹80L · Location Whitefield, Marathahalli · Type
Apartment · Purpose To live in · Timeline Within 3 months · Must-haves
Parking, Gym. Plain language. At the card's foot, a tinted #eff4ff strip
with a bell icon: "Alerts on — we'll notify you when a new match is listed."
+ a "Turn off" link.
MATCHES — "Your matches (6)" with "Updated 2 days ago" right-aligned. Be
honest about staleness; it's not a live count.
Below: match rows. These ARE recommendation-engine output, so EVERY ROW gets
the AI widget treatment — 1px gradient border #3525cd → #571ac0, faint
tertiary glow — plus a "92%" score chip in tertiary tint (#e9ddff / #571ac0),
a "NEW" flag on the first row, and reason lines (green check "Budget", green
check "Location", muted ✗ "No gym"). The profile card at the top does NOT
get the AI treatment — the customer wrote it; the model didn't.

SCREEN 4 — PORTAL INQUIRIES (/portal/inquiries)
Heading "My inquiries (2)".
First card, expanded: property block (thumbnail, title, price, specs); then
Status / Sent / Via with the status as a pill reading "An agent is on it";
then "Your message:" with the customer's words in a tinted #eff4ff inset
panel; then a TIMELINE — thin vertical line with dated entries, completed
steps as filled #3525cd dots, future steps as hollow #c7c4d8 dots: "12 Jul
Inquiry received" / "13 Jul Anjali picked this up" / "○ Site visit". One
action: "View property" (outlined).
Second card, collapsed: "Palm Grove Villa" + "Received" pill.
CRITICAL: never show an internal pipeline stage. The customer sees only:
Received · An agent is on it · Visit scheduled · In discussion · Completed ·
Closed. Never "negotiation" or "lost".
Two more mockups: an inquiry with NO property (from the contact form — the
message IS the content), and the empty state.
No tertiary on this screen — an inquiry is a human conversation.

SCREEN 5 — PORTAL NOTIFICATIONS (/portal/notifications)
"Notifications" + a "Mark all as read" link. A borderless list — unread rows
carry a filled #3525cd dot and bolder text; read rows muted. Every row links:
  ● 2 new homes match your requirements — Sunview Residences + 1 more — 2h
  ● An agent replied to your inquiry — Sunview Residences — 1d
    Price dropped on a saved property — Palm Grove Villa ₹1.2Cr → ₹1.1Cr — 4d
The FIRST row is recommendation output — give it a tertiary "AI match" chip.
The others get none.
PREFERENCES — below a hairline: a grid, rows are event types, columns are
channels (In-app / Email / SMS). In-app toggles are live, filled #3525cd when
on. EMAIL AND SMS COLUMNS ARE DISABLED — greyed at 40% opacity with a note:
"Email and SMS notifications are coming soon." Do not draw them as working
switches.
Empty state: "You're all caught up." — calm, not celebratory.

═══════════════════════════════════════════════════════════════
FINAL CHECKS — the three things most likely to go wrong
═══════════════════════════════════════════════════════════════
1. TERTIARY VIOLET #571ac0 appears ONLY on AI-generated output: the "AI
   match" chips in the dashboard and notifications, the recommendation
   match cards on the requirements screen, and the match-score badges.
   NOWHERE ELSE. Not on status pills, not on the favorite heart, not on
   buttons.
2. NO MONOSPACE AND NO SERIF. Every price and every figure is Plus Jakarta
   Sans.
3. LANGUAGE: use plain language always. "To live in" not "self_use",
   "In discussion" not "negotiation". Never show internal pipeline stage
   names to the customer.
```

---

## 19. Single-Paste Prompt — The Entire Admin Portal

> **What this is.** One self-contained prompt covering **all 20 buildable admin screens** in `docs/17-admin-spec/`. Same structure as §17 and §18: a condensed token block is inlined so it works as a single paste.
>
> ⚠️ **Generated artifact — regenerate from `DESIGN.md` if the design changes.** Do not edit the tokens here.
>
> **Screen 20 (`20-tenant-branding.md`) is excluded** — it is 🕓 post-MVP (PRD FR16.2). There is no theming layer for it to configure.
>
> ⚠️ **TWO OPEN GAPS THIS PROMPT WORKS AROUND — read before you paste:**
>
> **1. The status ramp is short by one color, and it now bites in three places.** `DESIGN.md` defines `success` / `warning` / `error` / `neutral`. That covers a listing's Draft / Pending / Published / Sold. It does **not** cover:
> - **Lead stages** — `contacted`, `site_visit_scheduled` and `negotiation` are *in progress*: not done, not failed, not inert, and **not a warning**. On the Kanban board, the table, and the customer's Inquiries page.
> - **Property `on_hold` and `archived`** — the enum has **six** states (`06-property-approvals-status.md` §2.1), and `DESIGN.md`'s canonical mapping only names five.
>
> The prompt below uses `neutral` for all of them as an honest placeholder. **Add an `info` family to `DESIGN.md`** — a hue distinct from `primary` indigo and `secondary` blue — and the Kanban, the leads table, the agent profile and the customer Inquiries page all get correct at once.
>
> **2. Email and SMS have no provider, and there is no job scheduler** (Gap G9). This guts two screens: the **notification rules** (§19 below) can't deliver on the channels it offers, and the "lead sits in New for 48h" rule needs a scheduler that doesn't exist. The prompt renders those channels disabled rather than as switches that silently do nothing.

**Stitch prompt:**

```
Design the complete admin portal for PropVista CRM — a multi-tenant real
estate CRM used by agents, admins and platform super-admins. 20 screens, one
consistent design system.

This is a TOOL, not a storefront. It shares the design system with the public
site but is COMPACTER and DENSER: 24px card padding rather than 32px, tighter
rows, less decorative. Agents live in this thing for eight hours a day.
Desktop-first — a Kanban board is not a mobile experience.

It carries the PROPVISTA brand, never a tenant's. It is not tenant-branded.

═══════════════════════════════════════════════════════════════
PART 1 — THE DESIGN SYSTEM
═══════════════════════════════════════════════════════════════

CONCEPT: "Effortless Intelligence." Soft Minimalism. Bento-box layouts —
content in rounded white containers on a soft canvas. Calm and spacious even
when dense: no heavy borders, no muddy shadows, no cramped tables.

COLOR — use these exact values, no others:
  Canvas / page background      #f8f9ff
  Card surface                  #ffffff
  Input fill                    #eff4ff
  Chip fill (neutral tags)      #e5eeff
  Hairline border               #c7c4d8
  Primary text                  #0b1c30
  Secondary text                #464555
  PRIMARY — high-intent actions #3525cd   (buttons, focus rings, active nav)
  Button gradient               #3525cd → #0058be
  Primary tint (selected/hover) #e2dfff
  TERTIARY — the AI layer       #571ac0   (tint #e9ddff)
  Dark / terminal               #213145   (text on it: #eaf1ff)
  STATUS success (live, won)    #c3f0da fill / #00522f text
  STATUS warning (needs a human)#ffddb0 fill / #2c1700 text
  STATUS error (failed, urgent) #ffdad6 fill / #93000a text
  STATUS neutral (inert)        #e2e1ec fill / #1a1a24 text

THE ONE RULE THAT MATTERS MOST:
  #571ac0 tertiary violet marks AI-GENERATED OUTPUT AND NOTHING ELSE. In this
  portal that means exactly: the AI-derived lead sources (Chatbot, AI Search),
  the AI-source bars in the dashboard chart, the bot's messages and tool calls
  in a chat transcript, the recommendation-weight preview, and the search-
  insights panels. NOTHING ELSE. Not the nav. Not focus rings (those are
  PRIMARY #3525cd). Not status badges. Not buttons. Not chart series that
  aren't AI-derived.

STATUS IS NOT BRAND: never use primary, secondary or tertiary to mean a
  status. Status uses the four status colors above, and always carries a TEXT
  LABEL as well as a color.

TYPE: Plus Jakarta Sans throughout. THERE IS NO MONOSPACE AND NO SERIF —
  every price, metric, percentage and table figure is Plus Jakarta Sans.
  Page heading 30px/600 · Section 24px/600 · Metrics 30px/600
  Body 16px/400 · Table cells & labels 14px/600 · Caption 12px/500
  Numbers in a column align on the digit so they read as a column.

SHAPE: Cards 24px radius. Buttons, inputs, table containers 12px. Chips and
  pills fully rounded. Nothing sharp.

DEPTH: One ultra-soft shadow for floating elements: 0 10px 30px
  rgba(11,28,48,0.04). 1px #c7c4d8 hairlines only where necessary.
  Glassmorphism (20px blur + rgba(255,255,255,0.7)) on slide-in panels.

COMPONENTS:
  Buttons — 48-56px. Primary = #3525cd→#0058be gradient, white text.
    Secondary = outlined 1px #3525cd. Text = #464555. Destructive = #ba1a1a.
  Inputs — #eff4ff fill, 12px radius, NO border at rest, 2px #3525cd ring on
    focus. Every field has a VISIBLE LABEL — never a placeholder as a label.
  Tables — the workhorse. NO heavy row borders and NO zebra striping. Separate
    rows with vertical space and a #eff4ff hover tint. Sticky header row.
    Right-align all numbers.
  Lists — no dividers. Spacing + hover tint.
  Icons — line style, 1.5px stroke.

═══════════════════════════════════════════════════════════════
PART 2 — SHARED FURNITURE (build once, reuse everywhere)
═══════════════════════════════════════════════════════════════

SIDEBAR (every screen except login): a fixed left rail, ~240px. PropVista
  logo at top, the tenant's business name beneath it in 12px #464555 (a
  label, not a brand). Then nav rows with line icons: Dashboard, Properties,
  Leads, Agents, Users, AI Config, Content, Reports, Settings.
  RULE: the nav must reach EVERY module in one click from anywhere — admins
  jump around, they don't follow a sequence. Active row = #e2dfff tint with
  #3525cd text and icon. Collapses to icon-only on tablet.

STATUS CHIPS — fully rounded, pale fill with dark text of the same hue, and
  ALWAYS a text label:
    Property:  Draft #e2e1ec/#1a1a24 · Pending Approval #ffddb0/#2c1700 ·
               Published #c3f0da/#00522f · Sold #213145/#eaf1ff ·
               Rejected #ffdad6/#93000a · On hold #e2e1ec/#1a1a24 ·
               Archived #e2e1ec/#1a1a24 (muted)
    Lead:      New #e2e1ec/#1a1a24 · Contacted / Site visit / Negotiation
               #e2e1ec/#1a1a24 · Won #c3f0da/#00522f · Lost #e2e1ec/#1a1a24
    User:      Active #c3f0da/#00522f · Invited #ffddb0/#2c1700 ·
               Inactive #e2e1ec/#1a1a24

LEAD-SOURCE CHIPS — the AI-derived sources get tertiary; the rest are neutral:
    💬 Chatbot   #e9ddff fill / #571ac0 text   ← AI
    🔍 AI Search #e9ddff fill / #571ac0 text   ← AI
    📋 Requirement form · 📝 Contact form · 🚶 Walk-in
                 #e5eeff fill / #464555 text   ← not AI

THE STALE FLAG — a small red dot or #ba1a1a text used ONLY for things
  genuinely rotting: an unassigned lead past its threshold, an agent's slow
  response time, an escalated chat waiting for a human. It must stay rare
  enough to mean something.

═══════════════════════════════════════════════════════════════
PART 3 — THE 20 SCREENS
═══════════════════════════════════════════════════════════════

── ACCESS ──────────────────────────────────────────────────────

SCREEN 1 — LOGIN (/admin/login)
A single centered card, max 420px, on the quiet canvas. No sidebar. The
PROPVISTA wordmark at the top — the platform brand, NOT the tenant's. Heading
"Sign in to your workspace". Email and Password fields (visible labels, reveal
icon on the password). A full-width "Sign in" primary button. A "Forgot your
password?" text link. Then a hairline and, below it, in #464555: "Need access?
Ask your administrator to invite you."
THERE IS NO SIGN-UP LINK. Admin accounts are invite-only.
Second small mockup — INVITE ACCEPTANCE: the same shell, but the email is
pre-filled and locked (greyed, non-editable), and the user only sets a
password. The role and tenant are NOT shown, not even as disabled fields —
they were fixed by the inviter and aren't the invitee's business.

── CORE CRM ────────────────────────────────────────────────────

SCREEN 2 — DASHBOARD (/admin/dashboard)
Top row: four KPI cards — Total Listings, Active Leads, Conversion Rate,
Site Visitors. Each a white bento card: a 14px #464555 label above a 30px
semibold #0b1c30 number.
Below, two columns: LEFT a line chart "Leads Over Time" (30-day trend) drawn
in primary #3525cd. RIGHT a horizontal bar chart "Lead Source Breakdown" —
Chatbot, AI Search, Requirement Form, Contact Form, Walk-in. The two AI-driven
sources (Chatbot, AI Search) are drawn in TERTIARY #571ac0; the other three in
primary #3525cd. That's the whole point of the chart: it shows whether the AI
features are earning their cost.
Below: "Recent Activity" — a borderless feed, small icon + one-line
description + timestamp, hover tint #eff4ff. Escalated chats in this feed are
flagged in error #ba1a1a — they are the only genuinely time-sensitive item.

SCREEN 3 — PROPERTIES LIST (/admin/properties)
A data table in a white bento container. Columns: Photo (rounded thumbnail),
Title, Type, Price (right-aligned, 24px semibold), Status (chip), Agent,
Actions. Above it: a search field, filter dropdowns, and an "Add Property"
primary button top-right. When rows are checked, a bulk-action toolbar appears
above the table — "Approve Selected", "Feature Selected", "Archive Selected".
No zebra striping, no heavy row borders — spacing and a #eff4ff hover tint.

SCREEN 4 — ADD / EDIT PROPERTY (/admin/properties/new)
A multi-step form in a centered white bento card, with a horizontal step
indicator across the top: Basic Info · Media · Pricing · Amenities · Location.
The current step in primary #3525cd; completed steps carry a check.
Show "Basic Info": Title, Description (textarea), Property Type (dropdown),
Listing Type (Buy/Rent segmented toggle), Bedrooms and Bathrooms (number
steppers). All #eff4ff fill, visible labels, 2px #3525cd focus ring.
Foot: "Save as Draft" text button left, "Next" primary button right.

SCREEN 5 — BULK UPLOAD (/admin/properties/bulk-upload)
Three numbered steps down the page.
① DOWNLOAD THE TEMPLATE — a card with a "⬇ property-template.csv" outlined
button and the line "Column definitions and allowed values included."
② UPLOAD — a large dashed-border dropzone, 24px radius, #eff4ff fill: "Drop a
.csv or .xlsx here — or browse".
③ REVIEW — the important one. A summary strip: "142 rows · 128 valid · 14 need
attention" — the valid count in success #00522f, the problem count in warning
#2c1700. Below it, an error table: Row / Title / Issue, where each issue is
written in plain language — "price is not a number: 'on request'", "title is
required", "unknown amenity: 'swiming pool' — did you mean 'swimming_pool'?"
Two buttons: "⬇ Download the 14 failed rows" (outlined) and "Import the 128
valid rows as drafts" (primary).
PARTIAL IMPORT IS THE POINT: never make someone fix 14 rows before they get
any value from the other 128.

SCREEN 6 — APPROVALS QUEUE (/admin/properties?status=pending)
The properties list filtered to Pending Approval, beside a REVIEW PANEL. Each
queued row shows the property with everything a reviewer needs to decide
without leaving: photos, price, specs, the submitting agent, and what changed.
Two prominent actions per item: "Approve & Publish" (primary) and "Reject"
(outlined, error #ba1a1a text). Rejecting reveals a required reason field —
a rejection without a reason is a dead end for the agent who submitted it.
Include a small status-flow diagram: Draft → Pending Approval → Published,
with Rejected looping back to Draft, and Sold / On hold / Archived branching
off Published.

SCREEN 7 — LEADS KANBAN (/admin/leads)
Five columns: New · Contacted · Site Visit Scheduled · Negotiation · Closed.
Each header shows the stage name and a count chip.
Lead cards: customer name (14px semibold), a SOURCE CHIP (tertiary for
Chatbot / AI Search, neutral for the rest), the property they're interested in
(one line, truncated), the assigned agent's small round avatar, and a relative
timestamp. UNASSIGNED leads show a loud, highlighted "—" where the avatar
would be, and a stale one carries the red dot — an unassigned lead is nobody's
responsibility and must be impossible to miss.
Show one card MID-DRAG between Contacted and Site Visit, lifted with the soft
shadow and slightly scaled.

SCREEN 8 — LEAD DETAIL (slide-in panel)
A glassmorphic panel sliding in from the right, 32px padding. Top: customer
contact info (name, phone, email) with click-to-call and click-to-email. Then
the source chip, and the property they asked about. Then an ACTIVITY TIMELINE
— a thin #c7c4d8 vertical line with dated entries, completed steps as filled
#3525cd dots. Then a notes textarea, and a "Set follow-up reminder" date
picker at the foot with a primary save button.
IF THE LEAD CAME FROM AN ESCALATED CHAT, flag it hard in error #ba1a1a with
the chat transcript one click away — this is the only genuinely real-time item
in the CRM. Someone is waiting right now. It must not look like every other
lead.

SCREEN 9 — LEADS TABLE (/admin/leads?view=table)
The same data as the board, as a dense sortable table — with a [Kanban][Table]
toggle at top and an "Export CSV" button.
Filter row: search by name/phone, plus Stage, Agent, Source and Created-date
dropdowns.
Columns: checkbox · Name · Source (chip) · Property · Stage (chip) · Owner ·
AGE · row menu.
THE AGE COLUMN IS THE POINT — days since creation, with a red dot when stale.
It is the column a manager sorts by, and it is what surfaces the leads quietly
rotting. Make it prominent. Unassigned owners show a highlighted "—", never a
blank.
When rows are checked, a bulk bar appears: "Assign to [Meera ▾] [Apply]" and
"Change stage".

── PEOPLE ──────────────────────────────────────────────────────

SCREEN 10 — AGENTS (/admin/agents)
A [Leaderboard][List] toggle. The leaderboard is a ranked table: # · Agent ·
Active leads · Closed (30d) · Conversion rate · Avg. first response. Slow
response times carry the red dot.
Below, an AGENT PROFILE: round avatar, name, email, phone, role and join date.
Then two side-by-side cards — ASSIGNED LEADS broken down by stage, and
ASSIGNED LISTINGS broken down by status — each with a "View all →" link.
At the foot, an ACTIONABLE FLAG in warning #2c1700: "⚠ 5 leads have been in
'New' for over 3 days." A metric that tells you what to do beats one that
tells you a number.

SCREEN 11 — USERS & ROLES (/admin/users)
A table: Name · Email · Role · Status chip (Active / Invited / Inactive) · row
menu. An "Invited" row offers an inline "resend" link. Top-right: an "Audit
log" outlined button and a "+ Invite user" primary button.
Below, an INVITE FORM: Email, then Role as radio options WITH PLAIN-LANGUAGE
DESCRIPTIONS beside them — "Admin — full access to everything in your
workspace" and "Agent — their assigned leads only". An admin choosing from a
bare enum will choose wrong.
THE ROLE LIST MUST NOT CONTAIN A SUPER-ADMIN OPTION. Ever.
The row menu says "Deactivate", never "Delete".

SCREEN 12 — AUDIT LOG (/admin/users/audit-log)
Filters: Actor, Action, Entity, Date range. An "Export CSV" button.
A table: When (date over time, two lines) · Who · Did what.
THE ACTION MUST BE WRITTEN FOR A HUMAN: "granted ADMIN to meera@t.com (was:
agent)" — never "UPDATE users SET role='admin'". An audit log nobody can read
is an audit log nobody reads.
HIGH-RISK ENTRIES ARE VISUALLY DISTINCT — role grants, deactivations and
tenant-settings changes carry the red dot in error #ba1a1a. Those are the
entries an investigation is actually looking for.
Each row deep-links to the entity it touched.

── AI CONFIGURATION (four tabs) ────────────────────────────────

SCREEN 13 — AI CONFIG · CHATBOT (/admin/ai-config/chatbot)
A tab bar: [Chatbot] [Recommendation] [Logs] [Search].
Three stacked cards:
  GREETING — "The first thing a visitor sees." A textarea holding "Hi! I'm
    here to help you find a home with Sharma Estates. What are you looking
    for?"
  FAQ LIBRARY — "Facts the bot may use when answering." An expandable list of
    Q&A rows, each with a row menu, and a "+ Add a Q&A" button.
  ESCALATION — "Hand off to a human when:" a checkbox list (the visitor asks
    for one · the bot can't answer after 2 attempts · the visitor seems
    frustrated · the conversation mentions [tag input: legal, complaint]), and
    a handoff-message textarea.
Foot: a "Save" primary button, and beside it a "💬 Test the bot with these
settings" button carrying the AI treatment (gradient border) — it opens a
sandbox chat using the UNSAVED settings.

SCREEN 14 — AI CONFIG · RECOMMENDATION (/admin/ai-config/recommendation)
Heading: "How should we rank matches for your buyers?"
Four labelled sliders — Budget fit 40% · Location 30% · Amenities 20% ·
Property type 10% — each with its percentage on the right. Beneath them a
running "Total 100% ✓" in success #00522f (it turns error red if it doesn't
sum to 100).
THEN THE PREVIEW, WHICH IS THE WHOLE SCREEN. An AI-widget card (gradient
border, faint tertiary glow) showing a sample buyer — "3BHK · ₹50–80L ·
Whitefield · wants parking + gym" — and two side-by-side ranked shortlists:
"With your current weights" vs "With the new ones", each listing three
properties with their match percentages, showing how the order CHANGES.
An abstract slider means nothing; a reordered shortlist means everything.
Foot: "Reset to defaults" text button, "Save" primary button.

SCREEN 15 — AI CONFIG · CHAT LOGS (/admin/ai-config/chat-logs)
A summary strip: "312 conversations · 58 leads (18.6%) · 41 escalated (13.1%)
· 12 flagged". The escalation rate is the number to watch — a rising one means
the bot is failing.
Filters: Status, Outcome, "Flagged only" checkbox.
A table: When · Msgs · Outcome (chip: Lead created = success, Escalated =
error, Abandoned = neutral) · a preview of the first message · a flag icon.
ESCALATED-AND-UNHANDLED ROWS ARE VISUALLY LOUD in error #ffdad6 / #93000a.
Someone is waiting right now — it must not look like a log entry.
Below, the TRANSCRIPT panel — the full conversation. User messages plain;
BOT MESSAGES CARRY THE TERTIARY TREATMENT because they are model output. Tool
calls are rendered INLINE as small tertiary-tinted code chips: [🔧
lookup_property(property_id: "a3f…")] above the bot's reply. That inline tool
call is how you verify the bot used live data instead of inventing it.
Foot: "⚑ Flag for review" and "View the lead →".

SCREEN 16 — AI CONFIG · SEARCH INSIGHTS (/admin/ai-config/search-insights)
A summary strip: "1,284 searches · 84% returned results · avg 1.4s · 3.2% fell
back to keyword search".
QUERIES WITH NO RESULTS — the commercially valuable panel. Subhead: "These
buyers wanted something you don't list." A ranked list of query strings with
counts: "3BHK under 40 lakhs in Indiranagar 47×", "villa with a private pool
31×". Beneath it, a tip in tertiary: "Consider listing in these segments."
QUERIES WITH FEW RESULTS (1–2) — a second panel, with the crucial note: "You
may HAVE these — but if your listing descriptions don't say so, the AI can't
find them. This is a content problem, not an inventory one, and it's fixable
today."
HEALTH — Avg latency 1.4s, Fallback rate 3.2%, Est. cost/search ₹0.04, each
with a small sparkline. The fallback rate is how you notice the AI layer
degrading before customers complain.
Both query panels are AI output — give them the AI-widget treatment.

── CONTENT, REPORTING & PLATFORM ───────────────────────────────

SCREEN 17 — CONTENT / CMS (/admin/cms)
A table: Title · Slug · Status chip · Updated. A "+ New page" primary button.
Below, the EDITOR: Title and Slug fields, then a rich-text editor with a
simple toolbar (B / I / H2 / bullets / link / image) in a bordered container.
Then an SEO card: a Page-title field with a live "52/60 characters ✓" counter,
a Description field with "138/160 ✓", and a GOOGLE PREVIEW — a mock search
result showing the blue title, the green URL, and the grey snippet, so the
admin can see what the world will see.
Foot: "Save draft" text · "Preview" outlined · "Publish" primary.

SCREEN 18 — REPORTS (/admin/reports)
BUILD A REPORT — a card: Type (radio: Leads / Sales / Inventory), a Period
date range, a "Group by" dropdown, and Agent / Stage / Property-type filters.
A "Generate" primary button.
THE RESULT — a table titled "Leads by source · 1–30 Jun 2026": Source · Leads
· Won · Lost · Open · Conversion rate. Rows for AI Chatbot, AI Search, Contact
form, Requirement, Walk-in, with a bold TOTAL row. The two AI sources carry
their tertiary source chips. Numbers right-aligned and aligned on the digit.
This is the report that proves — or disproves — that the AI features are worth
what they cost. Make it feel like evidence.
Foot: "⬇ Excel" and "⬇ PDF" outlined buttons.

SCREEN 19 — NOTIFICATION RULES (/admin/settings/notifications)
Heading: "Tell the right people when something happens." A "+ New rule"
button.
A rules table: When… · Send via · To… · On (toggle) · row menu. Example rows:
"A new lead arrives / Email + In-app / Assigned agent", "A chat is escalated /
Email + SMS / All agents", "A lead sits in 'New' for 48h / Email / Admins".
Below, a NEW RULE form: a "When" dropdown, "Send" channel checkboxes, and a
"To" radio group — the assigned agent · specific people (a tag input) · a role.
⚠ CRITICAL: EMAIL AND SMS CANNOT BE DELIVERED — no provider is configured.
Render every Email and SMS checkbox DISABLED at 40% opacity, with a warning
strip above the table in warning #ffddb0 / #2c1700: "Email and SMS delivery
isn't configured yet — only in-app notifications will be sent." Do not draw
working switches for channels that would silently do nothing.

SCREEN 20 — AGENT CHAT CONSOLE (/admin/chat)   ★ THE REAL-TIME ONE
Where the chatbot's promise comes true — the bot says "I've looped in one of our
agents", and this is that agent arriving.
Three columns: sidebar · queue · conversation.
QUEUE: "⚠ 3 waiting". Cards for each escalated conversation, UNCLAIMED FIRST,
SORTED BY WAIT TIME, longest at top. Each: visitor name · **WAITING TIME (the
most important number on the screen — "14m", turning #ba1a1a past a threshold)** ·
a preview of what they said · message count · a "Take" button.
CONVERSATION: the visitor's contact details and the property in play, then the
transcript with THREE VISUALLY DISTINCT VOICES:
  👤 VISITOR — plain, neutral.
  🤖 BOT — TERTIARY #571ac0. It is model output. Tool calls inline:
       [🔧 lookup_property(id: "a3f…")]
  🙋 AGENT — **NEVER TERTIARY.** A human wrote it. Attribute by name, primary-
       tinted bubble, avatar.
A divider marks the handoff: "── escalated 14m ago ──".
Composer at the foot, **disabled until you have claimed the conversation**. Then
"Close conversation".
⚠️ The bot's messages and the agent's messages MUST NOT look the same. If a human
agent's reply is painted in the AI color, the screen is lying about who is talking
— on the one screen whose whole purpose is to show a worried customer that a real
person has arrived.

SCREEN 21 — SUPER ADMIN · TENANTS (/platform/tenants)
A DIFFERENT sidebar — this is the platform level, not a tenant's workspace.
It reads "PLATFORM" with just two rows: Tenants, Health. No tenant name
beneath the logo.
Heading "Tenants (14)" with a status filter and a "+ New tenant" button.
A table: Business · Domain · Status chip (Active = success, Trial = warning
with "3d left", Suspended = error with the red dot) · Properties · Leads · row
menu (Edit · Suspend · Reactivate · View as).
Below, a NEW TENANT form: Business name, Subdomain (shown as
"[ nova ].propvista.com"), Status dropdown — and then FIRST ADMIN: an email
field, with the note "They get an invite and become the tenant's first admin."
A tenant with no admin is an empty workspace nobody can get into, so the two
are created together in one step.

═══════════════════════════════════════════════════════════════
FINAL CHECKS — what most often goes wrong here
═══════════════════════════════════════════════════════════════
1. TERTIARY VIOLET #571ac0 appears ONLY on: the Chatbot and AI Search source
   chips, the two AI bars in the dashboard chart, the bot's messages and
   inline tool calls in a transcript, the recommendation preview, the search-
   insight panels, and the "Test the bot" button. NOT on nav, NOT on focus
   rings, NOT on status chips, NOT on buttons.
2. NO MONOSPACE AND NO SERIF. Every price, percentage and table figure is Plus
   Jakarta Sans, right-aligned, aligned on the digit.
3. TABLES ARE THE PRODUCT HERE. No zebra stripes, no heavy borders — spacing,
   a sticky header, and a hover tint. Dense but never cramped.
4. THE RED FLAG STAYS RARE. It marks only things genuinely rotting: an
   unassigned stale lead, an escalated chat waiting for a human, a high-risk
   audit entry. If everything is flagged, nothing is.
```

---

## 20. Single-Paste Prompt — Core Admin (the 10 screens you actually work in)

> **What this is.** A **focused** single-paste prompt covering the admin surface an agent lives in daily: the dashboard, property CRUD, the lead pipeline, and the two chat screens. **Ten screens, deep** — where §19 is twenty screens, broad but shallower per screen.
>
> **Use this when** you're building or iterating the core CRM. Use **§19** when you need the whole portal including agents, users, audit log, CMS, reports and super-admin.
>
> ⚠️ **Generated artifact.** The tokens below are copied from `DESIGN.md`. **If `DESIGN.md` changes, regenerate this section AND §19.** Never hand-edit a token here.
>
> **SCREEN 10 (Agent Chat Console) is new.** It closes gap G7 — until 2026-07-14 the bot could escalate to a human and **no endpoint let that human reply**. Spec: `17-admin-spec/22-agent-chat-console.md` · `04-api-spec.md` §12A · `05-ai-chatbot-spec.md` §10A.

**Stitch prompt:**

```
Design the core admin portal for PropVista CRM — a multi-tenant real estate CRM.
10 screens, one design system. This is where agents and admins live for eight
hours a day.

It is a TOOL, not a storefront: compact, dense, desktop-first, calm. It carries
the PROPVISTA brand, never a tenant's.

═══════════════════════════════════════════════════════════════
PART 1 — THE DESIGN SYSTEM
═══════════════════════════════════════════════════════════════

CONCEPT: "Effortless Intelligence." Soft Minimalism. Bento-box layouts — content
in rounded white containers on a soft canvas. Dense but never cramped: no heavy
borders, no muddy shadows, no zebra-striped tables.

COLOR — use these exact values, no others:
  Canvas / page background      #f8f9ff
  Card surface                  #ffffff
  Input fill                    #eff4ff
  Chip fill (neutral)           #e5eeff
  Hairline border               #c7c4d8
  Primary text                  #0b1c30
  Secondary text                #464555
  PRIMARY — high-intent actions #3525cd   (buttons, focus rings, active nav)
  Button gradient               #3525cd → #0058be
  Primary tint (selected/hover) #e2dfff
  TERTIARY — the AI layer       #571ac0   (tint #e9ddff)
  Dark / terminal               #213145   (text on it: #eaf1ff)
  STATUS success                #c3f0da fill / #00522f text
  STATUS warning                #ffddb0 fill / #2c1700 text
  STATUS error / urgent         #ffdad6 fill / #93000a text  (strong: #ba1a1a)
  STATUS neutral                #e2e1ec fill / #1a1a24 text

THE ONE RULE THAT MATTERS MOST — read it twice:
  #571ac0 tertiary violet marks AI-GENERATED OUTPUT AND NOTHING ELSE.
  In this portal that is exactly: the Chatbot and AI Search lead-source chips,
  the two AI bars in the dashboard chart, and THE BOT'S MESSAGES AND TOOL CALLS
  in a transcript.
  It is NOT for: nav, focus rings (those are PRIMARY #3525cd), status chips,
  buttons, or a HUMAN AGENT'S CHAT REPLY. A human wrote that.

STATUS IS NOT BRAND: never use primary/secondary/tertiary to mean a status.
  Status uses the four status colors above and ALWAYS carries a text label.

TYPE: Plus Jakarta Sans throughout. NO MONOSPACE, NO SERIF — every price,
  percentage and table figure is Plus Jakarta Sans, right-aligned, aligned on
  the digit.
  Page heading 30/600 · Section 24/600 · Metrics 30/600 · Body 16/400 ·
  Table cells & labels 14/600 · Caption 12/500

SHAPE: Cards 24px radius. Buttons, inputs, table containers 12px. Chips fully
  rounded. Nothing sharp.

DEPTH: One ultra-soft shadow for floating elements: 0 10px 30px
  rgba(11,28,48,0.04). 1px #c7c4d8 hairlines only where needed. Glassmorphism
  (20px blur + rgba(255,255,255,0.7)) on slide-in panels.

COMPONENTS:
  Buttons — 48-56px, 12px radius. Primary = gradient, white text. Secondary =
    outlined 1px #3525cd. Text = #464555. Destructive = #ba1a1a.
  Inputs — #eff4ff fill, no border at rest, 2px #3525cd ring on focus. EVERY
    field has a VISIBLE LABEL above it — never a placeholder as a label.
  Tables — the workhorse. NO zebra striping, NO heavy row borders. Separate rows
    with vertical space and a #eff4ff hover tint. Sticky header. Numbers right.
  Icons — line style, 1.5px stroke.

═══════════════════════════════════════════════════════════════
PART 2 — SHARED FURNITURE
═══════════════════════════════════════════════════════════════

SIDEBAR (every screen): a fixed left rail ~240px. PropVista logo at top, the
  tenant's business name beneath it in 12px #464555 (a label, not a brand). Nav
  rows with line icons: Dashboard · Properties · Leads · **Chat** · Agents ·
  Users · AI Config · Reports · Settings.
  The **Chat** row carries a COUNT BADGE when people are waiting — it is the one
  nav item allowed to shout, because someone is waiting right now.
  Active row = #e2dfff tint, #3525cd text and icon.

STATUS CHIPS — fully rounded, pale fill + dark text of the same hue, ALWAYS with
  a text label:
    Property: Draft #e2e1ec/#1a1a24 · Pending Approval #ffddb0/#2c1700 ·
              Published #c3f0da/#00522f · Sold #213145/#eaf1ff ·
              Rejected #ffdad6/#93000a · On hold / Archived #e2e1ec/#1a1a24
    Lead:     New #e2e1ec/#1a1a24 · Contacted / Site visit / Negotiation
              #e2e1ec/#1a1a24 · Won #c3f0da/#00522f · Lost #e2e1ec/#1a1a24

LEAD-SOURCE CHIPS — the AI-derived ones get tertiary; the rest do not:
    💬 Chatbot  #e9ddff / #571ac0   ← AI
    🔍 AI Search #e9ddff / #571ac0  ← AI
    📋 Requirement · 📝 Contact form · 🚶 Walk-in   #e5eeff / #464555

THE RED FLAG — #ba1a1a, used ONLY for things genuinely rotting: an unassigned
  stale lead, an escalated chat waiting for a human, a high-risk audit entry.
  If everything is flagged, nothing is.

═══════════════════════════════════════════════════════════════
PART 3 — THE 10 SCREENS
═══════════════════════════════════════════════════════════════

SCREEN 1 — DASHBOARD (/admin/dashboard)
Top row: four KPI cards — Total Listings · Active Leads · Conversion Rate ·
Site Visitors. Each a white bento card: a 14px #464555 label above a 30px
semibold #0b1c30 number.
Two columns below. LEFT: a line chart "Leads Over Time" (30-day) in primary
#3525cd. RIGHT: a horizontal bar chart "Lead Source Breakdown" — Chatbot, AI
Search, Requirement Form, Contact Form, Walk-in. The two AI-driven sources are
drawn in TERTIARY #571ac0; the other three in primary. That contrast IS the
chart's purpose: it shows whether the AI features are earning their cost.
Below: "Recent Activity" — a borderless feed, icon + one line + timestamp,
#eff4ff hover tint. **Escalated chats in this feed are flagged in #ba1a1a** —
they are the only genuinely time-sensitive item on the page.

SCREEN 2 — PROPERTIES LIST (/admin/properties)
A data table in a white bento container. Columns: Photo (rounded thumb) · Title ·
Type · Price (right-aligned, 24px semibold) · Status (chip) · Agent · Actions.
Above it: a search field, filter dropdowns, and an "Add Property" primary button
top-right. When rows are checked, a bulk-action toolbar appears above the table:
"Approve Selected" · "Feature Selected" · "Archive Selected".
No zebra stripes. No heavy row borders. Spacing and a hover tint.

SCREEN 3 — ADD / EDIT PROPERTY (/admin/properties/new)
A multi-step form in a centered white bento card. A horizontal step indicator
across the top: Basic Info · Media · Pricing · Amenities · Location — current
step in primary #3525cd, completed steps with a check.
Show "Basic Info": Title · Description (textarea) · Property Type (dropdown) ·
Listing Type (Buy/Rent segmented toggle) · Bedrooms and Bathrooms (number
steppers). All #eff4ff fill, visible labels, 2px #3525cd focus ring.
Foot: "Save as Draft" text button left, "Next" primary button right.

SCREEN 4 — BULK UPLOAD (/admin/properties/bulk-upload)
Three numbered steps.
① Download the template — a card with a "⬇ property-template.csv" outlined
button and the line "Column definitions and allowed values included."
② Upload — a large dashed dropzone, 24px radius, #eff4ff fill: "Drop a .csv or
.xlsx here — or browse".
③ Review — the important one. A summary strip: "142 rows · 128 valid · 14 need
attention" with the valid count in #00522f and the problem count in #2c1700.
Below it an error table — Row / Title / Issue — with issues in PLAIN LANGUAGE:
"price is not a number: 'on request'" · "title is required" · "unknown amenity:
'swiming pool' — did you mean 'swimming_pool'?"
Two buttons: "⬇ Download the 14 failed rows" (outlined) and "Import the 128 valid
rows as drafts" (primary).
PARTIAL IMPORT IS THE POINT. Never make someone fix 14 rows before they get any
value from the other 128.

SCREEN 5 — APPROVALS QUEUE (/admin/properties?status=pending)
The property list filtered to Pending Approval, beside a review panel. Each
queued item shows everything a reviewer needs to decide without leaving: photos,
price, specs, the submitting agent.
Two actions per item: "Approve & Publish" (primary) and "Reject" (outlined,
#ba1a1a text). **Rejecting reveals a REQUIRED reason field** — a rejection with
no reason is a dead end for the agent who submitted it.

SCREEN 6 — LEADS KANBAN (/admin/leads)
Five columns: New · Contacted · Site Visit Scheduled · Negotiation · Closed. Each
header carries the stage name and a count chip.
Lead cards: customer name (14px semibold) · a SOURCE CHIP (tertiary for Chatbot /
AI Search, neutral for the rest) · the property they want (one line, truncated) ·
the assigned agent's round avatar · a relative timestamp.
UNASSIGNED leads show a loud highlighted "—" where the avatar would be, and a
stale one carries the red dot. An unassigned lead is nobody's responsibility and
must be impossible to miss.
Show one card MID-DRAG between Contacted and Site Visit, lifted with the soft
shadow, slightly scaled.

SCREEN 7 — LEAD DETAIL (slide-in panel)  ← this is the "customer" view
A glassmorphic panel sliding from the right, 32px padding.
Top: the customer — name, phone, email, with click-to-call and click-to-email.
Then the source chip, and the property they asked about.
Then their own message, in a tinted #eff4ff inset panel.
Then an ACTIVITY TIMELINE — a thin #c7c4d8 vertical line with dated entries;
completed steps are filled #3525cd dots, future steps hollow #c7c4d8.
Then a notes textarea, a "Set follow-up reminder" date picker, and a primary save
button.
**IF THE LEAD CAME FROM AN ESCALATED CHAT**, flag it hard in #ba1a1a with a
"View conversation →" link straight to the Chat Console. Someone may be waiting
in that chat right now — it must not look like every other lead.

SCREEN 8 — LEADS TABLE (/admin/leads?view=table)
The same data, dense and sortable. A [Kanban][Table] toggle at top and an
"Export CSV" button.
Filters: search by name/phone, plus Stage · Agent · Source · Created-date.
Columns: checkbox · Name · Source (chip) · Property · Stage (chip) · Owner ·
AGE · row menu.
**THE AGE COLUMN IS THE POINT** — days since creation, red dot when stale. It is
the column a manager sorts by, and it is what surfaces the leads quietly rotting.
Make it prominent. Unassigned owners show a highlighted "—", never a blank.
Checked rows reveal a bulk bar: "Assign to [Meera ▾] [Apply]" · "Change stage".

SCREEN 9 — AI CHAT LOGS (/admin/ai-config/chat-logs)   — read-only review
A summary strip: "312 conversations · 58 leads (18.6%) · 41 escalated (13.1%) ·
12 flagged". **The escalation rate is the number to watch — a rising one means
the bot is failing.**
Filters: Status · Outcome · "Flagged only".
A table: When · Msgs · Outcome (chip: Lead created = success, Escalated = error,
Abandoned = neutral) · first-message preview · flag icon.
ESCALATED-AND-UNHANDLED ROWS ARE VISUALLY LOUD (#ffdad6 / #93000a).
Below, the TRANSCRIPT panel. Visitor messages plain. **BOT messages carry the
TERTIARY treatment — they are model output.** Tool calls render INLINE as small
tertiary-tinted chips above the bot's reply:
    [🔧 lookup_property(property_id: "a3f…")]
That inline tool call is how you verify the bot used live data instead of
inventing it.
Foot: "⚑ Flag for review" · "View the lead →".

SCREEN 10 — AGENT CHAT CONSOLE (/admin/chat)   ★ THE REAL-TIME ONE
This is where the chatbot's promise comes true. The bot tells a visitor "I've
looped in one of our agents" — this is the agent showing up.

THREE-COLUMN layout: sidebar · queue · conversation.

QUEUE (middle, ~320px): a header "⚠ 3 waiting". Below, cards for each escalated
conversation, UNCLAIMED FIRST, SORTED BY WAIT TIME, LONGEST AT TOP:
  · visitor name (14px semibold)
  · **WAITING TIME — the most important number on this screen.** "14m", and it
    goes #ba1a1a red past a threshold. It is what turns "a queue" into "someone
    is waiting."
  · a preview of what they said: "I want to speak to someone about Sunview"
  · message count
  · a "Take" button (primary #3525cd)
Conversations you're already handling are marked "● mine" and sort below.

CONVERSATION (right, fills the rest):
  Header: the visitor — name, phone — plus the property in play with a
  "View →" link.
  The transcript, with THREE VISUALLY DISTINCT VOICES:
    👤 VISITOR — plain, neutral surface, left-aligned.
    🤖 BOT — TERTIARY #571ac0 treatment. It is model output. Tool calls inline:
         [🔧 lookup_property(id: "a3f…")]
    🙋 AGENT — **NEVER TERTIARY.** A human wrote it. Attribute it by name
         ("Anjali"), and give it a clearly human treatment — a primary-tinted
         bubble with the agent's avatar.
  A divider marking the handoff: "── escalated 14m ago ──".
  Composer at the foot: a text input with a send button. **It is DISABLED and
  visibly greyed until you have claimed this conversation.**
  Below it: "Close conversation" (outlined, #464555).

⚠️ THE MOST IMPORTANT THING ON THIS SCREEN: the bot's messages and the agent's
messages MUST NOT look the same. Tertiary violet means "a machine generated
this." If a human agent's reply is painted in the AI color, the screen is lying
about who is talking — on the one screen whose entire purpose is to show a
worried customer that a real person has arrived.

Also render TWO small states:
  (a) EMPTY QUEUE — "No one's waiting." Calm, not celebratory. This is the normal
      state and it should feel like it.
  (b) CLAIM RACE LOST — a quiet inline message, "Ravi picked this one up", and the
      queue refreshes. NOT an error toast. Two agents clicking "Take" at the same
      moment is a normal race, not a failure.

═══════════════════════════════════════════════════════════════
FINAL CHECKS — what most often goes wrong
═══════════════════════════════════════════════════════════════
1. TERTIARY VIOLET #571ac0 appears ONLY on: the Chatbot / AI Search source chips,
   the two AI bars in the dashboard chart, and THE BOT'S messages and tool calls.
   NOT on nav. NOT on focus rings. NOT on status chips. NOT on buttons.
   **NOT on a human agent's chat reply.**
2. NO MONOSPACE, NO SERIF. Every price, percentage and figure is Plus Jakarta
   Sans, right-aligned, aligned on the digit.
3. TABLES ARE THE PRODUCT. No zebra stripes, no heavy borders — spacing, a sticky
   header, a hover tint. Dense but never cramped.
4. THE RED FLAG STAYS RARE. Only genuinely rotting things: an unassigned stale
   lead, an escalated chat waiting for a human, a high-risk audit entry.
5. WAITING TIME on Screen 10 is the single most important number in this portal.
   Everywhere else a stale view costs someone minutes. There, a person is sitting
   in a chat window right now.
```

---

## 21. Tips for Using These Prompts in Stitch

Each of §17 (public site), §18 (customer portal), and §19 (admin portal) is a complete, self-contained prompt: copy it, paste it into Stitch, and run the generator.

**Use them in this order:**
1. §17 first — build the public site and all 11 public screens, including the chat widget overlay.
2. Then §18 — build the customer portal, reusing the header and nav shell from the public site but focusing on the five authenticated screens.
3. Finally §19 — build the admin portal, which shares the design system but is denser and desktop-first.

**What to do:**
- **Paste `DESIGN.md` first** in its own message, then paste one prompt section in a separate message. Every prompt assumes the design system is already in context.
- **Run the screens in the order above** — Stitch stays more visually consistent when later prompts can reference earlier screens ("match the style of the chat widget I just generated").
- **If a result drifts off-brand**, re-paste `DESIGN.md` alongside the screen prompt rather than trying to correct it with a vague follow-up.

**What NOT to do:**
- Do NOT paste the entire file into Stitch — it won't help.
- Do NOT paste `DESIGN.md` and a section prompt together in one go.
- Do NOT edit the token block inlined in each prompt. They are generated artifacts — if the tokens change in `DESIGN.md`, regenerate the prompts.

**Watch these discipline rules:**
- **Tertiary violet #571ac0** marks ONLY AI-generated output: the chat widget, AI search results, requirement-wizard matches, portal recommendation cards, and the "AI match" chips. NOWHERE ELSE — not on nav, not on focus rings, not on buttons, not on non-AI status badges.
- **No monospace and no serif.** Every price and every figure is Plus Jakarta Sans.
- **Tables in admin portal:** no zebra stripes, no heavy borders — spacing, a sticky header, and a hover tint. Dense but never cramped.

---

**This is a supplementary doc** (not part of the core 00–10 engineering set) — reference it alongside `01-prd.md`'s wireframe notes when generating visuals, and keep both in sync if the PRD's UI requirements change. The design system itself is owned by [`DESIGN.md`](./DESIGN.md); never fork a copy of it into this file.
