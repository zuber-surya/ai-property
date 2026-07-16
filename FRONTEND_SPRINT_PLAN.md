# Frontend Sprint Plan — PropVista CRM UI Development with Stitch

> **Extended frontend-specific guidance** for building the two React surfaces (public site + admin portal) using Google Stitch for rapid UI generation and iteration.
>
> **Status:** v1.0 · **Last updated:** 2026-07-14  
> **See also:** `docs/15-development-plan.md` (overall phases), `docs/16-customer-spec/` (public site specs), `docs/17-admin-spec/` (admin specs), `docs/DESIGN.md` (design tokens)

---

## 1. Frontend Architecture & Tools

### 1.1 Two Independent React Apps (Vite + TypeScript)

| App | Path | Stack | Purpose | Users |
|---|---|---|---|---|
| **Public Site** | `public-site/` | React 18 + Vite + TS + TailwindCSS | Homepage, search, property details, requirement wizard, chat, customer portal | Visitors + registered customers |
| **Admin Portal** | `admin-portal/` | React 18 + Vite + TS + TailwindCSS | CRM back office for agents, admins, super admin | Agents, tenant admins, platform super admin |

**Both apps:**
- Share the same folder structure: `pages/`, `components/`, `hooks/`, `api/`, `context/`, `styles/`
- Use TailwindCSS for styling (configured to match `docs/DESIGN.md` tokens exactly)
- Strict TypeScript (no `any` without inline justification)
- Function components + hooks only
- API client functions grouped by domain in `api/` (e.g. `api/properties.ts`, `api/leads.ts`)

### 1.2 Stitch Integration in Your Workflow

**What Stitch does:** Generates high-fidelity React components directly from natural-language descriptions + design system context.

**When to use Stitch:**
- ✅ First draft of a complex new screen (search, Kanban, multi-step form)
- ✅ Rapid exploration of layout options
- ✅ Generating component skeletons with proper structure
- ❌ NOT for small tweaks or bug fixes (faster to edit by hand)
- ❌ NOT for custom business logic (you wire that in after)

**The workflow:**

```
1. Read the spec file (docs/16-customer-spec/*.md or docs/17-admin-spec/*.md)
2. Open the relevant design system section (docs/DESIGN.md + colors/type/spacing)
3. Paste this into Stitch:
   - Full DESIGN.md (frontmatter + prose) to establish the theme
   - The Stitch prompt from docs/11-stitch-design-prompts.md OR a custom detailed description
4. Stitch generates a React component
5. Export component as .tsx, paste into your `components/` or `pages/` folder
6. Wire in:
   - API calls (call the service layer via `api/` modules)
   - State management (useState / useReducer / Context)
   - Form validation
   - Error handling & loading states
7. Test against the spec's acceptance criteria
8. Code review (linting, type safety, tenant scoping)
```

---

## 2. Frontend Sprint Breakdown (Aligned with `docs/15`)

### Phase 0: Sprint 0 — Skeleton & Tooling (Weeks 1–2)

**Objective:** Both React apps are scaffolded, linted, and deployable; developers have a clear local dev setup.

#### Tasks:

**2.0.1 — Public Site Scaffold**
- Scaffold `public-site/` with Vite + React 18 + TypeScript
- Folder structure: `src/pages/`, `src/components/`, `src/hooks/`, `src/api/`, `src/context/`, `src/styles/`, `src/types/`
- Install & configure:
  - TailwindCSS (map tokens from `DESIGN.md` to Tailwind config)
  - ESLint + Prettier (use `frontend.md` style rules from `.claude/rules/`)
  - Vitest + React Testing Library for unit tests
  - `vite.config.ts` with API proxy to `http://localhost:8000` for backend calls

**2.0.2 — Admin Portal Scaffold**
- Same as 2.0.1, but folder at `admin-portal/`
- Additional: Role-based access control (RBAC) context setup (placeholder for auth + role checks)

**2.0.3 — Shared Design System (TailwindCSS Config)**
- Create `shared-design.config.js` or equivalent
- Map every `DESIGN.md` token to Tailwind:
  - Colors: generate `colors: { primary, secondary, tertiary, ... }` **from `docs/DESIGN.md`** — never hand-type a hex here (`OWNERSHIP.md` §3)
  - Typography: Tailwind theme extensions for `display-lg`, `headline-md`, `body-md`, `label-md`, etc.
  - Spacing: Tailwind theme spacing based on 8px base (`spacing: { 1: "8px", 2: "16px", ... }`)
  - Border radius: `borderRadius: { sm: "4px", md: "12px", lg: "16px", xl: "24px", full: "9999px" }`
- Both apps import this config so colors/type/spacing are 100% synchronized

**2.0.4 — Auth Context & Session Handling**
- Create `src/context/AuthContext.tsx` (provider for user + tenant data)
- Create `src/hooks/useAuth.ts` to read auth context
- Placeholder for JWT token handling (actual auth wiring happens in Sprint 1)
- Session-ID (`X-Session-Id`) header setup for anonymous users

**2.0.5 — API Client Scaffold**
- Create `src/api/client.ts` — base axios/fetch setup with:
  - Automatic `Authorization: Bearer <token>` header (from AuthContext)
  - Automatic `X-Session-Id` header for anonymous users
  - Error handling → standardized error toasts
- Stub out domain modules:
  - `src/api/properties.ts` (placeholder for `getProperties()`, `getPropertyById()`, etc.)
  - `src/api/leads.ts`, `src/api/auth.ts`, `src/api/users.ts`
  - Each module exports typed functions that call the backend

**2.0.6 — Local Dev & Deployment Smoke Test**
- Both apps run locally: `npm run dev` → Vite dev server on `:3000` (public) and `:3001` (admin)
- CI/CD skeleton (GitHub Actions or equivalent):
  - Lint check: `npm run lint`
  - Test run: `npm run test`
  - Build check: `npm run build`
