# Risk Register — PropVista CRM

> **Doc 22.** Owns: **project and product risk.**
> `GAPS.md` owns **spec gaps** — things that are unbuildable because a doc doesn't say enough. This owns **risks** — things that could go wrong even if every spec were perfect. Different questions; don't merge them.
>
> **Status:** v1.0 · **Created:** 2026-07-14

---

## How to read this

**Impact × Likelihood**, and — more usefully — *when you'd find out*. A risk you discover late is worth more attention than one you discover early, even at the same severity.

| | |
|---|---|
| 🔴 | Could end the product or the company |
| 🟠 | Would cost serious money or time |
| 🟡 | Would hurt |

---

## 1. 🔴 Cross-tenant data leak

**Impact:** terminal. One real-estate business sees a competitor's buyer pipeline — budgets, phone numbers, timelines. There is no recovering the reputation of a multi-tenant CRM that leaked across tenants.

**Likelihood:** low *if* RLS is genuinely enforced; **high** if the team drifts into relying on application filtering, because that requires being right every single time.

**When you'd find out:** possibly never. A quiet leak leaves no error.

**Mitigation:** RLS as the primary control (ADR-0003), a mandatory isolation test per tenant-owned table, and the RLS migration helper so a new table cannot be created without a policy.

**Residual:** the `tenants` table has **no RLS backstop** — it is the table `tenant_id` points at. Two application-level controls are all that protect it (`19-security-and-privacy.md` T1). **This is the thinnest part of the whole defense and it needs its explicit tests written early, not in Sprint 8.**

---

## 2. 🔴 Silent AI degradation

**Impact:** the product's entire differentiation is three AI features. If they quietly get worse, the product quietly becomes a worse Zillow with a CRM bolted on. Customers don't complain — they leave.

**Likelihood:** **high over time.** Prompts get edited. Models get deprecated and swapped. Listing descriptions get sloppier and embeddings degrade. Nothing about this throws an exception.

**When you'd find out:** **late.** Conventional monitoring is green throughout. This is the defining risk of an AI-first product and conventional engineering practice has no answer to it.

**Mitigation:** the golden eval sets (`18-test-strategy.md` §3) re-run on **every prompt change** — which is why prompts are versioned files, not inline strings. The **fallback rate** and **escalation rate** are the leading indicators, surfaced on the admin AI-config screens for exactly this reason.

**Residual:** the eval suite exists as a spec, not as code. No baselines are recorded anywhere. **Until they are, "the AI got worse" is an opinion, not a measurement.**

---

## 3. 🟠 Bedrock cost runs away

**Impact:** unbounded. It is the only variable cost, and the `ai/*` endpoints are **public and unauthenticated by design** (ADR-0015). A scraper or a bored attacker is a bill, not an outage.

**Likelihood:** near-certain that *someone* probes it. Certain that a retry bug will eventually loop.

**When you'd find out:** when the invoice arrives, unless per-tenant token logging is in place from day one.

**Mitigation:** per-session/IP rate limits, per-tenant soft caps with graceful degradation, per-call token/latency/model logging.

**Residual:** ⚠️ **thresholds are undecided** (`GAPS.md` X1) and there is no per-tenant cost visibility yet. **The runbook currently has no lever to pull** (`20-operations-runbook.md` §4.2). This must close before the AI endpoints are public.

---

## 4. 🔴 DPDP non-compliance blocks the pilot

**Impact:** the product cannot legally launch in its home market. Also: the "right to erasure" **directly conflicts** with the soft-delete-everything rule the CRM is built on.

**Likelihood:** **certain to surface** the moment a real pilot tenant's legal team reads the contract.

**When you'd find out:** at the pilot — i.e. after everything is built. This is the most expensive possible moment.

**Mitigation:** none currently. `19-security-and-privacy.md` §3 is the first time it is written down anywhere in the doc set.

**Action:** consent capture, privacy notice, data export and an erasure mechanism (crypto-shred or field redaction, so pipeline history survives while PII genuinely dies) are **build items that appear in no sprint**. Get counsel; then put them in `15-development-plan.md`.

---

## 5. 🟠 The region trilemma is unresolved

**Impact:** decides latency on every request *and* every AI call, and it cannot be changed cheaply once provisioned.

