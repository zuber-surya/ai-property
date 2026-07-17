# `.claude/` — Project Guidance for Claude Code

Committed, project-scoped guidance so every Claude Code session builds PropVista CRM consistently.

**🎯 Start here:** Root `CLAUDE.md` + `AGENTS.md` (auto-loaded). Then dive into files here as your task requires.

```
Project root/
├── AGENTS.md         ⭐ AGENTS: Master guide for AI coding agents (read first!)
├── CLAUDE.md         ⭐ MASTER: Non-negotiables, stack, build order (auto-loaded)
├── ROUTE_MAP.md      🗺️  ROUTES: All endpoints, tenant scoping, implementation status
│
└── .claude/
    ├── settings.json # Shared project settings (permission allowlist)
    ├── rules/        # Cross-cutting engineering rules — read as-needed
    │   ├── workflow.md    docs-first process, git, scope, self-check
    │   ├── backend.md     FastAPI layering, style, async, errors
    │   ├── frontend.md    React/TS, ONE route-based app (ADR-0020), state
    │   ├── database.md    schema conventions, Alembic, RLS helper
    │   ├── ai.md          Bedrock/Claude, prompts, tenant scoping, cost
    │   ├── security.md    tenant isolation (RLS), auth, secrets, audit
    │   └── testing.md     pytest/Vitest, mocking Bedrock, golden sets
    └── modules/      # Per-domain playbooks with test cases
        ├── README.md       index: 16 PRD modules → domains
        ├── auth-tenant.md  Auth, roles, tenant scoping
        ├── property.md     Properties, bulk upload, approvals
        ├── lead-crm.md     Lead capture, pipeline, assignment
        ├── ai-chatbot.md   Chatbot, system prompts, handoff
        ├── ai-search.md    AI search, query parsing, ranking
        └── ai-recommendation.md Requirement wizard, matching
```

## Workflow for AI Agents

1. **Read `AGENTS.md` first** (5 min) — Quick Start guide, non-negotiables, common pitfalls
2. **Read `CLAUDE.md`** (2 min, auto-loaded) — Stack decisions, build order
3. **Your task maps to a domain?** → Open `.claude/modules/{domain}.md` (3 min)
   - Names exact `docs/` sections, tables, FR numbers, test cases
4. **Need rules for that domain?** → Read `.claude/rules/{relevant}.md` (varies)
5. **Need routes/endpoints?** → Consult `ROUTE_MAP.md` (master reference)
6. **Always read the owning doc** (e.g., `docs/04-api-spec.md` for endpoints)

These files summarize and *link to* `docs/00`–`docs/15`, which remain the source of truth. If they ever disagree, the `docs/` win — and update whichever is stale.
