📄 Customer‑Facing Pages (Public Site + Customer Portal)

1. Homepage (/) – 01-homepage.md

Purpose – Get visitors into a result set as fast as possible via natural‑language search, quick filters, or a featured listing; also expose the ever‑present chat widget and the Requirement‑Wizard CTA.
Layout / Regions
HEADER (logo, nav, Login/Portal)
HERO – free‑text search + mic + submit
AUTOSUGGEST (dropdown under input)
QUICK FILTERS (chips: Buy/Rent/Type/Price)
FEATURED PROPERTIES (grid of cards with heart)
REQUIREMENT CTA BAND (“Not sure where to start? …”)
FOOTER (static links, tenant contact)
CHAT LAUNCHER (fixed bottom‑right bubble)
Components – SearchInput, Autosuggest, FilterChip, PropertyCard (image, price, beds/area, favorite heart), CTAButton, FooterLinks, ChatLauncher.
Interaction Flow
1. Page loads → GET /properties?is_featured=true&page_size=6 (featured grid).
2. User types in hero → debounced autosuggest (client‑side only; gap G3 – no endpoint yet).
3. Mic click → Web Speech API fills input.
4. Submit (Enter/button/pick suggestion) → navigate to /search?q=<query>.
5. Heart toggle → Optimistic toggle → POST/DELETE /properties/{id}/favorite.
6. Click featured card → /property/:id.
7. Click CTA → /requirement-analysis.
8. Open chat bubble → chat overlay (no API call on open; first message triggers /ai/chat/message).
States – Loading (skeleton cards), Empty (hide featured section or show CTA), Error (hide featured, log), Voice‑unsupported (hide mic), Logged‑in/out (header shows “My Portal” vs “Login”, heart state persists via session/user).
API Calls

- GET /properties?is_featured=true&page_size=6 (featured)
- POST /properties/{id}/favorite / DELETE … (favorite)
- Chat first message → POST /ai/chat/message (see chatbot feature).
Permissions / Tenancy – Fully anonymous. Tenant is derived from request domain/subdomain; featured query is scoped to that tenant via RLS (plus app‑level filter). No tenant_id sent by client.
Notes / Open Questions
- [G3] Autosuggest endpoint missing (FR2.4).
- [G5] Public CMS read endpoint missing (hero/banner editing).
- Number of featured items & ordering (most recent / admin‑picked) not defined.
- Voice input assumed to be browser Web Speech API (no backend transcription).

---
2. Property Listing / Search Results (/search) – 02-property-listing.md

Purpose – Unified results surface for AI natural‑language search and classic filter browsing; must support grid/list/map toggle, faceted filters, sorting, pagination/incremental loading skeletons, empty-state falling back to filtered by AI or manual filters, favorite without nudging users toward AI.
Layout / Regions
HEADER (logo, search bar pre‑filled with query, clear button)
FILTER RAIL (collapsible on mobile) – Price, Type, Bedrooms, Location, Amenities
RESULT HEADER – count + plain‑language query interpretation
PARSED‑QUERY CHIPS (AI‑only, removable)
VIEW TOGGLE (Grid/List/Map)
SORT dropdown (Relevance, Price ↑/↓, Newest, Area)
RESULT GRID / LIST / MAP (property cards with favorite heart; AI cards show match‑score badge)
LOAD‑MORE / PAGINATION (or infinite scroll – open question)
Components – SearchBar, FilterPanel (accordion/sheet), ResultHeader, Chip, ViewToggle, SortDropdown, PropertyCard (image, title, price, beds/area, favorite, match‑score), LoadMoreButton or Pagination, MapView (with “not mapped” sidebar).
Interaction Flow
1. Arrive with ?q= → POST /ai/search (query+filters+page) → returns items[], parsed_query, total.
  - If AI parse fails/times‑out/429 → silent fallback to GET /properties?<filters> (keyword‑only).

2. Arrive without ?q= → GET /properties?<filters> (standard filter browse).
3. Changing any filter/sort → update URL, re‑call appropriate endpoint (AI or filter).
4. Removing a parsed‑query chip → drops that constraint, re‑calls AI search.
5. Toggle view/sort → no new request (client‑side only).
6. Heart toggle → optimistic POST/DELETE /properties/{id}/favorite.
7. Click card → /property/:id.
8. Load more / paginate → same endpoint with increased page.
States – Loading (skeleton cards or dimmed previous results), Empty filters (show suggestion to widen), Empty AI results (show closest‑match fallback + wizard CTA), AI degraded (quiet “Showing keyword results”), API error (full‑page retry, chat still usable), Map view missing coordinates (show “not mapped” sidebar), Logged out (session‑scoped hearts).
API Calls

- POST /ai/search (when ?q= present) – body {query, filters, page, page_size}
- GET /properties?… (filter‑only or fallback) – standard listing params
- POST /properties/{id}/favorite / DELETE …
Permissions / Tenancy – Anonymous. Tenant derived from domain; all property queries must be scoped to that tenant via RLS (AI path must include tenant_id in vector query – anti‑leak guard).
Notes / Open Questions
- Pagination vs. infinite scroll (FR4.5) – recommendation: numbered pagination.
- Match‑score badge: show raw % or qualitative label? (open).
- Map provider not chosen (cost/API‑key implications).
- “Location” filter: free‑text vs. fixed taxonomy vs. radius (no locality table).

---
3. Property Details (/property/:id) – 03-property-details.md

Purpose – Conversion page: help visitor picture living there, assess affordability, and contact an agent in one tap; also show similar properties.
Layout / Regions
HEADER (logo, nav, back arrow)
← Back to results
MAIN AREA
  LEFT COLUMN
    GALLERY (hero image + thumbnail strip; favorite heart overlay)
    TITLE BLOCK (title, type, beds/baths/area, price, status badge)
    TABS
      Overview (description + price breakdown)
      Amenities (list/check‑boxes)
      Floor Plan (image or “no floor plan”)
      Location (map + landmarks)
      EMI Calculator (client‑only)
  RIGHT COLUMN (sticky on scroll)
    CTA CARD
      Price, price‑per‑sqft
      Primary: Schedule Visit
      Secondary: Request Callback
      Agent badge (avatar, name, phone) – falls back to tenant contact