- One test app deployed to staging (e.g., public site to `https://staging-public.propvista.app`)
- Smoke test: can load the app, auth context loads without crashing

**Acceptance Criteria (Sprint 0):**
- [ ] Both apps scaffold without build errors
- [ ] `npm run dev` works locally on both; can make a request to `/health` on the backend
- [ ] Tailwind config maps all `DESIGN.md` tokens
- [ ] Linter passes with zero warnings
- [ ] CI pipeline runs on a test commit; all checks pass
- [ ] One app deployed to staging; responds with 200

---

### Phase 1: Sprints 1–4 — Core Customer & Admin CRM (Weeks 3–10)

#### Sprint 1 — Public Site: Homepage + Navigation (Week 3)

**Objective:** The first page a customer sees is beautiful, on-brand, and wired to the backend.

**Dependencies:** Backend auth endpoint + GET `/properties` (trending/featured) working.

**Tasks:**

**2.1.1 — Navigation Bar (Shared Across All Public Pages)**
- Create `src/components/Navbar.tsx` — glassmorphic (from `DESIGN.md` Depth section), logo, nav links, auth buttons
- Behavior:
  - Logged-out: shows "Sign In" link + "Register" button
  - Logged-in: shows user initials + dropdown (Profile, Favorites, Inquiries, Logout)
  - Sticky to top, z-index above main content
- **Stitch approach:** Use Stitch prompt from `docs/11-stitch-design-prompts.md` §0 (shared nav), then refine by hand

**2.1.2 — Homepage Hero & Featured Properties**
- Page: `src/pages/Homepage.tsx`
- Sections (from `docs/16-customer-spec/01-homepage.md`):
  1. Hero section: AI search bar (natural-language placeholder) + voice icon + quick-filter chips below
  2. Featured Properties grid: 6 property cards (3 columns, responsive)
  3. Floating AI chat bubble (bottom-right)
- **Stitch approach:** Paste full `DESIGN.md` + `docs/11-stitch-design-prompts.md` §1 prompt → get component → wire in API calls
- **API calls:**
  - `GET /api/v1/properties?featured=true&limit=6` → populate Featured grid
- **State:**
  - `useState(searchText)` for search bar input
  - `setIsSearching()` for loading state while query sends
- **Error handling:** If featured properties fail to load, show a skeleton or graceful "Unable to load featured properties"
- **Testing:**
  - Render test: all sections visible on page load
  - Integration test: featured properties fetch and render with real data

**TC-FEAT-01:** Homepage loads within 2s (LCP target from `12-srs.md` NFR-PERF-1).

**2.1.3 — AI Search Bar (Extracted Component)**
- Component: `src/components/SearchBar.tsx`
- Behavior:
  - Text input + voice icon + submit button
  - Placeholder text changes dynamically (random examples)
  - On submit → navigates to `/search?q={searchText}` with query param
  - Voice icon clicked → (mic integration) records audio, sends to backend `/ai/search/voice`
- Reused on: Homepage, Property Listing header
- **Stitch approach:** Derive from homepage Stitch output, extract to component

**2.1.4 — AI Chatbot Bubble**
- Component: `src/components/ChatWidget.tsx` (floats bottom-right)
- Behavior:
  - Collapsed state: small circular button with chat icon
  - Click → expands to full chat window
  - Chat history managed in component state (persisted to session storage for the visit)
  - Send message → POST `/api/v1/ai/chat/message` → stream response
  - "Talk to an agent" button at bottom (marks conversation for escalation)
- **Stitch approach:** Use `docs/11-stitch-design-prompts.md` §2
- Mounted globally in `src/App.tsx` so it appears on every route

**Acceptance Criteria (Sprint 1):**
- [ ] TC-FEAT-01: Homepage LCP < 2s
- [ ] Featured properties grid renders with real data from backend
- [ ] Search bar navigates correctly to `/search`
- [ ] Chat widget opens/closes; can type a message
- [ ] All text uses correct typography tokens from `DESIGN.md`
- [ ] All colors use correct tokens (no hex hardcoding)
- [ ] ESLint passes; all TypeScript strict mode

---

#### Sprint 2 — Public Site: Search & Property Details (Week 4)

**Objective:** Visitors can find properties via natural-language search and browse details.

**Dependencies:** Backend `/api/v1/ai/search` endpoint + GET `/properties/{id}` working.

**Tasks:**

**2.2.1 — Property Listing (Search Results) Page**
- Page: `src/pages/PropertyListing.tsx`
- Sections:
  1. Sticky search bar at top (SearchBar component from Sprint 1)
  2. Filter sidebar: property type, price range, bedrooms, location (faceted search)
  3. Results grid: property cards (toggleable between grid, list, map views)
  4. Pagination
- **Stitch approach:** Prompt from `docs/11-stitch-design-prompts.md` or custom "real estate search results page, Material 3, filters on left"
- **API calls:**
  - GET `/api/v1/properties?search_text={q}&filters=...` → results with pagination
  - GET `/api/v1/properties/facets?search_text={q}` → for filter options (price ranges, types available)
- **State:**
  - `useState(filters)` - tracks all active filters
  - `useState(view)` - 'grid' | 'list' | 'map'
  - `useState(page)` - for pagination
  - `useState(isLoading)` - while fetching
- **Error handling:** If search fails, show "No results" or graceful error message
- **Testing:**
  - TC-LIST-01: Multiple filters combined correctly (from `docs/15` test matrix)
  - Render test: all 3 view modes toggle correctly

**2.2.2 — Property Details Page**
- Page: `src/pages/PropertyDetails.tsx` (route `/property/:id`)
- Sections (from `docs/16-customer-spec/03-property-details.md`):
  1. Hero image carousel (responsive, large)
  2. Key facts: price, beds, baths, area, address
  3. Description
  4. Agent contact card + "Request viewing" button
  5. Favorites toggle (heart icon, top-right of hero)
  6. Chat-to-learn button (opens chat widget pre-populated)
  7. Related properties carousel (bottom)
