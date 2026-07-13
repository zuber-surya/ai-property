---
name: PropVista CRM
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#464555'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#777587'
  outline-variant: '#c7c4d8'
  surface-tint: '#4d44e3'
  primary: '#3525cd'
  on-primary: '#ffffff'
  primary-container: '#4f46e5'
  on-primary-container: '#dad7ff'
  inverse-primary: '#c3c0ff'
  secondary: '#0058be'
  on-secondary: '#ffffff'
  secondary-container: '#2170e4'
  on-secondary-container: '#fefcff'
  tertiary: '#571ac0'
  on-tertiary: '#ffffff'
  tertiary-container: '#6f3dd9'
  on-tertiary-container: '#e3d5ff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e2dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#0f0069'
  on-primary-fixed-variant: '#3323cc'
  secondary-fixed: '#d8e2ff'
  secondary-fixed-dim: '#adc6ff'
  on-secondary-fixed: '#001a42'
  on-secondary-fixed-variant: '#004395'
  tertiary-fixed: '#e9ddff'
  tertiary-fixed-dim: '#d0bcff'
  on-tertiary-fixed: '#23005c'
  on-tertiary-fixed-variant: '#5516be'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '600'
    lineHeight: '1.3'
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.4'
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.4'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  container-max: 1440px
  gutter: 24px
  margin-desktop: 40px
  margin-mobile: 20px
  stack-lg: 48px
  stack-md: 24px
  stack-sm: 12px
---


## Brand & Style

The design system is anchored in the concept of "Effortless Intelligence." It seeks to transform the often chaotic nature of real estate management into a serene, curated experience. The brand personality is professional yet deeply human, evoking the feeling of a premium physical concierge rather than a database.

The visual style is **Soft Minimalism** with **Glassmorphic** accents. It prioritizes negative space (white space) to reduce cognitive load, allowing property imagery and AI-driven insights to breathe. We move away from the traditional "dashboard" feel—characterized by dense tables and heavy borders—toward a "canvas" feel, using bento-style layouts to group information into meaningful, digestible modules.

Key attributes:
- **Calm & Spacious:** Generous padding and margins to prevent data fatigue.
- **Warmly Modern:** A soft-blue tinted neutral palette that feels more inviting than pure grayscale.
- **AI-First:** Subtle glows and translucent layers signal where intelligence is assisting the user.

## Colors

> **The token block above is canonical.** Every value named in this prose is one of those tokens — never introduce a hex that isn't in the token set.

The color palette is designed to be receding and calm, allowing property photography to be the protagonist.

- **The Canvas:** `background` / `surface` (`#f8f9ff`) is the base — a soft, non-reflective surface that reduces eye strain compared to pure white. Cards sit on it in `surface-container-lowest` (`#ffffff`).
- **High-intent actions:** `primary` (`#3525cd`) is reserved for high-intent actions — primary buttons, active states, selected options. `primary-container` (`#4f46e5`) is its lighter companion; `primary-fixed` (`#e2dfff`) is the low-contrast tint for selected/hover states.
- **The intelligence layer:** The `tertiary` family (`#571ac0`, container `#6f3dd9`, tint `#e9ddff`) is used **exclusively** for AI-generated insights, predictions, match scores, and automated suggestions. It is a semantic color, not a decorative one — if an element wasn't produced by the model, it is not tertiary. **There are no exceptions**, including focus and hover states, which use `primary`.
- **Text:** `on-surface` (`#0b1c30`) is a deep slate rather than pure black, maintaining a premium, editorial feel. Secondary text uses `on-surface-variant` (`#464555`) to establish hierarchy without needing thin font weights.

### ⚠️ The container tokens invert Material 3

This token set is *shaped* like a Material 3 scheme, so tools and engineers will read it with M3 expectations. **It does not follow them.** Read this before using any `*-container` token:

| Token pair | This system | Material 3 would be |
|---|---|---|
| `primary-container` / `on-primary-container` | `#4f46e5` saturated, **light** `#dad7ff` text | pale tint, dark text |
| `secondary-container` / `on-secondary-container` | `#2170e4` saturated, **light** `#fefcff` text | pale tint, dark text |
| `tertiary-container` / `on-tertiary-container` | `#6f3dd9` saturated, **light** `#e3d5ff` text | pale tint, dark text |
| `primary-fixed` / `on-primary-fixed` | `#e2dfff` pale, dark `#0f0069` text | *(same — follows M3)* |

**The `-fixed` tokens are the pale tints.** When you want a low-contrast background with dark text — a selected chip, a hover tint, a soft badge — reach for `*-fixed`, never `*-container`. The `*-container` tokens are saturated fills that take light text.

Note `tertiary-container` + `on-tertiary-container` lands at **4.55 : 1** — it passes AA for normal text with nothing to spare. Don't set anything below 16px on it.

### Token roles

Every token has a job. Ones without a stated job get used arbitrarily by whatever tool touches this file next.

- `outline` (`#777587`) — form-field borders in their resting/unfocused state.
- `surface-dim` (`#cbdbf5`) — scrims and overlays (map dimming, modal backdrop).
- `surface-tint` (`#4d44e3`) — reserved; do not use until assigned.
- `inverse-primary` (`#c3c0ff`) — primary-colored elements sitting on `inverse-surface`.
- ~~`surface-bright`~~ — **redundant alias of `surface`** (both `#f8f9ff`). Do not use.
- ~~`surface-variant`~~ — **redundant alias of `surface-container-highest`** (both `#d3e4fe`). Do not use.

