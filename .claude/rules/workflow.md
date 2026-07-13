# Rule: Workflow & Process

Applies to: every task, every session. Source: `docs/09-coding-standards.md` §1/§4/§8, `docs/15-development-plan.md` §2.

## Docs are the source of truth
- Read the relevant `docs/` section before writing code. Point work at specific doc sections, not memory.
- If a requirement changes, **update the doc first, then implement.** Never let code drift ahead of the specs.
- Every new endpoint must already exist in `docs/04-api-spec.md` and trace to a PRD module (`docs/01-prd.md`). If it doesn't, add it to the spec first.

## Scope of work
- **One module or one sprint task per session.** Don't attempt "the whole backend" at once. Follow the sprint sequencing in `docs/15-development-plan.md` §4.
- Write tests **alongside** the implementation, not after.
- Prefer explicit over clever — code is built incrementally by an agent across many sessions and must read cleanly without the conversation history that produced it.

## Git
- Branches: `feature/<module>-<short-desc>` or `fix/<short-desc>`.
- Commits: short imperative summary referencing the PRD module (e.g. `Add property bulk-upload endpoint (PRD Module 9)`).
- Small, focused commits. **No direct commits to `main`.**

## Self-check before "done"
Run the checklist in `docs/09-coding-standards.md` §8:
- [ ] Matches the folder/layering in `docs/02-architecture.md`?
- [ ] Every new endpoint exists in `docs/04-api-spec.md` (or spec updated first)?
- [ ] Tenant-owned tables/queries respect `tenant_id` scoping?
- [ ] AI prompts in `app/ai_clients/prompts/`, not inlined?
- [ ] DB changes go through an Alembic migration?
- [ ] Secrets read from env vars, not hardcoded?
- [ ] Tests cover the new logic (+ tenant-isolation tests if a new tenant-owned table was added)?