- **Stitch approach:** Paste `DESIGN.md` + property details prompt → generate
- **API calls:**
  - GET `/api/v1/properties/{id}` → full property data
  - POST `/api/v1/leads` (if user submits viewing request) → creates lead
  - POST `/api/v1/favorites` (if user favorites) → persists favorite
- **State:**
  - `useState(property)` + `isLoading`
  - `useState(isFavorited)` - updates when user clicks heart
  - `useState(showViewingForm)` - for modal
- **Error handling:** 404 if property not found; graceful loading skeleton
- **Testing:**
  - TC-DETAILS-01: Page renders with partial data without breakage
  - Favorite toggle persists after page refresh

**2.2.3 — Favorite Hearts (Session + Persisted)**
- Hook: `src/hooks/useFavorites.ts`
- Behavior:
  - Before login: stored in `sessionStorage` (keyed by property ID)
  - After login: synced to backend, persisted in `user_favorites` table
  - API: POST/DELETE `/api/v1/portal/favorites/{property_id}`
- Wired into: property cards (all pages), Property Details page hero
- **Testing:** TC-LIST-02 from `docs/15` — favorited pre-login, migrates post-login

---

#### Sprint 3 — Public Site: Requirement Wizard & Contact (Week 5)

**Objective:** Customers can describe their needs and get matched; they can submit inquiries directly.

**Dependencies:** Backend `/api/v1/ai/recommend` + lead capture endpoint working.

**Tasks:**

**2.3.1 — Requirement Wizard (Guided Flow)**
- Page: `src/pages/RequirementWizard.tsx` (route `/requirement-analysis`)
- Sections (from `docs/16-customer-spec/04-requirement-wizard.md`):
  1. Welcome screen: explain what wizard does
  2. Multi-step form: budget, property type, location, special features (AI learns progressively)
  3. Results screen: ranked property matches + save profile option
- **Stitch approach:** Paste DESIGN.md + multi-step form prompt → get modal components
- **API calls:**
  - POST `/api/v1/ai/recommend` → sends answers, gets matches + reasoning
  - POST `/api/v1/portal/requirements` (if user saves) → persists profile
- **State:**
  - `useState(step)` - tracks which step in wizard
  - `useState(answers)` - accumulates user responses
  - `useState(results)` - recommendations from AI
  - `useState(isSaved)` - if profile is persisted
- **Validation:** Each step must validate before allowing next (budget is number, etc.)
- **Testing:**
  - TC-REC-02 from `docs/15`: No results returns closest-match fallback
  - Form validation blocks invalid inputs

**2.3.2 — Contact & Inquiry Form**
- Page: `src/pages/Contact.tsx` (route `/contact`)
- Sections (from `docs/16-customer-spec/05-contact-page.md`):
  1. Contact form: name, email, phone, message
  2. Success state: "Thanks, an agent will follow up"
- **Stitch approach:** Prompt "real estate contact form, glassmorphic card, form submission feedback"
- **API calls:**
  - POST `/api/v1/leads/contact` → creates lead from form submission
- **State:**
  - `useState(formData)` - tracks inputs
  - `useState(isSubmitting)` - button disabled while posting
  - `useState(success)` - shows success message
- **Error handling:** Form validation errors, submission failure (show error toast)
- **Testing:**
  - Submit form → lead created in backend
  - Invalid email blocked by validation

**2.3.3 — Authentication Pages (Login & Register)**
- Pages: `src/pages/Login.tsx` (route `/login`) + `src/pages/Register.tsx` (route `/register`)
- Behavior (from `docs/16-customer-spec/06-auth-register-login.md`):
  - Login: email/password + "Forgot password?" link
  - Register: email/password/name + terms checkbox
  - Both redirect to `/portal` on success
  - Anonymous session-data migrates to account on register (handled by backend + context)
- **Stitch approach:** Prompt "real estate login form, simple clean design" → generate
- **API calls:**
  - POST `/api/v1/auth/login` → returns JWT
  - POST `/api/v1/auth/register` → creates user + returns JWT
- **State:**
  - `useAuth()` hook updates global auth context with JWT
  - AuthContext persists JWT to localStorage
  - On app load, context checks if valid JWT exists; restores user
- **Error handling:** Invalid credentials show inline error; network failures show toast
- **Testing:**
  - Register → new JWT issued → redirect to portal
  - Favorites from anonymous session migrate to account

---

#### Sprint 4 — Public Site: Customer Portal (Week 6)

**Objective:** Authenticated customers have a personalized view of favorites, requirements, inquiries.

**Dependencies:** All public site features from Sprints 1–3 complete.

**Tasks:**

**2.4.1 — Portal Layout & Navigation**
- Component: `src/components/PortalNav.tsx` — left sidebar with links to dashboard, favorites, requirements, inquiries, notifications
- Used in all portal pages (nested under `/portal/*`)
- Sidebar shows user name, has logout button

**2.4.2 — Portal Dashboard**
- Page: `src/pages/PortalDashboard.tsx` (route `/portal`)
- Shows:
  - Welcome greeting
  - Quick stats: # favorites, # saved requirements, # active inquiries
  - Recommended properties based on saved requirements
  - Recent activity feed
- **Stitch approach:** "Admin dashboard style portal landing, Material 3 cards, stat blocks"
- **API calls:** GET `/api/v1/portal/dashboard` → aggregated data
- **Testing:** Stats reconcile with underlying data

**2.4.3 — Portal Favorites Page**
- Page: `src/pages/PortalFavorites.tsx` (route `/portal/favorites`)
- Shows: grid of favorited properties with remove button
- **API calls:** GET `/api/v1/portal/favorites` → list of favorite property IDs, GET `/api/v1/properties/{id}` for details
- **Testing:** Remove from favorites → list updates

