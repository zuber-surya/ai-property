#!/bin/bash
# Script to generate GitHub issues from PropVista CRM backlog and development plan
# This script creates issue bodies that can be used with GitHub CLI or API

set -e

REPO="zuber-surya/ai-property"

echo "Generating GitHub issues for PropVista CRM..."
echo "Repository: $REPO"
echo ""

# Function to create an issue body
create_issue() {
  local title="$1"
  local body="$2"
  local labels="$3"

  echo "=== ISSUE: $title ==="
  echo "Labels: $labels"
  echo "Body:"
  echo "$body"
  echo ""
  echo "---"
  echo ""
}

# Sprint 0 Issues
create_issue "Scaffold backend/ folder structure" \
"**Branch:** feature/sprint0-backend-scaffold
**Spec:** 02-architecture.md §4.2

Tasks:
- [ ] Structure per §4.2: api/v1/, services/, repositories/, models/, schemas/, ai_clients/prompts/, core/
- [ ] requirements.txt: fastapi, uvicorn[standard], sqlalchemy[asyncio], asyncpg, alembic, pydantic, pydantic-settings, boto3, pgvector, python-jose
- [ ] Dev deps: pytest, pytest-asyncio, httpx, ruff, black
- [ ] app/core/config.py - all settings load here, env vars only
- [ ] app/main.py - FastAPI instance, v1 router, /health → {\"status\":\"ok\"}
- [ ] Shared exception handler → error envelope in 04-api-spec.md §1
- [ ] .env.example with placeholders

Acceptance: uvicorn app.main:app --reload serves /health → 200; ruff + black clean." \
"task,sprint-0"

create_issue "Scaffold public-site/ folder structure" \
"**Branch:** feature/sprint0-public-site-scaffold
**Spec:** 02-architecture.md §5.2 · .claude/rules/frontend.md

Tasks:
- [ ] Vite + React + TypeScript, strict mode on, no unjustified any
- [ ] @vitejs/plugin-react (note: @vitejs/plugin-tsx does not exist)
- [ ] Folder shape: pages/, components/, hooks/, api/, context/
- [ ] eslint + prettier; vitest + React Testing Library, one smoke test
- [ ] Design tokens from DESIGN.md → CSS-var / Tailwind config
- [ ] This is a second sanctioned fork of the tokens - mark generated file and add to check_drift.py watch list

Acceptance: npm run dev serves a page; build, lint, test all pass." \
"task,sprint-0"

create_issue "Scaffold admin-portal/ folder structure" \
"**Branch:** feature/sprint0-admin-portal-scaffold
**Spec:** Same shape as public-site/, Not tenant-branded (ADR-0010)

Acceptance: Same as public-site scaffold." \
"task,sprint-0"

echo "Issue generation complete!"
echo ""
echo "To create these issues using GitHub CLI (once authenticated):"
echo "gh issue create --repo $REPO --title \"<title>\" --body \"<body>\" --label \"<labels>\""
echo ""
echo "Or copy/paste the issue bodies above into the GitHub web interface."