Components – ImageCarousel/Gallery, FavoriteHeart, TitleBlock, Tabs, PropertyCard‑like Amenities list, MapComponent, EMICalculator (plain JS), CTAButton (primary/secondary), AgentInfoCard, SimilarPropertiesCarousel.
Interaction Flow
1. Mount → GET /properties/{id} (published only) → populate gallery, title block, tabs (all tab data in same payload).
2. Mount → GET /properties/{id}/similar → populate carousel (non‑fatal if fails).
3. Tab switch → client‑only (no extra fetch).
4. Heart toggle → optimistic POST/DELETE /properties/{id}/favorite.
5. Click “Schedule View” or “Request Callback” → open Lead‑Capture modal (see feature 15).
  - Submit → POST /leads (source=property_details, property_id attached) or POST /leads/callback-request (add time‑slot).
  - On success → show inline confirmation, change CTA to “Inquiry sent ✓” (disabled).

6. Click Similar card → navigate to its /property/:id.
7. Open chat with context → POST /ai/chat/message with property_id.
States – Loading (skeleton gallery + title), Partial data (hide missing tabs: floor‑plan, map, amenities; show agent fallback if none; placeholder images), Not‑found / soft‑deleted (friendly 404 with “Browse similar”), Sold/On Hold (status badge, CTAs replaced with “No longer available – see similar”), Duplicate submit guard (button disabled + server‑side idempotency), Logged‑in (pre‑filled lead form, favorite persists to account).
API Calls

- GET /properties/{id}
- GET /properties/{id}/similar
- POST /properties/{id}/favorite / DELETE …
- POST /leads (message) / POST /leads/callback-request (callback)
- POST /ai/chat/message (when chat opened from here)
Permissions / Tenancy – Fully anonymous. The GET /properties/{id} endpoint must 404 if the record belongs to a different tenant than the request’s domain (anti‑ID‑guessing). Agent PII limited to name & business phone only.
Notes / Open Questions
- Price breakdown (FR5.1) – schema has only a single price column → either drop requirement or add structured price columns first.
- Nearby landmarks (FR5.1) – no data source; decide manual entry vs. Places API.
- “Schedule Visit” – does it need a real availability calendar or just a requested time (slot currently has no storage – see feature 15).
- Default EMI interest rate – hard‑coded, tenant‑configurable, or user entered only?

---
4. Requirement Analysis Wizard (/requirement-analysis) – 04-requirement-wizard.md

Purpose – Help visitors who can’t articulate a search query; five easy questions → ranked shortlist with plain‑language match reasons (the third USP).
Layout / Regions
HEADER (logo, nav)
PROGRESS BAR – 5 steps, current highlighted, completed steps show check
QUESTION AREA – one question per step, large tap‑target option cards (single‑select) or multi‑select chips (amenities)
NAVIGATION – ← Back (always enabled unless step 1), → Next (disabled until selection, unless skippable), “Skip this step” link (on non‑essential steps)
Results View (after final step)
HEADER – “We found X homes that fit.” + [Edit my answers]
MATCH CARDS (image, title, price, beds/area, score line, ✓/✗ reason lines)
SAVE PROMPT (anon only) – “Create an account and we’ll alert you when a new match is listed.” + [Sign up]
Components – ProgressBar, QuestionHeader, OptionCard (single‑select), MultiSelectChipGroup, BackButton, NextButton, SkipLink, MatchCard (image, title, price, score, reason list), SavePrompt, SignUpButton.
Interaction Flow
1. User starts wizard → all answers kept in local client state (no backend calls until submit).
2. For each step: select option(s) → enable Next (unless step skippable).
3. On final step → Submit → POST /ai/recommend with {budget_min, budget_max, preferred_locations, property_type, purpose, timeline, must_have_amenities}.
4. Backend: persists requirement_profiles (user‑ or session‑scoped), scores candidates using tenant’s ai_config.recommendation_weights, generates match_reason via Bedrock, stores requirement_matches.
5. Response includes requirement_profile_id + matches[] (each with match_score, match_reason).
6. Render scored cards with ✓/✗ reasons (e.g., “✓ Within your budget”, “✗ No gym”).
7. “Edit my answers” → wizard reopens pre‑filled → PUT /ai/recommend/{requirement_profile_id} (update in place, re‑run matching).
8. Click a match card → /property/:id.
9. Anonymous user → after results see Save Prompt → sign‑up flow → on account creation, session profile re‑keyed to user_id.
States – In‑progress (answers survive back‑button within wizard), Submitting (full‑screen loading spinner with honest copy), Results – strong matches (ranked cards with reasons), Results – weak/no matches (closest‑match fallback + CTA to widen criteria), Bedrock failure (still show deterministic list, generic reasons), Rate‑limited (same as Bedrock failure), Total failure (retry + link to listings with answers mapped to filters), Logged‑in (no save prompt, profile auto‑saves).
API Calls

- POST /ai/recommend (create)
- PUT /ai/recommend/{requirement_profile_id} (update)
- GET /ai/recommend/{requirement_profile_id} (portal – view saved profile)
- DELETE /ai/recommend/{id} – missing (gap G6)
Permissions / Tenancy – Anonymous full experience; login only persists it. Tenant data isolation: candidate properties and weighting come strictly from the request‑domain tenant (RLS + app filter). Session‑ID or user‑ID must never be null simultaneously.
Notes / Open Questions
- Shared amenity taxonomy needed (wizard, listing filters, properties.amenities).
- Gap G6: no delete endpoint for requirement profile (FR7.3).
- Progress‑bar navigation: allow jump to any completed step? (open).
- Source of locality chips in step 2 – hard‑coded, distinct location_address, or free‑text only?
- Show raw match‑score % to users or use qualitative label? (same as listing).

---
5. Contact Page (/contact) – 05-contact-page.md

Purpose – Simple, low‑tech path to a human‑agent lead (message or callback request).
Layout / Regions
HEADER
Talk to us – we’ll reply within one business day.
[ CONTACT FORM ]   [ TENANT CONTACT INFO ]
Form fields: Name* , Phone* , Email , Message
Mode toggle: ○ Send a message   ● Request a callback ────┐
                                                    ↓ shows Date & Slot pickers
Submit button

Components – Shared LeadCapture container (name, phone, email, message, mode toggle, date picker, slot picker, submit), TenantContactInfo (address, phone, email, hours, map embed – currently missing data source).
Interaction Flow
1. Page loads – form empty, “Send a message” selected.
2. User fills name, phone (required), optional email, message.
3. If “Request a callback” toggled → show date & slot pickers (client validation: not in past).
4. Submit → client validation (required fields, phone format, message length).
  - On validation failure → inline field errors, no request.
  - On success → button disabled + spinner.
  - If mode = message → POST /leads with source="contact_form"
  - If mode = callback → POST /leads/callback-request (adds requested date/slot).