**2.4.4 — Portal Saved Requirements & Matches**
- Page: `src/pages/PortalRequirements.tsx` (route `/portal/requirements`)
- Shows: saved requirement profiles + new matches since last visit
- Users can re-run a profile, set match notifications
- **API calls:** GET `/api/v1/portal/requirements` + GET `/api/v1/portal/requirements/{id}/matches`
- **Testing:** New property published → matching requirement gets notification (if opted in)

**2.4.5 — Portal Inquiries & Lead Status**
- Page: `src/pages/PortalInquiries.tsx` (route `/portal/inquiries`)
- Shows: inquiries user has submitted + their status (new, contacted, scheduled viewing, etc.)
- User can add notes to their own inquiries
- **API calls:** GET `/api/v1/portal/inquiries` + PATCH `/api/v1/portal/inquiries/{id}/notes`
- **Testing:** Inquiry status updates reflect in portal

**2.4.6 — Portal Notifications**
- Page: `src/pages/PortalNotifications.tsx` (route `/portal/notifications`)
- Shows: in-app notifications (new matches, message from agent, etc.)
- Mark as read / clear all
- **API calls:** GET `/api/v1/portal/notifications` + PATCH (mark read)
- **Testing:** New match fires notification; mark-read works

**Acceptance Criteria (Sprints 1–4):**
- [ ] All 12 customer-facing pages render without errors
- [ ] All pages use correct design tokens (colors, typography, spacing)
- [ ] API calls to backend are wired correctly (correct endpoints, request/response mapping)
- [ ] Auth flow works: register → favorites migrate → login → see personalized content
- [ ] Tenant scoping: a different tenant's properties never leak into results/favorites
- [ ] All linting + type checks pass
- [ ] Each page has basic Vitest snapshot test

---

### Phase 1b: Admin Portal (Sprints 2–4, Parallel with Public Site)

Start admin portal development in parallel with Sprint 2 of public site (once auth is working). Admin screens are more complex but more isolated (less cross-tenant risk once auth is locked).

#### Sprint 2 (Parallel) — Admin: Login & Dashboard (Week 4)

**2A.2.1 — Admin Login Page**
- Page: `src/pages/AdminLogin.tsx` (route `/admin/login`)
- Specialized for admin/agent accounts (uses same JWT endpoint as customers, but checks role server-side)
- On successful login, redirect to `/admin/dashboard`

**2A.2.2 — Admin Dashboard**
- Page: `src/pages/AdminDashboard.tsx` (route `/admin/dashboard`)
- Sections (from `docs/17-admin-spec/02-dashboard.md`):
  1. Top KPIs: properties, leads, conversion, active agents
  2. Leads pipeline chart (stacked bar or funnel)
  3. Lead activity feed
  4. Upcoming follow-ups / reminders
- **Stitch approach:** "Real estate admin dashboard, multiple KPI cards, funnel chart, Material 3"
- **API calls:** GET `/api/v1/admin/dashboard` → all dashboard data
- **Testing:** KPI numbers reconcile with underlying leads/properties

**2A.2.3 — Admin Navbar + Left Sidebar**
- Component: `src/components/AdminNav.tsx` — left sidebar with:
  - Logo
  - Nav items: Dashboard, Properties, Leads, Agents, Users, AI Config, CMS, Reports, Settings
  - User profile + logout
  - All items reachable in one click (from `docs/13-ui-ux-flows.md` §2.4)
- Mounted in all `/admin/*` routes

**Acceptance Criteria:**
- [ ] Admin can log in with agent/admin/super_admin role
- [ ] Dashboard loads with real KPI data
- [ ] Left nav reaches all 9 major sections in one click
- [ ] Role-based access control prevents agents from accessing User Management

---

#### Sprint 3 (Parallel) — Admin: Properties & Approvals (Week 5)

**2A.3.1 — Properties List**
- Page: `src/pages/AdminProperties.tsx` (route `/admin/properties`)
- Sections (from `docs/17-admin-spec/03-properties-list.md`):
  1. Filter/sort bar: status (draft, pending, approved, published), type, date range
  2. Table view: property name, type, price, status, actions (edit, preview, delete)
  3. Bulk actions: bulk upload link, multi-select delete
- **Stitch approach:** "Real estate admin table with filters, Material 3, status badges"
- **API calls:**
  - GET `/api/v1/admin/properties?status=...&limit=20&offset=0` → paginated list
  - GET `/api/v1/admin/properties/facets` → filter options
- **State:**
  - `useState(filters)`, `useState(page)`, `useState(selectedRows)`
- **Testing:** Filters work; pagination works; bulk selection works

**2A.3.2 — Add/Edit Property Form**
- Page: `src/pages/AdminPropertyAddEdit.tsx` (route `/admin/properties/new`, `/admin/properties/:id/edit`)
- Multi-step form (from `docs/17-admin-spec/04-property-add-edit.md`):
  1. Basic info: name, type, address, price, beds/baths/area
  2. Media: upload photos, floor plan, 3D tour link
  3. Description: detailed text + amenities
  4. Advanced: agent, tags, featured status, approval workflow
- **Stitch approach:** "Multi-step form with tabs, upload zones, Material 3, form validation feedback"
- **API calls:**
  - POST `/api/v1/admin/properties` (new) or PATCH `/api/v1/admin/properties/{id}` (edit)
  - POST `/api/v1/storage/upload` → upload media files
- **State:**
  - `useState(step)`, `useState(formData)`, `useState(uploadProgress)`
  - Form validation on each field + before submit
- **Testing:**
  - Create property → appears in list
  - Edit property → changes persist
  - File upload → images appear in form preview

