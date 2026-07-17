# Module: Lead / CRM

Covers PRD Module 6 (Contact / Lead Capture, public), Module 10 (Lead & CRM Pipeline, admin), and Module 12 (Agent/Broker Management). Every AI feature ultimately funnels into a lead here.

**Read:** `docs/04-api-spec.md`, `docs/01-prd.md` §7/§11/§13, `docs/03-database-schema.md`.
**Rules:** `backend`, `database`, `frontend`, `testing`.

## Tables
`leads`, `lead_notes`, `lead_activities` (stage **and ownership** history). Agents are `users` with `role = 'agent'` — **there is no `agents` table**.

## Key requirements

⚠️ **This list cites FR numbers. It does not restate them — open `01-prd.md` §11.** Two rows here previously paraphrased the PRD and the paraphrase drifted: it said stage names were *"configurable"* and assignment was *"manual or automatic (round-robin/rules-based)"*. **Both were decided the other way on 2026-07-13**, and this file — which agents are told to read *first* — kept saying otherwise. That is the exact failure `OWNERSHIP.md` §3 forbids ("cite the FR, never restate it"), and it is how doc 11 once produced a false bug report.

- **FR6.1–6.4** — contact form, callback slot picker, confirmation, every submission creates a lead. Idempotent via `leads.idempotency_key`.
- **FR10.1** — Kanban pipeline. **Stages are a FIXED enum** (`new` · `contacted` · `site_visit_scheduled` · `negotiation` · `closed_won` · `closed_lost`). Configurable stage names are **out of scope for MVP** — ADR-0013, `03-database-schema.md` §10.1 #1. Table view alternative: FR10.5.
- **FR10.2** — **Manual claim from a shared queue. There is NO auto-assignment** — not round-robin, not rules-based (ADR-0014, `03-database-schema.md` §3.8.1). New leads are created `assigned_agent_id = NULL` and every agent sees the shared `new` column.
  - **FR10.2a** — the claim is **atomic**: a conditional `UPDATE … WHERE assigned_agent_id IS NULL`. Two agents racing → exactly one winner, the loser gets **409**.
  - **FR10.2b** — the stale-lead alert is **MANDATORY, not optional**: manual claim loses leads without it. ✅ Buildable — `pg_cron` + the jobs worker (`02-architecture.md` §4.4, `mark_stale_leads()` listed by name).
- **FR10.3** — notes, call logs, follow-up reminders per lead.
- **FR10.4** — source tracking: `chatbot` · `ai_search_inquiry` · `requirement_form` · `contact_form` · `property_details` · `walk_in`. Every lead has a non-null source; ownership is either an agent or *visibly* unclaimed, never invisible.
- Stage **and ownership** changes are timestamped in `lead_activities` — it is the source of truth for every time-based metric, **not** `leads.updated_at`.
- **FR12.x** — agent profile, performance, leaderboard. Metrics come from **one `metrics_service`** (`03-database-schema.md` §6); no screen writes its own metric SQL.

## Integration points
- AI Chatbot (`ai-chatbot`) creates leads via tool call with `source = "chatbot"`.
- Contact/callback submissions and AI-search inquiries create leads with the corresponding source.

## Acceptance / test cases (from `docs/15`)
- `TC-LEAD-01` every lead has a non-null `source`.
- `TC-LEAD-02` stage changes recorded in `lead_activities` with correct timestamps.
- `TC-TENANT-01` cross-tenant lead access fails **at the DB layer** (every new tenant-owned table — ADR-0003).
- Simultaneous double-claim → **exactly one owner** (FR10.2a).
- No duplicate lead records for a single submission (FR6.4).
