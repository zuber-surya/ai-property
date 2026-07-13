# `.claude/` — Project Guidance for Claude Code

Committed, project-scoped guidance so every Claude Code session builds PropVista CRM consistently. The root `CLAUDE.md` is loaded automatically each session; the files here are read **on demand** when you work in the relevant area.

```
.claude/
├── settings.json     # Shared project settings (permission allowlist for dev tooling)
├── rules/            # Cross-cutting engineering rules — read the ones your task touches
│   ├── workflow.md     docs-first process, git, scope, self-check
│   ├── backend.md      FastAPI layering, style, async, errors
│   ├── frontend.md     React/TS, two-app split, state
│   ├── database.md     schema conventions, Alembic, RLS helper
│   ├── ai.md           Bedrock/Claude, prompt files, tenant scoping, cost
│   ├── security.md     tenant isolation (RLS), auth, secrets, audit
│   └── testing.md      pytest/Vitest, mocking Bedrock, golden sets
└── modules/          # Per-domain playbooks
    ├── README.md       index: 16 PRD modules → backend domains
    ├── auth-tenant.md  ├─ property.md      ├─ lead-crm.md
    └── ai-chatbot.md   └─ ai-search.md     └─ ai-recommendation.md
```

## How to use
1. Start from the root `CLAUDE.md` (auto-loaded) for the non-negotiables and doc map.
2. When a task targets a domain, open its `modules/*.md` playbook — it names the exact `docs/` sections, tables, FR numbers, and acceptance tests.
3. Follow the `rules/*.md` files your change touches. `rules/security.md` (tenant isolation) applies to essentially everything.
4. These files summarize and point into `docs/00`–`docs/15`, which remain the source of truth. If they ever disagree, the `docs/` win — and update whichever is stale.