**2A.3.3 — Property Bulk Upload**
- Page: `src/pages/AdminBulkUpload.tsx` (route `/admin/properties/bulk-upload`)
- Behavior (from `docs/17-admin-spec/05-property-bulk-upload.md`):
  1. CSV template download
  2. File upload zone (drag-drop or click)
  3. Validation: preview + per-row error reporting
  4. Confirm → background job starts
  5. Job status modal: progress bar, row-by-row feedback
- **Stitch approach:** "File upload interface, Material 3, drag-drop zone, status tracking"
- **API calls:**
  - POST `/api/v1/admin/properties/bulk-upload` → uploads CSV, returns job ID
  - GET `/api/v1/admin/jobs/{job_id}` → polls for progress
- **Testing:**
  - TC-PROP-02 from `docs/15`: Malformed rows report per-row errors, not full-batch failure

**2A.3.4 — Property Approvals Status**
- Page: `src/pages/AdminPropertyApprovals.tsx` (route `/admin/properties?status=pending_approval`)
- Shows: only pending-approval properties, with "Approve" / "Reject" buttons + reason field
- Approval workflow: admin-only action. **Publishing enqueues the `jobs` pipeline** — embed → index → match saved profiles → notify (`02-architecture.md` §4.4). **Rejection requires a reason.** *(This line used to say "fires webhook (Gap G10)". There is no G10 in `GAPS.md`, and there is no approval webhook in any spec — both were invented here.)*
- **API calls:**
  - PATCH `/api/v1/admin/properties/{id}/approve` + PATCH `.../reject`
- **Testing:** Approve property → status changes to published; shows up in public search

---

#### Sprint 4 (Parallel) — Admin: Leads & CRM Pipeline (Week 6)

**2A.4.1 — Leads Kanban Board**
- Page: `src/pages/AdminLeadsKanban.tsx` (route `/admin/leads`)
- Kanban view: columns = pipeline stages (new, contacted, qualified, scheduled, viewing, closed-won/lost)
- Cards = lead name, company, status, agent assigned, expected close date
- Drag-drop to change stage
- Click card → open lead detail panel (side sheet)
- **Stitch approach:** "Kanban board with drag-drop, Material 3, cards with status badges, column actions"
- **API calls:**
  - GET `/api/v1/admin/leads` → all leads
  - PATCH `/api/v1/admin/leads/{id}` → update stage (via drag-drop)
- **State:**
  - `useState(leads)` — grouped by stage
  - Drag-drop handled by a library like `react-beautiful-dnd`
- **Testing:**
  - TC-LEAD-02: Drag card to new stage → `lead_activities` records the change

**2A.4.2 — Lead Detail Panel (Side Sheet)**
- Component: `src/components/AdminLeadDetail.tsx` — opened as a modal/side sheet when clicking a lead card
- Sections (from `docs/17-admin-spec/08-lead-detail.md`):
  1. Lead name, contact info, source
  2. Notes timeline (agent comments with timestamps)
  3. Activity timeline (stage changes, meetings scheduled)
  4. Assignment dropdown (agent to assign to)
  5. Properties suggested (based on requirement profile, if any)
- **API calls:**
  - GET `/api/v1/admin/leads/{id}` → full lead + history
  - POST `/api/v1/admin/leads/{id}/notes` → add note
  - PATCH `/api/v1/admin/leads/{id}` → update (stage, assigned agent, etc.)
- **Testing:** Notes persist; assignment changes are reflected immediately

**2A.4.3 — Leads Table View (Alternative)**
- Page: `src/pages/AdminLeadsTable.tsx` (route `/admin/leads?view=table`)
- Alternative to Kanban: sortable/filterable table (for mass operations, different workflow)
- Columns: lead ID, name, source, stage, agent assigned, created date, last activity
- Bulk actions: reassign multiple, bulk change stage
- **API calls:** Same as Kanban (GET `/api/v1/admin/leads`)
- **Testing:** Sorting and filtering work; bulk reassign works

**2A.4.4 — Leads Assignment & Routing**
- Component: `src/components/AdminLeadAssignment.tsx` — embedded in Leads page + Lead Detail
- Behavior: dropdown to select agent + (optional) auto-route rules (based on specialization, capacity)
- **API calls:** PATCH `/api/v1/admin/leads/{id}` with `assigned_agent_id`
- **Testing:** TC-LEAD-03: Agent can only see leads assigned to them (enforced server-side via tenancy scope)

---

### Phase 2: Sprints 5–7 — AI Features with Real Backend Integration

Once public site + admin core are done, wire up the three AI features end-to-end. These depend on backend AI services being complete.

#### Sprint 5 — AI Search Widget (Week 7)

**Objective:** Real-time AI search is fully integrated on homepage and property listing.

**Dependencies:** Backend `/api/v1/ai/search` + embeddings complete.

**Tasks:**

**2.5.1 — AI Search Bar Integration**
- Refine `SearchBar.tsx` component created in Sprint 1
- Wire to real `/api/v1/ai/search` endpoint
- Debounce typing (300ms) to avoid excessive requests
- Show real-time autocomplete as user types (from `06-ai-search-spec.md` §3)
- Handle voice input → POST `/api/v1/ai/search/voice` (if user clicks mic)
- **Testing:**
  - TC-SEARCH-01: Golden query test set (spot-check relevance)
  - TC-SEARCH-02: Bedrock timeout → fallback to standard search (shows "trying AI, or use filters")

**2.5.2 — Search Results Integration**
- Enhance `PropertyListing.tsx` to show AI search results + standard filters
- When user submits search query, show:
  1. AI-ranked results (primary)
  2. Filters sidebar (for refinement)
  3. Option to "Refine AI search" vs. "Use standard filters"
- **Testing:** Multiple queries, verify results quality against golden set

---

#### Sprint 6 — AI Chatbot End-to-End (Week 8)

**Objective:** Chat widget works with real streaming responses + escalation.

**Dependencies:** Backend `/api/v1/ai/chat/*` endpoints complete.

**Tasks:**

