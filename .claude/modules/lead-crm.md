# Module: Lead / CRM

Covers PRD Module 6 (Contact / Lead Capture, public), Module 10 (Lead & CRM Pipeline, admin), and Module 12 (Agent/Broker Management). Every AI feature ultimately funnels into a lead here.

**Read:** `docs/04-api-spec.md`, `docs/01-prd.md` §7/§11/§13, `docs/03-database-schema.md`.
**Rules:** `backend`, `database`, `frontend`, `testing`.

## Tables
`leads`, `lead_notes`, `lead_activities` (stage history), `agents` (subset of `users`).

## Key requirements
- FR6.1–6.4 Contact form (modal + inline), callback with time-slot picker, submit confirmation, **every submission creates a lead** tagged with source page + channel. Idempotent — no duplicate lead per submission.
- FR10.1 Kanban pipeline: New → Contacted → Site Visit Scheduled → Negotiation → Closed/Lost (stage names configurable). Table view alternative (FR10.5).
- FR10.2 Manual or automatic (round-robin/rules-based) assignment to agents.
- FR10.3 Notes, call logs, follow-up reminders per lead.
- FR10.4 Source tracking: chatbot, AI search inquiry, requirement form, contact form, walk-in. Every lead has a non-null source and an owner (or explicit "unassigned").
- Stage changes are **timestamped** in `lead_activities` for reporting.
- FR12.x Agent profile, performance view (leads closed, response time, conversion rate), leaderboard — metrics recompute as leads change stage/owner.

## Integration points
- AI Chatbot (`ai-chatbot`) creates leads via tool call with `source = "chatbot"`.
- Contact/callback submissions and AI-search inquiries create leads with the corresponding source.

## Acceptance
- No duplicate lead records for a single submission; every lead has a traceable source and owner state; stage changes timestamped.
