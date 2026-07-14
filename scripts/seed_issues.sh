#!/usr/bin/env bash
# Seed the GitHub issue board from docs/BACKLOG.md.
#
# BACKLOG.md owns the STRUCTURE of the work (tasks, subtasks, specs, branches).
# GitHub Issues own the STATUS. This script is the bridge, and it is committed so
# the board's creation is auditable — a hand-clicked board is not.
#
#   bash scripts/seed_issues.sh --dry-run    # print what it would create
#   bash scripts/seed_issues.sh              # create for real
#
# Idempotent: an issue whose exact title already exists is skipped, so a re-run
# adds only what's new.
#
# Requires: gh (https://cli.github.com), authenticated via `gh auth login`.

set -euo pipefail

DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

if [[ $DRY_RUN -eq 0 ]]; then
  command -v gh >/dev/null 2>&1 || {
    echo "gh is not installed. Install it (winget install GitHub.cli), then 'gh auth login'."
    echo "Meanwhile: bash scripts/seed_issues.sh --dry-run"
    exit 1
  }
  gh auth status >/dev/null 2>&1 || { echo "gh is not authenticated. Run: gh auth login"; exit 1; }
fi

EXISTING=""
if [[ $DRY_RUN -eq 0 ]]; then
  echo "Fetching existing issues (so a re-run doesn't duplicate)..."
  EXISTING="$(gh issue list --state all --limit 500 --json title --jq '.[].title')"
fi

ensure_label() {
  [[ $DRY_RUN -eq 1 ]] && return 0
  gh label create "$1" --color "$2" --description "$3" 2>/dev/null || true
}

# --- labels ---------------------------------------------------------------
ensure_label "pre-flight" "5b5b6b" "Must happen before any application code"
ensure_label "sprint-0"   "3525cd" "Environment & Foundation"
ensure_label "sprint-1"   "3525cd" "Data Layer, Auth & Tenancy"
ensure_label "sprint-2"   "3525cd" "Property Management"
ensure_label "sprint-3"   "3525cd" "Public Listing & Details"
ensure_label "sprint-4"   "3525cd" "Lead Capture & CRM Pipeline"
ensure_label "blocked"    "ba1a1a" "Blocked by a documented gap (see docs/GAPS.md)"
ensure_label "security"   "8a5300" "Touches tenant isolation or PII"