**2.6.1 — Chat Widget + Message Streaming**
- Refine `ChatWidget.tsx` created in Sprint 1
- Wire to real `/api/v1/ai/chat/message` endpoint
- Stream responses (fetch with `mode: 'cors'`, stream the text chunks real-time)
- Show typing indicator while waiting for response
- Display tool calls (if chatbot decides to look up a property, show "Looking up 3BHK near tech park...")
- **Testing:**
  - TC-CHAT-01: Golden conversation test set (verify no hallucinations)
  - Chat responds within target latency (`05-ai-chatbot-spec.md` §8)

**2.6.2 — Chatbot → Lead Capture**
- When user shares contact info during chat, automatically create lead:
  - Extract name, email, phone from conversation
  - POST `/api/v1/leads` with `source: 'chatbot'`
  - Show confirmation: "Thanks, an agent will follow up"
- **Testing:** Chat lead captured correctly in admin portal

**2.6.3 — Escalation (Chat → Agent Handoff)**
- "Talk to an agent" button in chat → marks conversation for escalation
- Escalated conversation visible in admin portal (later feature: real-time agent response)
- **Testing:** TC-CHAT-03: Escalation request visible in admin leads

---

#### Sprint 7 — AI Recommendation End-to-End (Week 9)

**Objective:** Requirement wizard generates real matches; saved profiles get notifications.

**Dependencies:** Backend `/api/v1/ai/recommend` + recommendation engine complete.

**Tasks:**

**2.7.1 — Requirement Wizard Integration**
- Refine `RequirementWizard.tsx` created in Sprint 3
- Wire to real `/api/v1/ai/recommend` endpoint
- Multi-step flow sends answers progressively, gets matches at end
- Show match results with:
  1. Property card (image, price, bedrooms, location)
  2. Match score / confidence
  3. Reasoning (why this property matches)
  4. Actions: save to favorites, view details, chat-to-learn
- Save profile option → POST `/api/v1/portal/requirements`
- **Testing:**
  - TC-REC-01: Golden requirement-profile test set (quality spot-check)
  - TC-REC-02: No strong matches → closest-match fallback (never empty state)

**2.7.2 — Saved Requirements + New Match Notifications**
- User can save a requirement profile
- When new property published, background job checks if it matches any saved profiles
- If match found, create notification: "New match! 3BHK published near tech park, 75L, matches your saved requirement"
- User sees notification in portal + (optionally) via email
- **Testing:** TC-REC-03: Publish property → matching requirement gets notification

---

### Phase 3: Sprints 8–11 — Admin Remaining Modules & Hardening

These sprints complete the admin portal + harden the full system.

#### Sprint 8 — Admin: Agents & Users (Week 10)

**2.8.1 — Agents Management**
- Page: `src/pages/AdminAgents.tsx` (route `/admin/agents`)
- List agents: name, email, specialization, leads assigned, conversion rate, status (active/inactive)
- Add agent → simple form (email + role)
- **API calls:** GET `/api/v1/admin/agents`, POST `/api/v1/admin/agents`
- **Testing:** Agent visible in lead assignment dropdown after creation

**2.8.2 — Users & Roles**
- Page: `src/pages/AdminUsers.tsx` (route `/admin/users`)
- List users (agents + tenant admins): email, role, created date, last login
- Invite user → form with email + role dropdown (agent, admin)
- Revoke access → remove from tenant
- **API calls:** GET `/api/v1/admin/users`, POST `/api/v1/admin/users/invite`, DELETE `/api/v1/admin/users/{id}`
- **Roles enforced server-side** via JWT claims + `require_role` FastAPI dependency
- **Testing:**
  - TC-ROLE-01: Newly invited agent has correctly scoped access from first login
  - Agent cannot access User Management (403)

**2.8.3 — Audit Log**
- Page: `src/pages/AdminAuditLog.tsx` (route `/admin/users/audit-log`)
- Read-only: list of write actions (create/update/delete) with actor, action, entity, timestamp
- Filterable by actor, action type, date range
- **API calls:** GET `/api/v1/admin/audit-log`
- **Testing:** Property approval recorded in audit log; agent assignment recorded

---

#### Sprint 9 — Admin: AI Configuration & CMS (Week 11)

**2.9.1 — AI Chatbot Configuration**
- Page: `src/pages/AdminAIConfig.tsx` (route `/admin/ai-config/chatbot`)
- Editable fields:
  - Greeting message (shown when chat opens)
  - FAQ list (Q&A pairs, chatbot will cite these if relevant)
  - Escalation threshold (when to suggest agent)
  - Blocked topics (if user asks about X, escalate immediately)
- **API calls:**
  - GET `/api/v1/admin/ai-config` → current settings
  - PATCH `/api/v1/admin/ai-config` → save changes
- **Testing:**
  - TC-AICONFIG-01: Change greeting → takes effect on next new chat without deployment

**2.9.2 — AI Recommendation Tuning**
- Page: similar to chatbot config, editable weight sliders for recommendation scoring:
  - Price weight, location weight, type weight, amenities weight
- **API calls:** Same pattern as chatbot config

**2.9.3 — CMS / Static Pages**
- Page: `src/pages/AdminCMS.tsx` (route `/admin/cms`)
- Sections:
  1. Pages list: About, Terms, Careers, Blog (if included)
  2. Edit page → rich text editor + SEO fields (title, description, slug)
  3. Publish → makes page available at `/<slug>` on public site
- **API calls:**
  - GET `/api/v1/admin/cms/pages`
  - PATCH `/api/v1/admin/cms/pages/{id}`
- **Testing:** Edited CMS page appears on public site at correct slug

**2.9.4 — Reports Builder**
- Page: `src/pages/AdminReports.tsx` (route `/admin/reports`)
- Simple report builder:
  1. Select metric: leads by stage, conversion rate, average deal size, leads by source
  2. Date range filter
  3. Generate table + download CSV