5. On 201 → replace form with confirmation panel: “Thanks, {name}. An agent will call you on {phone}.”
6. Errors (400/500/network) → show message above button, keep all values; never force re‑type.
States – Default (empty form), Logged‑in (pre‑fill name/phone/email from profile), Validating (inline errors), Submitting (button disabled + spinner), Success (confirmation panel), Error (message above button), Already‑submitted‑this‑session (show gentle note, not a block).
API Calls

- POST /leads (message) – body {customer_name, customer_phone, customer_email, message, source:"contact_form"}
- POST /leads/callback-request – same + requested time slot
- (No endpoint for tenant contact info – gap G1 in this doc)
Permissions / Tenancy – Anonymous. Created lead inherits tenant from request domain (RLS + app filter).
Notes / Open Questions
- Tenant contact info has no home in tenants table → need address/phone/email/hours columns or drop the panel.
- Callback time slot has no storage column in leads → must add before implementing.
- Rate‑limiting / bot protection on POST /leads currently unspecified for non‑AI public endpoints (recommend per‑IP limit + honeypot/CAPTCHA).
- Optional SMS/email confirmation (FR6.3) depends on chosen provider (not yet selected).

---
6. Auth – Register / Login (/login, /register) – 06-auth-register-login.md

Purpose – Unified entry for account creation and password‑based login (email + password). Also handles social/profile‑less guest‑to‑user migration of session‑scoped data (favorites, requirement profiles, chat history).
Layout / Regions
HEADER (logo, nav)
FORM TABS – [ Login ] [ Register ] (highlight active)
FORM FIELDS
  Email*
  Password*
  [Remember me] (login only)
  Full Name* (register only)
  Phone* (register only)
  [I agree to Terms & Privacy] (register only)
SUBMIT button (“Log in” / “Create account”)
FOOTER – links to Forgot password, Resend verification, etc.
Components – Form with toggle tabs, Input fields (email, password, name, phone), Checkbox (remember, terms), Button, FooterLinks.
Interaction Flow
- Login: Submit → POST /auth/login (email+password) → on success receive JWT, set Auth header, redirect to next URL or /portal. On failure → show inline error (invalid credentials).
- Register: Submit → POST /auth/register (email, password, name, phone) → on success → email verification link sent, auto‑log in (or show “check email to verify”), then redirect as above.
- Guest‑to‑User migration (handled automatically after successful login/register):
  - Any rows in favorites, requirement_profiles, chat_conversations keyed by current X‑Session‑Id are re‑keyed to the new user_id.
  - The X‑Session‑Id header is cleared/replaced with the logged‑in user’s session cookie.
States – Idle, Submitting (button disabled + spinner), Success (redirect or message), Error (inline message – invalid credentials, validation errors, email‑already‑exists).
API Calls

- POST /auth/login
- POST /auth/register
- (Password reset / email verification flows are out of scope for this UI prompt but exist in auth spec.)
Permissions / Tenancy – Public endpoints. After login, all subsequent requests include JWT; server resolves tenant_id from the user’s tenant_id claim (or from domain for public‑site routes).
Notes / Open Questions
- Social login (Google/Apple) not yet scoped – leave for post‑MVP.
- Password‑less email link login – out of scope.
- Ensure “Remember me” sets a long‑lived refresh token via secure‑httpOnly cookie (handled by auth layer).

---
7. Customer Portal – Dashboard (/portal) – 07-portal-dashboard.md

Purpose – Logged‑in home that answers “What’s happened since I was last here?” – new matches, replies, price changes on saved items, notification counts.
Layout / Regions
HEADER (logo, search, contact, avatar dropdown)
PORTAL NAV (horizontal tabs with counters)
  ▸ Overview   Favorites 4   Requirements   Inquiries 2   Notifications
WHAT’S NEW (compact unread‑notice banner)
SAVED PROPERTIES (first 4 favorites, newest first) → [See all →]
MY REQUIREMENTS (plain‑text summary + live match count) → [Edit →]
RECENT INQUIRIES (last 2‑3 leads with customer‑friendly stage) → [See all →]
Components – TabBar (with badges), AlertBanner (“What’s new”), PropertyCard (mini), RequirementSummaryCard, LeadSummaryRow (status badge), NotificationItem (icon + timestamp + short text).
Interaction Flow
1. On mount → four parallel requests:
  - GET /portal/favorites (first page only)
  - GET /portal/requirements
  - GET /portal/inquiries (first page only)
  - GET /portal/notifications (unread only) – currently missing/notifications table (gap G1)

2. Each section renders as its data arrives; a slow section never blocks others.
3. Click actions:
  - “View matches” → /portal/requirements
  - Favorite card → /property/:id
  - Requirement summary → /portal/requirements (edit)
  - Inquiry row → /portal/inquiries (expanded view)
  - Notification item → marks read, then deep‑links to its target (e.g., new message, price change).
  - Unfavorite from card → optimistic DELETE /properties/{id}/favorite, card disappears.
States – Loading (per‑section skeleton), First‑time user (no data yet → show onboarding CTAs: “Start by telling us what you’re looking for →” (wizard) and “Or browse listings →”), Empty sections (show relevant CTA or hide if worthless — e.g., hide “Recent inquiries” when none), Error in one section (inline retry, rest of page works), Logged‑out (redirect to login before any render).
API Calls

- GET /portal/favorites
- GET /portal/requirements
- GET /portal/inquiries
- GET /portal/notifications – gap G1 (no notifications table)
- DELETE /properties/{id}/favorite (from card)
All require Authorization: Bearer <jwt>.
Permissions / Tenancy – Two mandatory filters: tenant_id from the authenticated user's record AND user_id = current user. Tenant alone is insufficient – must also scope by user to avoid seeing another customer’s data in the same tenant.
Notes / Open Questions
- Gap G1: notifications table and preferences missing (see 11-portal-notifications.md).
- Blocking: leads has no user_id → inquiry history cannot be built correctly (see 10-portal-inquiries.md §11).
- Gap G4: “Saved Searches” appears in persona flow but no module/table/endpoint – either scope into PRD or remove from persona flow.
- Consider adding a GET /portal/summary endpoint (4 calls → 1) if latency becomes an issue – add to spec first.

