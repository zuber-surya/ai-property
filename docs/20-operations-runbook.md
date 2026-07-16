# Operations Runbook — PropVista CRM

> **Doc 20.** Owns: **what to do when it's broken.**
> `10-deployment-devops.md` owns *how it gets deployed*. This owns *what happens at 2am*.
>
> **Status:** v1.0 (pre-production — written before the first deploy, deliberately) · **Created:** 2026-07-14

---

## 1. Read this first

**Nothing is deployed yet.** This runbook is written *before* the first production incident rather than after, which is the only time you can write one honestly — after the first incident you write down what you did, not what you should have done.

It will be wrong in places. Update it **after every incident**, in the same PR as the fix.

---

## 2. What "broken" means here

This system fails in two very different ways, and the second one is the dangerous one.

**Loud failures** — the backend is down, `/health` is red, the site 500s. Obvious, alarming, and usually quick to fix.

**Quiet failures** — the AI degrades. Search stops finding things. The bot starts inventing listings. Recommendations go random. **Nothing throws. Nothing pages. The dashboards are green.** Customers just quietly get worse answers and leave. This is the failure mode that will actually cost you money, and no conventional monitoring will tell you it is happening.

**So the most important number in this system is the AI fallback rate**, not uptime. It is the early-warning signal that the AI layer is degrading, and it is visible on `/admin/ai-config/search-insights` (`17-admin-spec/16`).

---

## 3. Signals to watch

| Signal | Where | Means |
|---|---|---|
| **AI search fallback rate** rising | Search insights | The parse step is failing. The AI layer is degrading **silently**. Investigate before customers notice. |
| **Chatbot escalation rate** rising | Chat logs (`17-admin-spec/15`) | The bot is failing to answer. It is the number that tells you the bot is getting worse. |
| Bedrock latency (p95) | CloudWatch / structured logs | Every AI call logs latency, tokens and model ID. If p95 climbs, chat and search feel broken even when they "work". |
| **Bedrock spend** | Cost tracking, per tenant | The only unbounded variable cost. A spike is either abuse or a bug — both need action within hours, not days. |
| `/health` | App Runner / ECS | Loud failure. |
| 5xx rate | CloudWatch | Loud failure. |
| **Escalated chats unhandled** | Chat logs | Not an infra signal — a *human* one. Someone is waiting right now. It is the only genuinely real-time thing in the product. |

---

## 4. Runbooks

### 4.1 The AI layer is degrading (fallback rate up, or bot quality complaints)

**Do not restart anything.** This is almost never an infrastructure fault.

1. Check **Bedrock latency and error rate** in the structured logs. Timeouts present as parse failures downstream.
2. Check **whether a prompt changed**. Prompts are versioned files (`app/ai_clients/prompts/*.py`). `git log` that directory. **A prompt change is the most likely cause of a quality regression**, which is exactly why they are versioned files and not inline strings.
3. Check **whether the model ID changed** — a silent model deprecation or a config change moves you to a different model with different behavior.
4. Run the **AI eval suite** (`18-test-strategy.md` §3) against the golden set and compare with the recorded baseline. This is the only way to convert "it feels worse" into a number.
5. If a prompt change caused it: **revert the prompt**. Prompts revert independently of the application — that is the entire point of the `ai_clients/` isolation.

### 4.2 Bedrock spend spike

1. Check **per-tenant token usage**. Is it one tenant or all of them?
2. One tenant → check `ai/*` request volume from that tenant's domain. Likely abuse or a scraping loop.
3. All tenants → likely a code path calling Bedrock in a loop, or a retry storm. Check for a recently deployed change to a service that calls an AI client.
4. **Mitigate first, diagnose second:** tighten the rate limit or drop the per-tenant soft cap. Degradation (fallback to filter search) is the designed behavior when a cap is hit — it is not an outage.
5. ⚠️ Rate-limit thresholds are **not yet set** (`GAPS.md` X1). Until they are, this runbook has no lever to pull. **Fix that before production.**