- **API calls:** GET `/api/v1/admin/reports` with query params
- **Testing:**
  - TC-REPORT-01: Report figures match dashboard numbers for same filters

---

#### Sprint 10 — Admin: Settings & Multi-Tenancy (Week 12)

**2.10.1 — Tenant Branding**
- Page: `src/pages/AdminSettings.tsx` (route `/admin/settings`)
- Editable: tenant name, logo, primary accent color (single override, see `docs/DESIGN.md` note on FR16.2)
- **API calls:** PATCH `/api/v1/admin/tenants/{tenant_id}`
- **Testing:** Logo and name update visible immediately

**2.10.2 — Notification Rules**
- Page: `src/pages/AdminNotificationRules.tsx` (route `/admin/settings/notifications`)
- Configure when notifications fire:
  - New lead assigned → in-app + email (toggles per type)
  - Lead stage changed → in-app
  - New match for requirement → in-app + email
  - Daily digest (yes/no)
- **API calls:** PATCH `/api/v1/admin/tenants/{tenant_id}/notification_rules`
- **Testing:** Notification fires per configured rule

**2.10.3 — Super Admin Tenant Management (Platform-Level)**
- Page: `src/pages/PlatformTenants.tsx` (route `/platform/tenants`)
- **Roles:** visible only to `super_admin` role
- Sections:
  1. Tenants list: name, plan, created date, user count, property count
  2. Create tenant: form with tenant name + domain (custom or subdomain)
  3. Tenant detail: edit branding, see stats
  4. Deactivate/delete tenant
- **API calls:**
  - GET `/api/v1/platform/tenants`
  - POST `/api/v1/platform/tenants` (create)
  - PATCH `/api/v1/platform/tenants/{id}` (edit)
  - DELETE `/api/v1/platform/tenants/{id}` (delete)
- **Testing:**
  - TC-TENANT-03: Second full tenant onboarded; zero cross-tenant leakage
  - Agent from Tenant A cannot read Tenant B's properties (enforced by RLS)

---

#### Sprint 11 — Final Polish, Hardening, UAT (Week 13)

**2.11.1 — Performance Optimization**
- Profiling: identify slow renders / API calls
- Code splitting: lazy-load admin portal sections
- Image optimization: optimize hero images, use `next/image` or equivalent
- **Testing:**
  - TC-PERF-01: All pages meet LCP/FCP targets (from `12-srs.md` NFR-PERF-1)
  - Admin Kanban board smooth with 500+ leads

**2.11.2 — Full Regression Testing**
- Run all acceptance criteria from `docs/15-development-plan.md` §5 against real data
- Golden test sets for AI features (chat, search, recommendation)
- Cross-browser testing (Chrome, Firefox, Safari)
- Mobile responsiveness (public site + portal dashboard at least)

**2.11.3 — Monitoring & Alerting**
- Set up error tracking: Sentry or equivalent
- Set up analytics: Google Analytics or equivalent
- Real user monitoring (RUM): track LCP, FID, CLS from production
- **Testing:** Errors from production visible in dashboard

**2.11.4 — UAT with Pilot Tenant**
- Prepare staging environment with real pilot-tenant branding + sample data
- Provide UAT guide to pilot tenant
- Record feedback + bugs
- Final bug bash

---

## 3. Stitch Integration Workflow

### 3.1 Before You Paste into Stitch