---
8. Customer Portal – Favorites (/portal/favorites) – 08-portal-favorites.md

Purpose – Show all properties the current user has favorited, with ability to remove, sort, and navigate to details.
Layout / Regions
HEADER (logo, nav, back arrow)
PAGE TITLE – “My Favorites” + [Sort ▾] (Date added, Price ↓/↑, Newest)
EMPTY STATE – “You haven’t saved any properties yet. Start favoriting from listings.”
LIST / GRID – property cards (image, price, beds/area, favorite heart)
PAGINATION / LOAD‑MORE
Components – PageHeader, SortDropdown, EmptyState, PropertyCard (with unfavorite action), Pagination or LoadMoreButton.
Interaction Flow
1. Mount → GET /portal/favorites?page=&page_size=&sort= (defaults: page = 1, size = 20, sort = date_desc).
2. Changing sort or page → update URL, re‑fetch.
3. Heart toggle on a card → optimistic DELETE /properties/{id}/favorite (remove from list) or POST if re‑favoriting (shouldn’t happen as already favorited, but allow toggle).
4. Click card → /property/:id.
States – Loading (skeleton cards), Empty (show CTA to browse), Error (inline retry, keep previous data if any), Success (list updated).
API Calls

- GET /portal/favorites (with pagination & sort)
- POST /properties/{id}/favorite / DELETE … (toggle)
Permissions / Tenancy – Must filter by tenant_id (from user) AND user_id = current user.
Notes / Open Questions – None specific beyond generic tenant/user scoping.

---
9. Customer Portal – Requirements (/portal/requirements) – 09-portal-requirements.md

Purpose – List all saved requirement profiles, allow edit, delete, view matches, and create new profiles.
Layout / Regions
HEADER (logo, nav, back arrow)
PAGE TITLE – “My Requirements” + [New Requirement] button (opens wizard)
EMPTY STATE – “You haven’t saved any needs yet. Try the Requirement Wizard.”
LIST – each item:
  • Title line (e.g., “3BHK apartment • ₹50‑80L • Whitefield”)
  • Purpose / timeline badges
  • Match count (e.g., “12 current matches”)
  • Actions: [View matches] [Edit] [Delete]
Components – PageHeader, PrimaryButton (New Requirement), EmptyState, RequirementSummaryCard (title, badges, match count, action buttons), Pagination (if needed).
Interaction Flow
1. Mount → GET /portal/requirements (list of profiles with metadata).
2. Click New Requirement → open /requirement-analysis wizard (blank).
3. Click View matches on an item → navigate to /portal/requirements/{id}/matches (see match list page – not a separate spec but implied).
4. Click Edit → open wizard pre‑filled with that profile’s data → on save → PUT /ai/recommend/{id}.
5. Click Delete → confirm → DELETE /ai/recommend/{id} (gap G6 – endpoint missing).
6. After create/edit/delete → refresh list.
States – Loading (skeleton list), Empty (show CTA to start wizard), Error (inline retry), Success (toast “Saved”, “Deleted”).
API Calls

- GET /portal/requirements
- GET /ai/recommend/{id} (to fetch a specific profile for edit) – implied but not listed in spec; you may need to add
- POST /ai/recommend (create) – via wizard
- PUT /ai/recommend/{id} (update)
- DELETE /ai/recommend/{id} (delete) – gap G6
Permissions / Tenancy – Must scope to tenant_id of the user AND user_id = current user (profile ownership).
Notes / Open Questions
- Need a GET /ai/recommend/{id} endpoint to fetch a single profile for editing (not explicitly listed; add to spec).
- Delete endpoint missing (gap G6).

---
10. Customer Portal – Inquiries (/portal/inquiries) – 10-portal-inquiries.md

Purpose – Show all leads (inquiries, callback requests) submitted by the current user, with their current pipeline stage and ability to view details or re‑open chat.
Layout / Regions
HEADER (logo, nav, back arrow)
PAGE TITLE – “My Inquiries” + [Filter ▾] (All, New, Contacted, etc.)
EMPTY STATE – “You haven’t sent any inquiries yet.”
LIST – each item:
  • Property thumbnail + title
  • Status badge (converted to customer‑friendly label: New → “Just sent”, Contacted → “Agent replied”, etc.)
  • Timestamp
  • Actions: [View details] [Chat with agent] [Re‑open conversation]
Components – PageHeader, FilterDropdown (status), EmptyState, InquiryCard (thumb + title + status badge + time + action buttons), Pagination.
Interaction Flow
1. Mount → GET /portal/inquiries?status=&page= (default: all, page 1).
2. Changing filter or page → update URL, re‑fetch.
3. Click View details → navigate to the related /property/:id (if property_id present) or show a generic “Inquiry detail” modal (if no property).
4. Click Chat with agent → open chat widget with context pre‑filled (agent ID from lead).
5. Click Re‑open conversation → same as above (opens existing chat).
States – Loading (skeleton cards), Empty (show CTA to start an inquiry), Error (inline retry), Success (list updated).
API Calls

- GET /portal/inquiries (with optional status filter & pagination)
- (No direct write; leads are created via public endpoints – no mutation needed here.)
Permissions / Tenancy – Must filter by tenant_id (from user) AND user_id = current user. Critical gap: leads table currently lacks a user_id foreign key, so the backend cannot reliably filter by user; this is a blocking issue (see §11 of this file).
Notes / Open Questions
- Add user_id FK to leads (required for correct inquiry history).
- Define mapping from raw pipeline stages (new, contacted, negotiation, won, lost) to customer‑friendly labels for the badge.
- Pagination vs. infinite scroll – choose one and add to spec if needed.

---
11. Customer Portal – Notifications (/portal/notifications) – 11-portal-notifications.md

Purpose – Show all platform‑generated notifications (new matches, price changes, agent replies, etc.) with mark‑as‑read/delete actions and preferences toggle.
Layout / Regions
HEADER (logo, nav, back arrow)
PAGE TITLE – “Notifications”
TOP BAR – [Mark all as read]   [Settings ⚙️]   (settings opens modal for frequency/channel toggles)
EMPTY STATE – “You’re all caught up.”
LIST – each notification:
  • Icon (type: match, price, message, etc.)
  • Short message (e.g., “2 new homes match your criteria”)
  • Timestamp
  • Actions: [Mark as read] [Delete]   (swipe‑to‑delete on mobile)