### 4.3 Suspected cross-tenant data leak

**Stop. This is the worst thing that can happen to this product (ADR-0003).**

1. **Preserve evidence before you fix anything.** The audit log (actor, action, entity, timestamp) is the record. Do not let it roll.
2. Determine scope: which tenants, which tables, read or write.
3. **Check RLS is actually enabled on the table in question** — `SELECT relrowsecurity FROM pg_class WHERE relname = '<table>'`. A migration that created a table without applying the RLS helper is the most likely cause.
4. Remember the **known thin spot**: the `tenants` table has **no RLS backstop** (`19-security-and-privacy.md` T1). If the leak is tenant metadata, look there first.
5. **This is a personal-data breach with a reporting clock under DPDP.** There is currently no breach-notification process (§6). Escalate to whoever owns legal *immediately* — the engineering fix is not the whole obligation.

### 4.4 Backend down / `/health` red

1. App Runner / ECS health-check status and recent deploys.
2. **Roll back to the previous image** (`21-release-management.md` §4). Diagnose afterwards. A rollback is cheap; a long investigation with the site down is not.
3. If `/health` is green but requests hang → suspect **event-loop blocking**. The usual culprit is a synchronous call in an `async def` path. This system mandates async end-to-end precisely because of this, and `psycopg2` (synchronous) has already been proposed once in a plan (`GAPS.md` §6). If it ever ships, this is the symptom.

### 4.5 Database migration failed mid-deploy

1. Migrations run **only through CI**, never by hand — so the failure is in the pipeline, not on someone's laptop.
2. Do **not** hand-fix the database. That is how the schema and `03-database-schema.md` drift, and drift is the failure this project has already paid for once.
3. Write a **new** migration that corrects forward. Alembic `downgrade` is a fallback, not the first move — downgrades that drop columns lose data.

### 4.6 An escalated chat is sitting unhandled

Not an infra incident. A **customer is waiting right now**, and this is the only real-time obligation in the product. Route it to an on-duty agent. If it happens repeatedly, the escalation notification rule is not working.

⚠️ **Until the notifier code ships, in-app is the only channel that actually delivers** — so this queue is a **pull** signal and works only if someone is looking at the screen. That is an *implementation* state (§5), **not a spec gap**: the providers are decided (SendGrid + Twilio, `02-architecture.md` §3).

> This paragraph used to cite *"`GAPS.md` G9b"* as the reason. **There is no G9b** — it is one of the two gaps that never existed (`GAPS.md` §5A), and citing a retracted ID as a live blocker is how the false claim stayed alive. A proactive alert is buildable today: add a `pg_cron` job beside `mark_stale_leads()` (§4.4) — *"escalated and unclaimed for N minutes → enqueue a notification"*.

---

## 5. What we cannot do yet

Stated plainly, so nobody discovers it during an incident:

| Gap | Consequence |
|---|---|
| **Email/SMS not yet wired** | SendGrid and Twilio are *chosen* (`02-architecture.md` §3) but not yet integrated, and **Indian SMS needs DLT registration first**. Until then, alerts reach nobody who isn't already looking at the admin portal. |
| **No error tracking** chosen (Sentry suggested, unconfirmed) | You find out about frontend errors from customers. |
| **No alerting thresholds** defined | Every signal in §3 is a dashboard nobody is watching at 2am. |
| **No on-call rotation** | — |
| **No breach-notification process** | DPDP has a clock; we have no process (§4.3). |

**These are not "nice to haves". §3 lists signals and §4 lists responses, and right now nothing connects them: no alert routes to a human.** Closing that loop is a pre-production requirement, not a Phase 3 polish item.

---

## 6. After an incident

1. Write it down here, in the same PR as the fix.
2. If the incident was caused by drift — two docs disagreeing, a spec stale against the schema — **add a check to `scripts/check_drift.py`**. That is what the drift check is for: every check in it exists because that exact failure already happened once.
3. Blameless. The interesting question is never who, it is *what made this possible*.