# --- helper ---------------------------------------------------------------
# issue <id> <title> <labels> <branch> <spec> <blocker|-> <body...>
issue() {
  local id="$1" title="$2" labels="$3" branch="$4" spec="$5" blocker="$6"
  shift 6
  local full="[$id] $title"

  if [[ -n "$EXISTING" ]] && grep -Fxq "$full" <<< "$EXISTING"; then
    echo "  skip (exists): $full"
    return 0
  fi

  local body
  body="$(cat <<EOF
> Structure and subtasks: **[\`docs/BACKLOG.md\`](../blob/main/docs/BACKLOG.md)** — task \`$id\`.
> Work from the spec section below, **not** from this issue body. This issue owns *status*, nothing else.

**Branch:** \`$branch\`
**Spec:** $spec
EOF
)"

  if [[ "$blocker" != "-" ]]; then
    body="$body

---
## ⛔ BLOCKED — $blocker

This cannot start regardless of capacity. The blocker is a **document**, not a coding problem.
See [\`docs/GAPS.md\`](../blob/main/docs/GAPS.md). **Do not work around it in code** — fix the owning doc first (\`CLAUDE.md\`)."
    labels="$labels,blocked"
  fi

  body="$body

---
## Subtasks

$*

---
## Definition of Done

- [ ] Acceptance criteria in \`docs/BACKLOG.md\` \`$id\` **demonstrated** — not just \"it compiles\"
- [ ] \`python scripts/check_drift.py\` — no new drift
- [ ] Self-check: \`docs/09-coding-standards.md\` §8
- [ ] Tests written **alongside** the code, not after
- [ ] If a tenant-owned table was added: **a cross-tenant isolation test that fails at the DB layer** (ADR-0003)"

  if [[ $DRY_RUN -eq 1 ]]; then
    echo ""
    echo "────────────────────────────────────────────────────────"
    echo "TITLE:  $full"
    echo "LABELS: $labels"
    echo "$body"
    return 0
  fi

  echo "  create: $full"
  gh issue create --title "$full" --label "$labels" --body "$body" >/dev/null
}

echo ""
echo "Seeding PropVista backlog ($([[ $DRY_RUN -eq 1 ]] && echo 'DRY RUN' || echo 'LIVE'))"
echo ""

# --- Pre-flight -----------------------------------------------------------
issue "P.1" "Commit the doc set, install the DevOS gate" "pre-flight" \
  "feature/devos-and-design-system" "\`22-risk-register.md\` §7" "-" \
"- [ ] Branch off \`main\` — never commit to \`main\`
- [ ] Commit: design-system reconciliation, the doc-13 kill, the branding deferral
- [ ] Commit: the DevOS (OWNERSHIP, GAPS, check_drift.py, rules/devos.md, .githooks/)
- [ ] Commit: the SDLC docs (18–22, adr/, root README)
- [ ] \`git config core.hooksPath .githooks\`

**Why:** ~26 files changed, zero commits. Two days of decisions with no diff and no revert path."

issue "P.2" "Decide the AWS region" "pre-flight" \
  "-" "\`10-deployment-devops.md\` §1" "gap I1 — Bedrock region vs. India users vs. Supabase co-location" \
"- [ ] Confirm Bedrock Claude model availability by region — **from facts, not memory**
- [ ] Decide compute region, and co-locate the Supabase project with it
- [ ] Record as an **ADR**
- [ ] Update \`10-deployment-devops.md\` §1; close I1 in \`GAPS.md\`

**Why:** doc 10's entire rationale is \"co-locate compute with Bedrock\" — never checked against an India-first product. **Blocks all provisioning.**"

issue "P.3" "Decide font hosting for Plus Jakarta Sans" "pre-flight" \
  "-" "\`13-ui-ux-flows.md\` §5" "gap I2 — font hosting undecided" \
"- [ ] Self-hosted vs. Google Fonts
- [ ] Record in \`13-ui-ux-flows.md\` §5; close I2"

issue "P.4" "Absorb and delete SPRINT0_PLAN.md" "pre-flight" \
  "fix/absorb-sprint0-plan" "\`OWNERSHIP.md\` §6" "-" \
"- [ ] Confirm \`BACKLOG.md\` §4 supersedes it
- [ ] \`git rm SPRINT0_PLAN.md\`
- [ ] Re-baseline: \`python scripts/check_drift.py --accept\`

**Why:** it owns nothing **and it is wrong** — pins \`psycopg2-binary\` (synchronous) against an async-mandatory architecture, and lists \`@vitejs/plugin-tsx\`, which is not a real package.

**Acceptance:** \`async-violation\` drops **2 → 0**. The count going down is the proof."

issue "P.5" "Sweep the 25 stale gap citations" "pre-flight" \
  "fix/sweep-stale-gap-citations" "\`GAPS.md\` §5" "-" \
"- [ ] \`python scripts/check_drift.py\` — **the stale-gap findings ARE the worklist**
- [ ] Fix 16-customer-spec/07, 08, 09, 10, 11; 17-admin-spec/08, 19
- [ ] Re-baseline

**Why:** schema v1.1 closed G1, G2, the favorites uniqueness constraint and \`leads.user_id\`. Three portal specs still call all four blocking. Anyone reading them reports a blocker that no longer exists.

**Acceptance:** \`stale-gap\` drops to **0**."

# --- Sprint 0 -------------------------------------------------------------
issue "S0.1" "Scaffold backend/" "sprint-0" \
  "feature/sprint0-backend-scaffold" "\`02-architecture.md\` §4.2" "-" \
"- [ ] Folder structure per §4.2 — **exactly**; no new top-level folders
- [ ] \`requirements.txt\`: fastapi, uvicorn[standard], sqlalchemy[asyncio], **asyncpg**, alembic, pydantic, pydantic-settings, boto3, pgvector, python-jose
- [ ] ⚠️ **asyncpg, NOT psycopg2** — psycopg2 is synchronous and blocks the event loop
- [ ] Dev deps: pytest, pytest-asyncio, httpx, ruff, black
- [ ] \`core/config.py\` — all settings, env vars only
- [ ] \`main.py\` — FastAPI, v1 router, \`/health\`
- [ ] Shared exception handler → the error envelope (\`04-api-spec.md\` §1). **A raw DB or Bedrock error must never reach a client**
- [ ] \`.env.example\` (commit this; never a real \`.env\`)

**Acceptance:** \`/health\` → 200; ruff + black clean."

issue "S0.2" "Scaffold public-site/" "sprint-0" \
  "feature/sprint0-public-site-scaffold" "\`02-architecture.md\` §5.2 · \`.claude/rules/frontend.md\`" "-" \
"- [ ] Vite + React + TS, **strict mode**, no unjustified \`any\`
- [ ] \`@vitejs/plugin-react\` — ⚠️ **\`@vitejs/plugin-tsx\` is not a real package**
- [ ] \`pages/\`, \`components/\`, \`hooks/\`, \`api/\`, \`context/\`
- [ ] eslint + prettier; vitest + RTL, one smoke test
- [ ] Design tokens from \`DESIGN.md\` → CSS vars
- [ ] ⚠️ **That token file is a second sanctioned fork — add it to \`check_drift.py\`'s watch list.** An unwatched fork is how this project got two design systems

**Acceptance:** dev / build / lint / test all pass."

issue "S0.3" "Scaffold admin-portal/" "sprint-0" \
  "feature/sprint0-admin-portal-scaffold" "\`02-architecture.md\` §5.2" "-" \
"- [ ] Same shape as S0.2
- [ ] **Not tenant-branded** (ADR-0010) — carries the PropVista brand

**Acceptance:** dev / build / lint / test all pass."

issue "S0.4" "Database + Alembic + the RLS migration helper" "sprint-0,security" \
  "feature/sprint0-db-alembic" "\`03-database-schema.md\` · \`.claude/rules/database.md\`" "-" \
"- [ ] Supabase project (dev), **same region as the backend** (depends on P.2)
- [ ] Async SQLAlchemy against the Postgres URL. **The Supabase client is for Auth and Storage only — never data access** (ADR-0005)
- [ ] \`alembic init\`; URL from \`core/config.py\`
- [ ] Enable \`pgvector\`
- [ ] **The reusable RLS migration helper** — one macro, reused per tenant-owned table. **Never hand-write per-table policy SQL**
- [ ] Empty baseline migration

**Acceptance:** \`alembic upgrade head\` from empty; \`downgrade\` returns."

issue "S0.5" "CI/CD skeleton + staging deploy" "sprint-0" \
  "feature/sprint0-ci-staging" "\`10-deployment-devops.md\` §3 · \`21-release-management.md\` §4" "gap I1 — region undecided" \
"- [ ] GitHub Actions on PR: ruff/black/eslint/prettier, pytest, tsc, vitest
- [ ] **Add \`python scripts/check_drift.py\` to CI** — same gate as pre-commit
- [ ] On merge to main: build → Alembic → staging
- [ ] **Manual approval gate before production** — one bad migration touches every tenant at once
- [ ] **Migrations run only via CI.** Never by hand, in any environment
- [ ] **Secret scanning** — a committed key is the likeliest real breach

**Acceptance (doc 15):** CI passes on an empty commit; \`/health\` → 200 **in staging**."

issue "S0.6" "Local dev in one command + seed data" "sprint-0" \
  "feature/sprint0-local-dev" "\`15-development-plan.md\` §4 (the DoD)" "-" \
"- [ ] \`make setup\` / \`dev\` / \`test\` / \`check\`
- [ ] Seed: **two tenants, always.** A single-tenant fixture cannot catch a cross-tenant bug
- [ ] Seed properties across **all six** statuses; leads across every stage and source
- [ ] README \"Start here\" verified by someone who has never run it

**Acceptance:** clean clone → running in under 10 minutes."

issue "S0.7" "Structured logging + Bedrock observability" "sprint-0" \
  "feature/sprint0-logging" "\`10-deployment-devops.md\` §5 · \`.claude/rules/ai.md\`" "-" \
"- [ ] \`core/logging.py\` — structured logs
- [ ] The Bedrock client wrapper logs **latency, tokens and model ID by construction**, so a caller cannot forget

**Why now:** if this isn't in the wrapper from the first line it never gets retrofitted — and it is the only defence against both silent AI degradation and runaway Bedrock cost.

**Acceptance:** a stubbed Bedrock call emits all three fields."

# --- Sprint 1 -------------------------------------------------------------
issue "S1.1" "Core tables: tenants, users, roles_permissions" "sprint-1,security" \
  "feature/auth-tenant-core-tables" "\`03-database-schema.md\` §3.1–3.3" "-" \
"- [ ] Tables + Alembic migrations
- [ ] Every tenant-owned table: \`tenant_id UUID NOT NULL REFERENCES tenants(id)\`
- [ ] Soft delete (\`deleted_at\`) on user-facing entities"

issue "S1.2" "RLS policies via the reusable macro" "sprint-1,security" \
  "feature/auth-tenant-rls" "\`03-database-schema.md\` §4 · ADR-0003" "-" \
"- [ ] Apply RLS through the **one** reusable migration helper — never per-table hand-written SQL
- [ ] Verify: \`SELECT relrowsecurity FROM pg_class\` is true for every tenant-owned table

**This is the sprint that protects the company.** RLS is the *primary* control; app-level filtering is a second layer, never the only one."

issue "S1.3" "core/tenancy.py — resolve tenant_id per request" "sprint-1,security" \
  "feature/auth-tenant-resolution" "\`02-architecture.md\` §7 · \`.claude/rules/security.md\`" "-" \
"- [ ] Admin portal: \`tenant_id\` from the **authenticated user's** tenant association
- [ ] Public site: \`tenant_id\` from the **request domain** — independent of login
- [ ] **Never** from a client-supplied value. No customer endpoint accepts a \`tenant_id\`
- [ ] Set the Postgres session variable that the RLS policies read
- [ ] The \`users\` table — **not the JWT** — is the source of truth for role and tenant"

issue "S1.4" "Supabase Auth + JWT verification + require_role" "sprint-1,security" \
  "feature/auth-jwt-roles" "\`08-auth-roles-spec.md\` §1–2" "-" \
"- [ ] Supabase Auth issues the JWT; FastAPI never sees the password
- [ ] \`core/security.py\` verifies the JWT, extracts \`user_id\` + role
- [ ] \`require_role\` dependency. Roles enforced **server-side** — hiding UI is not a control
- [ ] A restricted role calling an out-of-scope API gets **403**"

issue "S1.5" "Anonymous session + session→account migration" "sprint-1" \
  "feature/auth-anon-session" "\`08-auth-roles-spec.md\` §4 · \`16-feature-favorites-session.md\` · ADR-0015" "-" \
"- [ ] \`X-Session-Id\` header; generated once, held in localStorage
- [ ] On register/login, re-key session-owned rows (favorites, requirement_profiles, chat_conversations, leads) from \`session_id\` to \`user_id\`
- [ ] The \`favorites\` uniqueness constraint must hold — **without it the migration creates duplicates**"

issue "S1.6" "Tenant-isolation test harness" "sprint-1,security" \
  "feature/auth-tenant-isolation-tests" "\`18-test-strategy.md\` §2.3 · ADR-0003" "-" \
"- [ ] TC-AUTH-01, TC-AUTH-02, TC-TENANT-01, TC-TENANT-02
- [ ] Two seeded tenants in every integration run
- [ ] **A helper any future table's isolation test can reuse in three lines.** If the test is laborious it will be skipped — and then ADR-0003 is decoration
- [ ] ⚠️ **Explicit tests for the \`tenants\` table, which has NO RLS backstop.** The only defences are \`require_role([\"super_admin\"])\` and \"derive the tenant from the JWT, never from a request parameter\"

**DoD (doc 15):** cross-tenant access fails **at the DB layer**, not just the API layer."

# --- Sprints 2-4 ----------------------------------------------------------
issue "S2.1" "properties / property_media / amenities + RLS + isolation test" "sprint-2,security" \
  "feature/property-tables" "\`03-database-schema.md\`" "-" \
"- [ ] Tables + migrations
- [ ] **RLS via the macro + a cross-tenant isolation test.** Every new tenant-owned table repeats S1.6. No exceptions"

issue "S2.2" "Property CRUD endpoints" "sprint-2" \
  "feature/property-crud" "\`04-api-spec.md\` §8" "-" \
"- [ ] **Every endpoint must already exist in the spec.** If it doesn't, update the spec first
- [ ] Router → Service → Repository. Routers hold no logic; services write no SQL
- [ ] TC-PROP-03: an agent without \`properties.edit\` gets a **403**"

issue "S2.3" "Property status workflow (six states)" "sprint-2" \
  "feature/property-status-workflow" "\`17-admin-spec/06-property-approvals-status.md\` §2.1" "-" \
"- [ ] draft / pending_approval / published / sold / on_hold / archived
- [ ] TC-PROP-01: \`pending_approval\` is **not publicly visible** until approved
- [ ] **De-indexing on \`sold\` matters as much as indexing** — a sold property left in the embeddings keeps getting recommended, which makes the AI look broken"

issue "S2.4" "Bulk upload with partial import" "sprint-2" \
  "feature/property-bulk-upload" "\`17-admin-spec/05-property-bulk-upload.md\`" "-" \
"- [ ] A real template: correct headers, an example row, allowed values. **Half of all import errors are prevented right here**
- [ ] TC-PROP-02: malformed rows report **per-row** errors, never a full-batch failure
- [ ] **Import the valid rows.** Never make someone fix 14 rows before they get value from the other 128
- [ ] Download the failed rows"

issue "S2.5" "Admin UI: property list + add/edit form" "sprint-2" \
  "feature/property-admin-ui" "\`17-admin-spec/03\`, \`04\` · Stitch prompts doc 11 §7" "-" \
"- [ ] List with status chips from the **semantic ramp** — never primary/secondary/tertiary (ADR-0009)
- [ ] Multi-step add/edit form
- [ ] **Focus rings are \`primary\`, not \`tertiary\`** (ADR-0008)"

issue "S2.6" "Property approvals queue" "sprint-2" \
  "feature/property-approvals" "\`17-admin-spec/06\`" "-" \
"- [ ] Approve & Publish / Reject
- [ ] **Rejection requires a reason** — a rejection without one is a dead end for the agent who submitted it"

issue "S3.1" "GET /properties with structured filters" "sprint-3" \
  "feature/property-public-list" "\`04-api-spec.md\` §4" "-" \
"- [ ] TC-LIST-01: combining price + type + bedrooms returns correctly intersected results
- [ ] Only \`published\` properties are ever visible publicly"

issue "S3.2" "GET /properties/{id}" "sprint-3" \
  "feature/property-public-detail" "\`04-api-spec.md\` §4" "-" \
"- [ ] Unpublished → 404 (never a partial render that leaks the listing exists)"

issue "S3.3" "Public site: listing page" "sprint-3" \
  "feature/public-listing-page" "\`16-customer-spec/02-property-listing.md\` · doc 11 §3" "-" \
"- [ ] Grid / list / map toggle, filters, sort, pagination"

issue "S3.4" "Public site: property details page" "sprint-3" \
  "feature/public-details-page" "\`16-customer-spec/03-property-details.md\` · doc 11 §4" "-" \
"- [ ] Implements **FR5.1–FR5.5**: gallery, floor plan, price breakdown, location + nearby landmarks, similar properties, sticky CTA, agent contact, EMI calculator
- [ ] **TC-DETAILS-01: must survive partial data** — a missing floor plan must not break the layout
- [ ] \"Similar properties\" is recommendation-engine output → it is the **only** tertiary element on the page
- [ ] ❌ **No AI Insights panel.** Price prediction is in no spec and was explicitly dropped (ADR-0012)"

issue "S3.5" "Favorites: anonymous → account migration" "sprint-3" \
  "feature/favorites-session-migration" "\`16-feature-favorites-session.md\` · ADR-0015" "-" \
"- [ ] TC-LIST-02: favorite anonymously → register → **the favorite survived**
- [ ] \`DELETE /properties/{id}/favorite\` must verify the favorite **belongs to the caller**. Scoping by \`property_id\` alone lets one user delete another's — it is the obvious implementation and it is wrong"

issue "S4.1" "leads / lead_notes / lead_activities + RLS + isolation test" "sprint-4,security" \
  "feature/lead-crm-tables" "\`03-database-schema.md\` §3.8" "-" \
"- [ ] Tables + migrations + RLS + cross-tenant isolation test
- [ ] \`leads.user_id\` and \`session_id\` — a lead must be linkable back to the customer who filed it"

issue "S4.2" "POST /leads with idempotency" "sprint-4" \
  "feature/lead-capture-endpoint" "\`04-api-spec.md\` §5 · FR6.4" "-" \
"- [ ] TC-LEAD-01: **every lead has a non-null \`source\`**
- [ ] \`leads.idempotency_key\` + UNIQUE (tenant_id, idempotency_key) — a double-submit must not create two leads"

issue "S4.3" "Public: contact form + callback slot picker" "sprint-4" \
  "feature/lead-contact-form" "\`16-customer-spec/05-contact-page.md\` · doc 11 §10" "-" \
"- [ ] Message vs. callback modes; slot picker on callback (FR6.2)
- [ ] Success **replaces the form in place** (FR6.3) — it does not navigate away
- [ ] Errors keep the entered values. **Never force a re-type**"

issue "S4.4" "Atomic lead claim" "sprint-4" \
  "feature/lead-atomic-claim" "\`03-database-schema.md\` §3.8.1 · ADR-0014" "-" \
"- [ ] Two agents claiming simultaneously must result in **exactly one owner** (FR10.2a)
- [ ] An unclaimed lead is visibly in the shared queue — **never invisible**"

issue "S4.5" "Admin Lead Kanban + table view" "sprint-4" \
  "feature/lead-crm-kanban" "\`17-admin-spec/07\`, \`09\` · doc 11 §8" "gap D1 — no 'info' status color" \
"- [ ] Kanban across the five stages; drag to change stage
- [ ] Table view sortable by **unclaimed age** — the query that surfaces a rotting queue
- [ ] Lead-source chips: **tertiary for Chatbot and AI Search only** — the other sources are neutral
- [ ] TC-LEAD-02: stage changes recorded in \`lead_activities\` with timestamps

**⛔ Blocked:** \`contacted\`, \`site_visit_scheduled\` and \`negotiation\` are *in progress* — not done, not failed, not inert, and **not a warning**. None of success/warning/error/neutral fits. \`neutral\` is a placeholder, not an answer. **Add an \`info\` family to \`DESIGN.md\`.**"

issue "S4.6" "Stale-lead alert (FR10.2b — MANDATORY)" "sprint-4" \
  "feature/lead-stale-alert" "\`01-prd.md\` FR10.2b · ADR-0014" "gap G9a — no job scheduler exists" \
"- [ ] Leads sitting unclaimed past a threshold must alert someone

**⛔ This is the sharpest item in the backlog.**

Manual lead claim (ADR-0014) is only safe **because** of this alert — it is the floor under the entire design. FR10.2b calls it **mandatory, not optional**: *\"without it, manual claim loses leads.\"*

But \`02-architecture.md\` specifies FastAPI \`BackgroundTasks\`, which **only runs after a request and cannot fire on a timer.** There is no scheduler. **A mandatory requirement is unbuildable as specced.**

Either pick a scheduler (\`pg_cron\` is free and already in the stack) or reopen the auto-assignment decision. **Do not build the pipeline and hope.**"

echo ""
echo "────────────────────────────────────────────────────────"
if [[ $DRY_RUN -eq 1 ]]; then
  echo "DRY RUN — nothing was created."
  echo "Run without --dry-run to create the board (requires gh)."
else
  echo "Done. Status now lives in GitHub Issues; structure stays in docs/BACKLOG.md."
fi