The bind: this is an **India-first** product (users want `ap-south-1`); **Supabase** should sit in the same region as the backend; and **Bedrock's Claude availability** may not include Mumbai. `10-deployment-devops.md`'s entire rationale for going AWS-native was *"co-locate compute with Bedrock"* — and that rationale has never been checked against an India-first product.

**When you'd find out:** at provisioning, or worse, from user-perceived latency after launch.

**Mitigation:** none. **Confirm Bedrock model availability by region before anything is provisioned** (`GAPS.md` I1).

---

## 6. 🔴 A gap that was never real cost a sprint plan

**What happened.** `CLAUDE.md` carried a stale summary — *"no job scheduler, no email/SMS provider"* — long after `02-architecture.md` decided both (§4.4 `pg_cron` + a jobs worker; §3 SendGrid + Twilio, **2026-07-13**). A spec-set README copied the summary. An agent copied the README. The claim reached **eight documents**, and **FR10.2b — a mandatory requirement — was planned as unbuildable for an entire sprint.**

**Nobody lied.** Every step was a faithful copy of the one above it. That is what makes summary-drift lethal: it doesn't look like an error, it looks like consensus.

**Impact:** a fictitious blocker in the sprint plan, a false "residual" in the G7 closure, a false consequence on ADR-0014, a false limitation in the runbook, and a warning baked into a Stitch prompt — all authored around a constraint that did not exist.

**Likelihood:** it has now happened **twice** (`OWNERSHIP.md` §5 #4 was the first). Assume it recurs.

**Mitigation:**
- `GAPS.md` is the **only** place a gap's state is recorded. Cite the ID; never restate the list.
- **An answered open-question is a lie with a checkbox.** `02-architecture.md` §9 still listed the scheduler as open a day after §4.4 decided it — close the question in the same commit as the decision.
- `scripts/check_drift.py` now has a **`false-gap`** check that hard-fails on any resurrection of these two claims.

**Residual:** the check catches *these* false gaps. It cannot catch the *next* one. **When a gap turns out not to exist, add it to the check** — that is what the check is for.


---

## 7. 🟠 The build is agent-executed, and agents forget

**Impact:** this repo is built by agents across many sessions with **no shared memory**. Every failure this project has already had is a memory failure: two design systems coexisting, 33 specs citing a dead one, a schema fix that never reached its dependents, a paraphrase of the PRD that drifted and produced a false bug report.

**Likelihood:** it has already happened, repeatedly. Assume it continues.

**When you'd find out:** whenever someone reads carefully — which, in a 40-document set, is rarely and late.

**Mitigation:** the DevOS. `OWNERSHIP.md` (one owner per concept), `GAPS.md` (one gap register), `scripts/check_drift.py` (six mechanical checks, each named after a failure that actually happened), and the pre-commit gate.

**Residual:** the check covers what has already gone wrong. It cannot catch the next *novel* kind of drift. **When an incident is caused by drift, add a check** (`20-operations-runbook.md` §6).

---

## 8. 🟡 Supabase is a single point of dependency

Postgres, Auth **and** Storage all sit with one vendor, on a different cloud from the compute. An outage there is a total outage. Data access is at least portable (SQLAlchemy speaks to plain Postgres — ADR-0005); **Auth is not**, and Supabase Auth issues the JWTs for both surfaces.

**Mitigation:** none currently. Accepted for MVP. Worth knowing that the Auth coupling is the sticky part, not the database.

---

## 9. 🟡 No error tracking, no alerting, nobody on call

`20-operations-runbook.md` §3 lists the signals to watch and §4 lists what to do — and **nothing connects them.** No alert routes to a human. Every signal is a dashboard nobody is looking at.

**Mitigation:** wire alerting before production. This is not Phase 3 polish; a runbook nobody is paged into is a document, not an operation.

---

## 10. 🟡 The specs are ahead of the code by an enormous margin

~25 documents, ~32 designed screens, **zero lines of application code.** Every spec is an untested hypothesis until something runs.

The specific danger is not that the docs are wrong — it is that their *volume* creates confidence they haven't earned. The AI Insights panel was fully designed before anyone noticed it was in no requirement. The `info` status color was missing for months and only surfaced when a screen actually needed six states.

**Mitigation:** **start Sprint 0.** Nothing validates a spec like an implementation. Sprints 0–2 are not blocked by any open gap.