Components – PageHeader, ActionButton (mark all as read), SettingsIcon (opens modal with toggles for email/SMS/in‑app per category), EmptyState, NotificationItem (icon, text, time, actions), Pagination or InfiniteScroll.
Interaction Flow
1. Mount → GET /portal/notifications?page=&page_size=&unread_only= (default: show unread first, then paginate all).
2. Mark‑as‑read on item → PATCH /portal/notifications/{id}/read (or bulk via “Mark all as read”).
3. Delete → DELETE /portal/notifications/{id} (or swipe).
4. Open settings → toggle switches → PATCH /portal/notification-preferences (save per‑user prefs).
5. Pull‑to‑refresh (if using infinite scroll) → refetch first page.
States – Loading (skeleton items), Empty (“You’re all caught up.”), Error (inline retry, keep previous data if any), Success (toast “Marked as read”, “Deleted”).
API Calls - Currently missing endpoints/notifications table (gap G1):
  - GET /portal/notifications
  - PATCH /portal/notifications/{id}/read
  - DELETE /portal/notifications/{id}
  - PATCH /portal/notification-preferences
Permissions / Tenancy - Must scope to tenant_id (from user) AND user_id = current user.
Notes / Open Questions

- Need to add notifications table and notification_preferences table to 03-database-schema.md (see gaps G1/G2).
- Determine transport for real‑time updates (WebSockets vs. polling) – out of scope for UI but affects payload shape.
- Choose icon set for notification types.

---
12. Static CMS Pages (/:slug) – 12-static-cms-pages.md

Purpose – Render editable marketing pages (About, Terms, Careers, Blog posts) served from the CMS.
Layout / Regions
HEADER (logo, nav)
CONTENT AREA – rich‑text output from CMS (title, body, images, embeds)
FOOTER (global)
Components – RichTextRenderer (supports headings, paragraphs, images, embedded videos, links), PageLayout (optional sidebar for related posts or CTA), Breadcrumbs (if hierarchy).
Interaction Flow
1. On route change → extract :slug from URL.
2. Call GET /cms/pages?slug=:slug (public endpoint, no auth).
3. Render returned HTML/markdown via RichTextRenderer.
4. If 404 → show “Page not found” with link to homepage.
States – Loading (skeleton container), Error (show fallback message + home link), Success (content rendered).
API Calls

- GET /cms/pages?slug=:slug – returns {title, body_html, published_at, author_name} (public, no auth)
Permissions / Tenancy - Public. The CMS endpoint must scope to the tenant identified by request domain (no tenant_id param from client).
Notes / Open Questions
- Need a public CMS read endpoint (currently missing – see 04-api-spec.md gap G5).
- Determine whether the CMS supports versioning/drafts – should only expose published (status='published') pages.
- Handling of assets (images, files) – ensure they are served via the tenant’s subdomain or signed URLs.

---
13. AI Search Widget – Feature (13-feature-ai-search.md)

Purpose – Re‑usable search bar (with voice, autosuggest, clear) that appears in the header of the Homepage and Property Listing page.
Layout / Regions (same as header search described in homepage):
[🔍]  Input field (placeholder: “Describe the home you’re looking for…”)   [🎤] Mic   [✕] Clear
Below the input – autosuggest dropdown (appears on debounced typing).
Components – SearchInput, MicButton, ClearButton, AutosuggestDropdown (list of suggestions with optional icon).
Interaction Flow
- Typing → debounce 250ms → show autosuggest (if endpoint existed) – gap G3 (no endpoint).
- Mic click → Web Speech API → fill input.
- Clear button → clear input, hide suggestions.
- Submit (Enter or button) → navigate to /search?q=<value> (no API call from widget itself).
States – Idle, Focused, Typing (show suggestions if any), Voice‑supported/unsupported (hide mic if not supported), Error (none – failures handled downstream).
API Calls – None directly (the search itself lives on /search page).
Permissions / Tenancy – Inherits from host page.
Notes / Open Questions
- Implement the missing autosuggest endpoint (GET /suggest?q= returning array of strings) and add to 04-api-spec.md before using.
- Voice fallback: if browser lacks SpeechRecognition, hide mic button (don’t show a broken icon).

---
14. AI Chatbot Widget – Feature (14-feature-ai-chatbot.md)

Purpose – Persistent floating chat bubble that opens a messenger‑style conversation with the PropVista AI assistant (capable of property lookup, lead capture, escalation).
Layout / Regions
Bubble (fixed bottom‑right, ≥44×44 px):
  [💬]  (avatar or icon)  – tapping opens the chat pane
Chat pane (slides up from bottom or appears as modal):
  Header: [← Back]   “Assistant”   [⋯ More] (menu: Clear chat, View history)
  Message list:
    • Bot message (avatar left, bubble with accent‑tint from DESIGN.md tertiary)
    • User message (avatar right, bubble with background‑neutral)
  Input box:
    [📎 Attachment]  Text area  [↑ Send]
Optional header actions – “View chat history” (opens modal with paginated list), “Clear chat”.
Components – ChatBubble, ChatHeader, MessageBubble (user/bot), InputArea (text field, send button, attachment icon), ScrollView, Timestamp, ActionMenu.
Interaction Flow
1. Page loads → chat icon rendered; no connection yet.
2. Tap bubble → chat pane opens; if there’s existing history (from session or user) → load via GET /ai/chat/history?session_id=… or GET /ai/chat/history?user_id=….
3. User types message → send icon → POST /ai/chat/message with {message, session_id (or user_id), tenant_id (implicit via domain)}.
4. Bot streams response (Server‑Sent Events or chunked JSON) – each chunk appended to the message list.
5. If the bot invokes a tool (e.g., property lookup, lead creation) it returns a structured action; the client:
  - Shows a property card (tap → /property/:id)
  - Shows a lead‑capture modal (same as property‑details CTA) – on submit → POST /leads (source=chatbot).
  - If user asks “talk to a human” → trigger escalation flow (POST /ai/chat/escalate) which creates a lead with source=chatbot_escalate and notifies agent.

6. On new message arrival while chat is closed → badge increment on bubble.
7. User can swipe‑left on a message to delete (only own messages) → DELETE /ai/chat/message/{id}.
8. Settings (•••) → toggle notifications, clear history, view transcript.
States –

