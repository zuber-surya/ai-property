# Release Management — PropVista CRM

> **Doc 21.** Owns: **branching, versioning, how a change reaches production, and how it gets pulled back.**
> `10-deployment-devops.md` owns the *pipeline mechanics*. This owns the *process around it*.
>
> **Status:** v1.0 · **Created:** 2026-07-14

---

## 1. Branching

```
main            always deployable. Protected. No direct commits.
 └─ feature/<module>-<desc>     e.g. feature/lead-crm-kanban
 └─ fix/<desc>                  e.g. fix/favorite-delete-scoping
```

- **No direct commits to `main`.** Ever. (`.claude/rules/workflow.md`)
- Small, focused commits. The message references the PRD module: `Add property bulk-upload endpoint (PRD Module 9)`.
- **Commit at each coherent decision, not at the end of the session.** This project once accumulated two full days of decisions across 14 files with zero commits, no diff and no revert path. That is the failure this rule exists to prevent.

## 2. What must be true before a PR merges

| Gate | Enforced by |
|---|---|
| No **new** drift | `scripts/check_drift.py` (pre-commit + CI). Existing debt is baselined — ADR-0016. |
| Lint + format clean | `ruff`, `black`, `eslint`, `prettier` |
| Unit + integration tests pass | `pytest` |
| **Tenant-isolation test exists for any new tenant-owned table** | Review. Non-negotiable — ADR-0003. |
| Frontend types + component tests pass | `tsc`, `vitest` |
| **Every new endpoint already exists in `04-api-spec.md`** | Review. If it doesn't, the spec changes first. |
| The §8 self-check (`09-coding-standards.md`) | Manual, and **that is a weakness** — see `18-test-strategy.md` §6 |

**If a change touches an owning doc, the same PR sweeps its dependents** (`OWNERSHIP.md` §4). A fix that lands in one doc and not its dependents is worse than no fix.

## 3. Versioning

- **The application is not semver'd.** It is a SaaS with one deployed version; there is no consumer pinning a release. Version = the git SHA, and that is what gets tagged on the image.
- **The API is versioned in the path** (`/api/v1/...`). A breaking change to a shape that a frontend depends on means `v2`, not an edit to `v1` — the two frontends deploy independently of the backend and will briefly be running old code against new API.
- **Prompts are versioned in-file** (`# v2 - added escalation instruction`). This is not decoration: when eval scores shift, the prompt version is the first thing you check (`20-operations-runbook.md` §4.1).
- **The schema is versioned by Alembic revision.** That is the only truth about what shape the database is in.

## 4. The release path

```
merge to main
   → build (backend image — API + jobs worker, one static frontend build)
   → alembic upgrade head  →  STAGING
   → deploy STAGING
   → smoke: /health, the 4 money paths (18-test-strategy.md §2.5)
   → [ MANUAL APPROVAL ]
   → alembic upgrade head  →  PRODUCTION
   → deploy PRODUCTION
   → watch: 5xx rate, Bedrock latency, AI fallback rate (20-operations-runbook.md §3)
```

**The manual gate before production is deliberate.** This is multi-tenant: one bad migration touches every tenant's data simultaneously. There is no blast-radius containment between tenants — that is the price of a shared schema.

**Migrations are applied only by CI.** Never by hand, in any environment, including early dev. That rule is what keeps `03-database-schema.md` and the live database from drifting, and it is the same principle as the drift check applied to the data layer.

## 5. Rollback

**Code rolls back. Migrations mostly do not.** Understanding that asymmetry is the whole of this section.

| Situation | Move |
|---|---|
| Bad code, schema unchanged | **Redeploy the previous image.** Fast, safe, boring. Do this first and diagnose after. |
| Bad code, schema changed **additively** (new nullable column, new table) | Roll back the code. **Leave the migration.** An additive migration is harmless to old code — which is exactly why migrations should be additive by default. |
| Bad code, schema changed **destructively** (dropped/renamed column) | You are in trouble, and you were in trouble before you deployed. `downgrade` may not restore data. **Restore from backup**, with the data loss between backup and now. |
| Bad prompt (AI quality regression) | **Revert the prompt file alone.** No application rollback needed — the `ai_clients/` isolation exists precisely so prompt changes and business logic move independently. |
| Bad data (a bulk import went wrong) | Properties are **soft-deleted**, so a bad bulk import is recoverable — `deleted_at` is set, not `DELETE`. |

**Therefore: prefer expand-then-contract.** Add the new column, deploy code that writes both, backfill, deploy code that reads the new one, and only *then* — in a later release — drop the old. It is slower and it means a destructive change is never coupled to the release that needs it.

## 6. Backups

Supabase provides managed Postgres backups. **Confirm the retention window on the actual plan and record it here** — an unverified backup is not a backup (`GAPS.md`).

`property_embeddings` is the one table that can be **fully regenerated** from `properties` (`06-ai-search-spec.md`). It is not a single point of unrecoverable failure, which is worth knowing when you are deciding what to restore first.

## 7. Hotfix

1. Branch from `main` (not from a feature branch).
2. Fix, with a test that fails without the fix.
3. The same gates apply. **A hotfix that skips the drift check or the isolation test is how the next incident is born.**
4. Straight through staging to production, same path, same manual gate. The gate is the point.

## 8. Open questions

- [ ] CI provider — GitHub Actions assumed, unconfirmed (`10-deployment-devops.md` §9).
- [ ] Who holds the production approval gate?
- [ ] Supabase backup retention on the chosen plan — **unverified**.
- [ ] Is there a staging→production data-refresh path? If so it must **not** copy buyer PII into a lower environment (`19-security-and-privacy.md`).