The two redundant aliases are left in the YAML rather than deleted, so an already-imported Stitch theme doesn't break on a missing key. Treat them as deprecated.

## Typography

This design system utilizes **Plus Jakarta Sans** for its modern, friendly, and geometric characteristics. The type scale is intentionally large to reinforce the sense of "Premium Space."

- **One face only:** There is **no monospace and no serif** in this system. Numerals — including prices — are set in Plus Jakarta Sans like everything else.
- **Headlines:** Use tight letter spacing and bold weights to create a confident, editorial look (`display-lg`, `headline-lg`).
- **Body Text:** Line heights are set at 1.6x to ensure maximum readability and a relaxed pace.
- **Prices & key figures:** `headline-md` (24px / 600) in `on-surface` — size and weight carry the emphasis, not a different typeface.
- **Hierarchy:** Focus on size and color (`on-surface` vs. `on-surface-variant`) rather than excessive weight changes. Labels use a slightly tighter tracking and medium/semibold weight for clarity at small sizes.

## Layout & Spacing

The layout follows a **Bento Box** philosophy: content is organized into logical, rounded containers that sit on a 12-column grid.

- **Grid:** 12 columns with 24px gutters. The max-width is capped at 1440px to ensure line lengths remain readable on ultra-wide monitors.
- **Rhythm:** An 8px base unit with a 4px half-step — `stack-sm` (12px) and `rounded.md` (12px) sit on the half-step. Component internal padding should be generous—typically 24px or 32px for cards—to avoid any feeling of "cramping."
- **Responsiveness:** On mobile, the grid collapses to a single column. The 40px desktop margins scale down to 20px.
- **The "Hero" Layout:** Property details should use a 60/40 or 70/30 split, prioritizing large-scale imagery on the left or top.

## Elevation & Depth

We avoid heavy, muddy shadows. Depth is communicated through **Tonal Elevation** and **Ambient Light**.

- **Surfaces:** Main cards use `surface-container-lowest` (`#ffffff`) against the `background` canvas (`#f8f9ff`).
- **Shadows:** Use a single, ultra-soft shadow for active states or floating elements: `0px 10px 30px rgba(11, 28, 48, 0.04)` — that is `on-surface` at 4%.
- **Glassmorphism:** Navigation bars and AI widgets use a backdrop blur (20px) with a semi-transparent white fill (`rgba(255, 255, 255, 0.7)`). This allows the colors of property photos to bleed through subtly, maintaining a sense of place.
- **Borders:** Instead of dark lines, use a 1px `outline-variant` (`#c7c4d8`) border to define boundaries only where necessary.

## Shapes

The shape language is characterized by **Generous Radii**. This design system avoids sharp corners to maintain its "Warm and Human" personality.

- **Cards/Bento Boxes:** Use `rounded.xl` (1.5rem / 24px) or higher. Large property image containers can go up to 32px.
- **Interactive Elements:** Buttons and input fields use `rounded.md` (0.75rem / 12px) to feel substantial and clickable.
- **Chips & Pills:** `rounded.full`.
- **Visual Continuity:** Every element, from the smallest chip to the largest container, must have some level of rounding to ensure the UI feels soft and approachable.

## Components

- **Buttons:** Large height (48px-56px). Primary buttons use a subtle gradient from `primary` (`#3525cd`) to `secondary` (`#0058be`), with `on-primary` (`#ffffff`) text. No sharp corners.
- **Inputs:** "Effortless Fields"—large 16px text, 16px vertical padding, and a `surface-container-low` (`#eff4ff`) fill with a border that only appears on focus. Focus states use a 2px `primary` (`#3525cd`) ring. **Not tertiary** — a focused field is a user action, not a model output, and the intelligence layer must not be diluted by a state that fires on every form field in the CRM.
- **Chips:** Used for property tags (e.g., "Just Listed," "High ROI"). Low-contrast `surface-container` (`#e5eeff`) backgrounds with medium-weight `on-surface-variant` text.
- **Cards:** The core of the bento layout. 24px-32px padding. Imagery should always have a `16/9` or `4/3` aspect ratio within cards.
- **AI Widgets:** Distinct from standard cards. Use a very subtle `1px` gradient border from `primary` (`#3525cd`) to `tertiary` (`#571ac0`), plus a faint tertiary background glow, to signify "Intelligence."
- **Lists:** Avoid borders between list items. Use vertical spacing and subtle hover states (a `surface-container-low` tint) to separate entries.
- **Property Hero:** A full-bleed or large-inset container that makes the real estate photography the center of the user's focus.

## Known Gap — Semantic Status Colors

⚠️ This system defines **no success or warning ramp** — the only semantic token is `error` (`#ba1a1a`). Status indicators (e.g. a listing's Draft / Pending Approval / Published / Sold states) currently have to borrow from `primary` and `secondary`, which are both blues and are **not reliably distinguishable at chip size**. Add a proper status ramp before building any screen that depends on status at a glance. Tracked against `docs/11-stitch-design-prompts.md` §7.