- Closed (badge shows unread count).
- Open – Loading (show skeleton bubbles while waiting for first bot reply).
- Empty state (first message from bot – greeting).
- Error (show retry button, keep conversation).
- Input disabled while sending.
Permissions / Tenancy –
- All chat endpoints require either a valid session_id (anonymous) OR user JWT (if logged in) – the backend resolves the tenant from the request domain and enforces that all messages belong to that tenant.
- No tenant_id sent by client; it is derived server‑side.
Notes / Open Questions
- Need to decide on transport for streaming response (SSE vs. JSON lines) – must be defined in 04-api-spec.md for /ai/chat/message.
- Escalation endpoint (POST /ai/chat/escalate) and its payload shape should be explicit in the spec.
- File attachments (if allowed) need upload endpoint and virus‑scan policy – currently out of scope.
- message retention / GDPR purge strategy – out of scope for UI but impacts history endpoint.

---
15. Lead Capture Feature – (15-feature-lead-capture.md) – Used as a modal or inline component

Purpose – Unified small form for capturing a lead (name, phone, email, message, optional property/context, source, callback slot). Appears as:
- Inline on Contact page
- Modal from Property Details CTA (Schedule Visit / Request Callback)
- Modal from Chatbot (on lead‑capture tool)
- Embedded in other places (e.g., after requirement‑wizard save prompt).
Layout / Regions (modal)

HEADER – “Get in touch” (or “Schedule a visit”, “Request a call”)
FORM
  Name *
  Phone *
  Email
  Message / Details (textarea)
  [Optional] Property context (read‑only line: “Regarding: Sunview Residences • ₹78L • 3BHK”)
  [Optional] Callback selector – appears when mode = callback:
       Date [ ▼ ]   Slot [ ▼ ]
  Submit button (primary)
  Secondary link: “Just sending a message” (toggles back to message‑only mode)
FOOTER – link to Privacy Policy
Components – Input fields (text, tel, email, textarea), Radio/Toggle for mode, Date picker, Time‑slot dropdown (representing predefined agent windows), SubmitButton, SecondaryLink.
Interaction Flow
1. Open → fields empty, mode defaults to “Message”.
2. Fill required name & phone; optional email/message.
3. If switch to “Callback”: show date & slot pickers (client validation: not in the past).
4. Submit → client validation (required fields, phone format, if callback → date+slot present).
  - On failure → inline field errors, no request.
  - On success → button disabled + spinner.
  - POST /leads (message mode) or POST /leads/callback-request (callback mode) with fields:
   customer_name, customer_phone, customer_email, message, property_id (if known), source (values: contact_form, property_details, chatbot, chatbot_escalate, etc.).

5. On 201 → show inline confirmation (“Thanks, {name}. An agent will contact you.”) and change submit button to a disabled “Message sent ✓”.
6. On error (400/500/network) → show message, keep form values, re‑enable button.
States – Idle, Validating (inline), Submitting (button + spinner), Success (confirmation toast + disabled button), Error (message above button).
API Calls

- POST /leads
- POST /leads/callback-request
- (Optional) GET /leads/{id} – not needed for this component.
Permissions / Tenancy – Anonymous allowed; created lead inherits tenant from request domain (RLS + app filter). If a property_id is present, the backend must verify it belongs to the same tenant (else 404).
Notes / Open Questions
- Need to add requested_callback_at and requested_slot columns to leads (currently missing – see the leads table schema in 03-database-schema.md).
- Define the set of allowed callback slots (e.g., 30‑min windows during business hours) – could be static or admin‑configurable.
- Rate‑limit / bot‑protect this endpoint (same as POST /leads – currently unspecified for non‑AI endpoints).

---
16. Session‑Persistence / Favorites Feature (16-feature-favorites-session.md)

Purpose – Describes how anonymous favorite hearts (session‑scoped) migrate to the user account on login/register, and how the UI should behave.
(No distinct UI to generate – it’s a behavior that lives in other components: favorite heart on property cards, portal favorites list, etc.)
Key Points for UI Implementation
- Heart toggle on any property card (homepage, listing, details, portal favorites, similar‑items carousel) must:
  a. Optimistically toggle UI (filled ↔ outline).
  b. On success → if the user is logged in, persist to favorites table (user_id set); if anonymous, store/update row keyed by session_id.
  c. On failure → revert UI optimistically and show a transient toast (“Couldn’t save favorite – try again”).

- On successful login or register (after receiving JWT), the frontend must:
 a. Send a background request to POST /favorites/migrate (or call the appropriate backend route) that re‑keys all rows with the current session_id to the new user_id.
 b. Clear the session_id cookie/storage (or keep it for anonymous‑only actions).
 c. Refresh any UI showing favorites (e.g., header heart badge, portal favorites list).
- The heart should never show a loading spinner that blocks the UI – optimistic update + possible rollback keeps the experience fluid.
Components – Re‑uses the PropertyCard favorite heart (already defined in other components).
Interaction Flow – See above; no additional standalone UI needed.
API Calls (implied)
- POST /properties/{id}/favorite / DELETE … (same as before) – backend must inspect X-Session-Id OR Authorization header to decide target table.
- POST /favorites/migrate (internal) – runs after login/register to move session_id → user_id rows.
Permissions / Tenancy – Same as favorite toggle elsewhere: must scope to requesting tenant.
Notes / Open Questions
- Ensure the migration endpoint exists and is idempotent (safe to call multiple times).
- If a user logs out, optionally clear the session‑specific favorites (or keep them for next anonymous session) – product decision pending.

---
✅ How to Use These Prompts

1. Copy the prompt for the screen you need.
2. Paste it into your AI‑design tool (e.g., Google Stitch “Create from description”).
3. Iterate – the tool will emit a UI skeleton (JSX/TSX or HTML/CSS).
4. Replace any placeholder text with the exact copy from the spec (the prompts already contain the exact wording where relevant).
5. Run the existing linters/formatters (prettier, eslint, black, ruff) to bring the generated code into the repo’s style.
6. Write the accompanying tests (unit + integration) as prescribed in docs/09-coding-standards.md §5 and the sprint’s TC-* tables.
7. Run the self‑checklist in docs/09-coding-standards.md §8 before considering the feature complete.