1. **Read the spec file** (docs/16-customer-spec/*.md or docs/17-admin-spec/*.md)
   - Understand layout, workflow, edge cases, acceptance criteria
2. **Gather design context** from `docs/DESIGN.md`
   - Colors, typography, spacing, shape, depth

### 3.2 Stitch Paste Sequence

```
Paste 1: Entire DESIGN.md (frontmatter + prose)
  → This establishes the theme for the session

Paste 2: The Stitch prompt for your screen
  → Either from docs/11-stitch-design-prompts.md (if it exists)
  → OR a custom detailed description you write
```

**Example custom prompt:**

```
Design an admin properties list page for PropVista CRM (a real estate CRM).
Follow the shared design direction (just pasted DESIGN.md).

Layout:
- Filter bar across the top: dropdown for status (All, Draft, Pending Approval,
  Published), text search by property name, date range picker
- Below: a table with columns: property image thumbnail, name, type, price,
  bedrooms, status badge (use semantic colors: success for Published, warning
  for Pending, neutral for Draft), actions menu (edit, preview, delete)
- Pagination at bottom: showing X–Y of Z results, with prev/next buttons
- Bulk actions: checkbox to select all rows, with "Delete Selected" button
  (disabled until rows selected)

Visual:
- Use the `primary` token for action buttons
- Use status colors for badge backgrounds (success/warning/error/neutral
  containers from DESIGN.md)
- Cards should have 1px hairline borders (outline-variant) and soft shadow
- All text in Plus Jakarta Sans, no serif/mono
```

### 3.3 After Stitch Generates

1. **Export the component** as `.tsx` → paste into `src/components/` or `src/pages/`
2. **Audit the output:**
   - ✅ Correct layout + wireframe
   - ✅ All colors are from DESIGN.md tokens (no hex hardcoding)
   - ✅ All fonts use Plus Jakarta Sans
   - ✅ Responsive (check breakpoints)
   - ❌ Remove Stitch-generated placeholder data; replace with props + state hooks
   - ❌ Remove hardcoded colors; replace with Tailwind tokens
3. **Wire in functionality:**
   - API calls (fetch data, submit forms)
   - State management (useState/useContext)
   - Error handling
   - Loading states
   - Validation
4. **Test:**
   - Render test (snapshot or unit test)
   - Integration test (real API calls)
   - A11y check (keyboard nav, ARIA labels)
5. **Code review:**
   - ESLint passes
   - TypeScript strict mode
   - Color/type/spacing use design tokens (no hardcoding)
   - Tenant scoping correct (if needed)

---

## 4. Quality Gates & Code Review

### 4.1 Every PR Must Pass

- **Lint:** `npm run lint` → zero warnings
- **Type check:** `npm run type-check` (or tsc) → strict mode, no `any`
- **Test:** `npm run test` → all Vitest tests pass
- **Build:** `npm run build` → no errors
- **Design tokens:** grep for hex colors / hardcoded sizes → all use Tailwind tokens from DESIGN.md config
- **API contracts:** review request/response bodies match backend `docs/04-api-spec.md`
- **Tenant scoping:** if page reads/writes user-scoped data, verify it uses `useAuth()` to scope to current user + tenant

### 4.2 Component Checklist (Before "Done")

For each new component/page:
- [ ] Spec file read + acceptance criteria listed
- [ ] Layout matches spec wireframe
- [ ] All colors use design tokens (no hex hardcoding)
- [ ] All typography uses token classes (display-lg, body-md, etc.)
- [ ] All spacing uses token units (not pixel-hardcoded)
- [ ] Error states rendered (empty, loading, error)
- [ ] Edge cases handled (partial data, null values)
- [ ] API calls made with correct endpoint + params from spec
- [ ] Response correctly mapped to component state
- [ ] Accessibility: keyboard nav works, ARIA labels present
- [ ] Mobile-responsive (test at 375px, 768px, 1440px)
- [ ] Unit test + integration test written
- [ ] ESLint + Prettier pass
- [ ] TypeScript strict mode, no `any`
- [ ] Commit message references sprint + component (e.g., "Sprint 2: Add PropertyDetails page (#xyz)")

---

## 5. Collaboration Between Frontend & Backend

### 5.1 API-First Coordination

1. **Backend** adds endpoint to `docs/04-api-spec.md` first (with request/response schema)
2. **Frontend** reads spec + waits for backend to deploy to staging
3. **Frontend** wires component to real endpoint
4. Both teams write tests for the contract (backend: endpoint test; frontend: integration test calling real API)

### 5.2 Shared Type Definitions

Ideal: **Generate frontend types from FastAPI OpenAPI schema** (using `openapi-typescript` or similar).

Fallback: **Duplicate Pydantic schema in `src/types/`** as TypeScript interfaces, kept in sync manually.

Example:
```typescript
// src/types/property.ts — mirrors backend Pydantic PropertyOut schema
export interface Property {
  id: string;
  tenant_id: string;
  name: string;
  property_type: 'apartment' | 'villa' | 'plot' | 'commercial';
  price: number;
  bedrooms: number;
  bathrooms: number;
  area_sqft: number;
  address: string;
  city: string;
  state: string;
  created_at: string;
  updated_at: string;
}
```

---

## 6. Environment Configuration

### 6.1 `.env.local` (Frontend)

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### 6.2 Deployment Environments

| Env | Frontend URL | Backend URL | Supabase | Notes |
|---|---|---|---|---|
| Local | `localhost:3000` | `localhost:8000` | local Supabase | Dev machine |
| Staging | `staging-public.propvista.app` | `api.staging.propvista.app` | staging Supabase | Test with real deployment |
| Production | `propvista.app` (public) + `portal.propvista.app` (portal) | `api.propvista.app` | prod Supabase | Live |

---

## 7. Common Pitfalls & Solutions

| Pitfall | Solution |
|---|---|
| Stitch generates hardcoded colors instead of token classes | After export, replace every `bg-[#hex]` with its token class (`bg-primary`, etc). Grep for `#` to catch stragglers — and `python scripts/check_drift.py` will fail if any survive. |
| Component doesn't handle loading/error states | Always show skeleton or spinner while `isLoading === true`; show error toast if API call fails. |
| API call forgetting to include tenant scope | Use `useAuth()` hook to get current `tenant_id`; always include in query params or request body. |
| Favorites/notifications not persisting after page reload | Save to localStorage or backend; on app load, call GET `/api/v1/portal/{resource}` to hydrate. |
| Mobile layout breaks at 375px | Test every page at mobile breakpoints; use Tailwind responsive prefixes (`md:`, `lg:`) liberally. |
| Linter errors after Stitch export | Run `npm run lint -- --fix` to auto-format; fix type errors by hand. |
| Component props undefined at render | Always provide default props or check existence before rendering; use optional chaining. |

---

## 8. Summary: Sprints at a Glance

| Sprint | Focus | Public Site Deliverables | Admin Portal Deliverables |
|---|---|---|---|
| **0** | Scaffold + Tooling | React app, auth context, API client | Same + RBAC context |
| **1** | Homepage + Nav | Homepage, navbar, chat bubble, search bar | Login, dashboard, sidebar nav |
| **2** | Search + Details | Property listing, property details, favorites | Properties list, add/edit form |
| **3** | Wizard + Contact | Requirement wizard, contact form, auth pages | Bulk upload, approvals workflow |
| **4** | Customer Portal | Dashboard, favorites, requirements, inquiries, notifications | Leads Kanban, lead detail, leads table |
| **5** | AI Search | Real `/ai/search` integration, golden test set | — |
| **6** | AI Chatbot | Real `/ai/chat/*` integration, lead capture, escalation | — |
| **7** | AI Recommendation | Real `/ai/recommend`, saved profiles, match notifications | — |
| **8** | — | — | Agents, users, audit log |
| **9** | — | — | AI config, CMS, reports, notifications |
| **10** | — | — | Tenant branding, settings, super admin tenants |
| **11** | Polish + UAT | Performance optimization, full regression, monitoring | Same + pilot UAT |

---

**Next steps:**
1. Use this plan + `docs/11-stitch-design-prompts.md` to start Sprint 0 scaffold
2. Set up Stitch project, test design system paste
3. Begin Sprint 1 with homepage design (Stitch) + navbar implementation
4. Maintain this plan as a living document — update as sprints progress and learnings emerge