When you encounter an open question (marked with [G# or a bracketed note), pause implementation, update the owning spec document first (e.g., 04-api-spec.md, 03-database-schema.md, 01-prd.md), then continue. This keeps the codebase and documentation in lockstep as required by the project’s workflow.


# Admin Portal Screens
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
  Button gradient               #3525c
  Secondary text                #464555
  PRIMARY — high-intent actions #3525cd   (buttons, focus rings, active nav)
  Button gradient               #3525cd → #0058be
  Primary tint (selected/hover) #e2dfff
  TERTIARY — the AI layer       #571ac
  Dark / terminal               #213145   (text on it: #eaf1ff)
  STATUS success                #c3f0d
  STATUS warning                #ffddb0 fill / #2c1700 text
  STATUS error / urgent         #ffdad6 fill / #93000a text  (strong: #ba1a1a)
  STATUS neutral                #e2e1e

THE ONE RULE THAT MATTERS MOST — read it twice:
  #571ac0 tertiary violet marks AI-GENERATED OUTPUT AND NOTHING ELSE.
  In this portal that is exactly: the Chatbot and AI Search lead-source chips,
  the two AI bars in the dashboard chaD TOOL CALLS
  in a transcript.
  It is NOT for: nav, focus rings (thous chips,
  buttons, or a HUMAN AGENT'S CHAT REPLY. A human wrote that.

STATUS IS NOT BRAND: never use primary/secondary/tertiary to mean a status.
  Status uses the four status colors above and ALWAYS carries a text label.

TYPE: Plus Jakarta Sans throughout. NO MONOSPACE, NO SERIF — every price,
  percentage and table figure is Plus Jakarta Sans, right-aligned, aligned on
  the digit.
  Page heading 30/600 · Section 24/60000 ·
  Table cells & labels 14/600 · Caption 12/500

SHAPE: Cards 24px radius. Buttons, inputs, table containers 12px. Chips fully
  rounded. Nothing sharp.

DEPTH: One ultra-soft shadow for floating elements: 0 10px 30px
  rgba(11,28,48,0.04). 1px #c7c4d8 haissmorphism
  (20px blur + rgba(255,255,255,0.7)) on slide-in panels.

COMPONENTS:
  Buttons — 48-56px, 12px radius. Primary = gradient, white text. Secondary =
    outlined 1px #3525cd. Text = #4645
  Inputs — #eff4ff fill, no border at rest, 2px #3525cd ring on focus. EVERY
    field has a VISIBLE LABEL above itabel.
  Tables — the workhorse. NO zebra striping, NO heavy row borders. Separate rows
    with vertical space and a #eff4ff mbers right.
  Icons — line style, 1.5px stroke.

══════════════════════════════════════
PART 2 — SHARED FURNITURE
═══════════════════════════════════════════════════════════════

SIDEBAR (every screen): a fixed left rail ~240px. PropVista logo at top, the
  tenant's business name beneath it in 12px #464555 (a label, not a brand). Nav
  rows with line icons: Dashboard · Prnts ·
  Users · AI Config · Reports · Settings.
  The Chat row carries a COUNT BADGE when people are waiting — it is the one
  nav item allowed to shout, because s
  Active row = #e2dfff tint, #3525cd text and icon.

STATUS CHIPS — fully rounded, pale fil, ALWAYS with
  a text label:
    Property: Draft #e2e1ec/#1a1a24 · Pending Approval #ffddb0/#2c1700 ·
              Published #c3f0da/#00522
              Rejected #ffdad6/#93000a · On hold / Archived #e2e1ec/#1a1a24
    Lead:     New #e2e1ec/#1a1a24 · Contacted / Site visit / Negotiation
              #e2e1ec/#1a1a24 · Won #c3f0da/#00522f · Lost #e2e1ec/#1a1a24

LEAD-SOURCE CHIPS — the AI-derived ones get tertiary; the rest do not:
    💬 Chatbot  #e9ddff / #571ac0   ← AI
    🔍 AI Search #e9ddff / #571ac0  ←
    📋 Requirement · 📝 Contact form · 🚶 Walk-in   #e5eeff / #464555

THE RED FLAG — #ba1a1a, used ONLY for unassigned
  stale lead, an escalated chat waiting for a human, a high-risk audit entry.
  If everything is flagged, nothing is.

═══════════════════════════════════════════════════════════════
PART 3 — THE 10 SCREENS
═══════════════════════════════════════════════════════════════

SCREEN 1 — DASHBOARD (/admin/dashboard
Top row: four KPI cards — Total Listings · Active Leads · Conversion Rate ·
Site Visitors. Each a white bento card: a 14px #464555 label above a 30px
semibold #0b1c30 number.
Two columns below. LEFT: a line chart  primary
#3525cd. RIGHT: a horizontal bar chart "Lead Source Breakdown" — Chatbot, AI
Search, Requirement Form, Contact Formsources are
drawn in TERTIARY #571ac0; the other three in primary. That contrast IS the
chart's purpose: it shows whether the  cost.
Below: "Recent Activity" — a borderless feed, icon + one line + timestamp,
#eff4ff hover tint. Escalated chats in1a1a —
they are the only genuinely time-sensitive item on the page.

SCREEN 2 — PROPERTIES LIST (/admin/pro
A data table in a white bento container. Columns: Photo (rounded thumb) · Title ·
Type · Price (right-aligned, 24px semibold) · Status (chip) · Agent · Actions.
Above it: a search field, filter dropdrimary button
top-right. When rows are checked, a bulk-action toolbar appears above the table:
"Approve Selected" · "Feature Selected" · "Archive Selected".
No zebra stripes. No heavy row borders

SCREEN 3 — ADD / EDIT PROPERTY (/admin/properties/new)
A multi-step form in a centered white  indicator
across the top: Basic Info · Media · Pricing · Amenities · Location — current
step in primary #3525cd, completed steps with a check.
Show "Basic Info": Title · Descriptiondropdown) ·
Listing Type (Buy/Rent segmented toggle) · Bedrooms and Bathrooms (number
steppers). All #eff4ff fill, visible labels, 2px #3525cd focus ring.
Foot: "Save as Draft" text button left.

SCREEN 4 — BULK UPLOAD (/admin/properties/bulk-upload)
Three numbered steps.
① Download the template — a card with a "⬇ property-template.csv" outlined
button and the line "Column definition."
② Upload — a large dashed dropzone, 24px radius, #eff4ff fill: "Drop a .csv or
.xlsx here — or browse".
③ Review — the important one. A summary strip: "142 rows · 128 valid · 14 need
attention" with the valid count in #00 #2c1700.
Below it an error table — Row / Title / Issue — with issues in PLAIN LANGUAGE:
"price is not a number: 'on request'" own amenity:
'swiming pool' — did you mean 'swimming_pool'?"
Two buttons: "⬇ Download the 14 failed rows" (outlined) and "Import the 128 valid
rows as drafts" (primary).
PARTIAL IMPORT IS THE POINT. Never make someone fix 14 rows before they get any
value from the other 128.

SCREEN 5 — APPROVALS QUEUE (/admin/pro
The property list filtered to Pending Approval, beside a review panel. Each
queued item shows everything a revieweving: photos,
price, specs, the submitting agent.
Two actions per item: "Approve & Publiutlined,
#ba1a1a text). Rejecting reveals a REQUIRED reason field — a rejection with
no reason is a dead end for the agent who submitted it.

SCREEN 6 — LEADS KANBAN (/admin/leads)
Five columns: New · Contacted · Site Visit Scheduled · Negotiation · Closed. Each
header carries the stage name and a co
Lead cards: customer name (14px semibold) · a SOURCE CHIP (tertiary for Chatbot /
AI Search, neutral for the rest) · the property they want (one line, truncated) ·
the assigned agent's round avatar · a
UNASSIGNED leads show a loud highlighted "—" where the avatar would be, and a
stale one carries the red dot. An unassigned lead is nobody's responsibility and
must be impossible to miss.
Show one card MID-DRAG between Contacted and Site Visit, lifted with the soft
shadow, slightly scaled.

SCREEN 7 — LEAD DETAIL (slide-in panel)  ← this is the "customer" view
A glassmorphic panel sliding from the right, 32px padding.
Top: the customer — name, phone, emailk-to-email.
Then the source chip, and the property they asked about.
Then their own message, in a tinted #eff4ff inset panel.
Then an ACTIVITY TIMELINE — a thin #c7c4d8 vertical line with dated entries;
completed steps are filled #3525cd dots, future steps hollow #c7c4d8.
Then a notes textarea, a "Set follow-up reminder" date picker, and a primary save
button.
IF THE LEAD CAME FROM AN ESCALATED CHAT, flag it hard in #ba1a1a with a
"View conversation →" link straight to the Chat Console. Someone may be waiting
in that chat right now — it must not look like every other lead.

SCREEN 8 — LEADS TABLE (/admin/leads?view=table)
The same data, dense and sortable. A [Kanban][Table] toggle at top and an
"Export CSV" button.
Filters: search by name/phone, plus Stage · Agent · Source · Created-date.
Columns: checkbox · Name · Source (chip) · Property · Stage (chip) · Owner ·
AGE · row menu.
THE AGE COLUMN IS THE POINT — days since creation, red dot when stale. It is
the column a manager sorts by, and it is what surfaces the leads quietly rotting.
Make it prominent. Unassigned owners sa blank.
Checked rows reveal a bulk bar: "Assign to [Meera ▾] [Apply]" · "Change stage".

SCREEN 9 — AI CHAT LOGS (/admin/ai-conreview
A summary strip: "312 conversations · 58 leads (18.6%) · 41 escalated (13.1%) ·
12 flagged". The escalation rate is the number to watch — a rising one means
the bot is failing.
Filters: Status · Outcome · "Flagged only".
A table: When · Msgs · Outcome (chip: Lead created = success, Escalated = error,
Abandoned = neutral) · first-message preview · flag icon.
ESCALATED-AND-UNHANDLED ROWS ARE VISUALLY LOUD (#ffdad6 / #93000a).
Below, the TRANSCRIPT panel. Visitor marry the
TERTIARY treatment — they are model output. Tool calls render INLINE as small
tertiary-tinted chips above the bot's reply:
    [🔧 lookup_property(property_id: "
That inline tool call is how you verify the bot used live data instead of
inventing it.
Foot: "⚑ Flag for review" · "View the lead →".

SCREEN 10 — AGENT CHAT CONSOLE (/admin/chat)   ★ THE REAL-TIME ONE
This is where the chatbot's promise comes true. The bot tells a visitor "I've
looped in one of our agents" — this is

THREE-COLUMN layout: sidebar · queue · conversation.

QUEUE (middle, ~320px): a header "⚠ 3 waiting". Below, cards for each escalated
conversation, UNCLAIMED FIRST, SORTED
  · visitor name (14px semibold)
  · WAITING TIME — the most important  and it
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
    🤖 BOT — TERTIARY #571ac0 treatmenalls inline:
         [🔧 lookup_property(id: "a3f…")]
    🙋 AGENT — NEVER TERTIARY. A humanme
         ("Anjali"), and give it a clearly human treatment — a primary-tinted
         bubble with the agent's avatar.
  A divider marking the handoff: "── e
  Composer at the foot: a text input with a send button. It is DISABLED and
  visibly greyed until you have claimed this conversation.
  Below it: "Close conversation" (outlined, #464555).

⚠️ THE MOST IMPORTANT THING ON THIS SCthe agent's
messages MUST NOT look the same. Tertiary violet means "a machine generated
this." If a human agent's reply is paieen is lying
about who is talking — on the one screen whose entire purpose is to show a
worried customer that a real person ha

Also render TWO small states:
  (a) EMPTY QUEUE — "No one's waiting. is the normal
      state and it should feel like it.
  (b) CLAIM RACE LOST — a quiet inline message, "Ravi picked this one up", and the
      queue refreshes. NOT an error toe" at the same
      moment is a normal race, not a failure.

═══════════════════════════════════════════════════════════════
FINAL CHECKS — what most often goes wrong
══════════════════════════════════════
1. TERTIARY VIOLET #571ac0 appears ONLY on: the Chatbot / AI Search source chips,
   the two AI bars in the dashboard chart, and THE BOT'S messages and tool calls.
   NOT on nav. NOT on focus rings. NOTons.
   NOT on a human agent's chat reply.
2. NO MONOSPACE, NO SERIF. Every price, percentage and figure is Plus Jakarta
   Sans, right-aligned, aligned on the
3. TABLES ARE THE PRODUCT. No zebra stripes, no heavy borders — spacing, a sticky
   header, a hover tint. Dense but never cramped.
4. THE RED FLAG STAYS RARE. Only genuiigned stale
   lead, an escalated chat waiting for a human, a high-risk audit entry.
5. WAITING TIME on Screen 10 is the single most important number in this portal.
   Everywhere else a stale view costs son is sitting
   in a chat window right now.