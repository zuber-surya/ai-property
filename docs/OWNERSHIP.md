# Ownership Registry — Who Owns What

> **Part of the PropVista DevOS.** See [`.claude/rules/devos.md`](../.claude/rules/devos.md) for the protocol, [`GAPS.md`](GAPS.md) for the gap register.
>
> **Status:** v1.0 · **Created:** 2026-07-14

---

## 1. Why this file exists

For several weeks this project had **two complete design systems** — `13-ui-ux-flows.md` §4 (brass/teal/Fraunces) and `DESIGN.md` (indigo/violet) — and all 33 per-page specs cited the wrong one. Nobody noticed, because nothing in the project could answer the question *"which file is allowed to say what a button looks like?"*

That is the failure this registry prevents. **Every concept has exactly one owner. Everything else links to it and never copies it.**

---

## 2. The registry

| Concept | Owner — the ONLY file allowed to define it | Everyone else must |
|---|---|---|
| **Color tokens, hex values** | `DESIGN.md` | link, never restate a hex |
| **Type scale, fonts** | `DESIGN.md` | link |
| **Spacing, radii, elevation, shadows** | `DESIGN.md` | link |
| **Component treatments** (buttons, inputs, chips, cards, AI widgets) | `DESIGN.md` | link |
| **Status / semantic colors** | `DESIGN.md` → Semantic Status Colors | link |
| **The `tertiary` = AI-only rule** | `DESIGN.md` → Colors | link |
| **Numeric breakpoints** | `13-ui-ux-flows.md` §4.7 | link |
| **Iconography** | `13-ui-ux-flows.md` §4.6 | link |
| **Personas, user flows, site maps** | `13-ui-ux-flows.md` §1–3 | link |
| **Functional requirements (FR numbers)** | `01-prd.md` | cite the FR, don't paraphrase it |
| **Module definitions (1–16)** | `01-prd.md` | cite |
| **REST endpoints, request/response shapes, error envelope** | `04-api-spec.md` | cite the path; never invent one |
| **Tables, columns, enums, RLS policy pattern** | `03-database-schema.md` | cite |
| **Folder structure, layering, tenancy strategy** | `02-architecture.md` | follow |
| **Auth, roles, permission matrix** | `08-auth-roles-spec.md` | cite |
| **Coding conventions + the §8 self-check** | `09-coding-standards.md` | follow |
| **Environments, CI/CD, hosting, provider choices** | `10-deployment-devops.md` | cite |
| **Sprint sequencing, `TC-*` acceptance cases** | `15-development-plan.md` | cite the TC id |
| **Task structure** — task IDs, subtasks, branch names, blocked-by-gap index | `BACKLOG.md` | cite the task id |
| **Task STATUS** — TODO → WIP → DONE | **GitHub Issues** (not a file) | Never record status in a doc. A markdown status column is hand-maintained state, and it will lie. |
| **Test levels, AI evaluation strategy, gates** | `18-test-strategy.md` | cite |
| **Threat model, PII handling, DPDP obligations** | `19-security-and-privacy.md` | cite |
| **Incident response, runbooks, signals** | `20-operations-runbook.md` | cite |
| **Branching, versioning, release path, rollback** | `21-release-management.md` | cite |
| **Project & product risk** (≠ spec gaps) | `22-risk-register.md` | cite |
| **Why a decision was made** | `adr/README.md` | cite the ADR number; **never re-argue a settled decision inline** |
| **Repo entry point / orientation** | `README.md` (root) | — |
| **Chatbot behavior + prompt design** | `05-ai-chatbot-spec.md` | cite |
| **AI search behavior** | `06-ai-search-spec.md` | cite |
| **AI recommendation behavior** | `07-ai-recommendation-spec.md` | cite |
| **NFRs** | `12-srs.md` | cite |
| **Within-screen interaction sequences** | `14-screen-workflows.md` | cite |
| **Per-page customer specs** (layout, workflow, states, edge cases) | `16-customer-spec/*.md` | — |
| **Per-screen admin specs** | `17-admin-spec/*.md` | — |
| **Stitch design prompts** | `11-stitch-design-prompts.md` | — |
| **Open gaps and their state** | `GAPS.md` | cite the gap ID; **never re-declare a gap locally** |
| **This registry** | `OWNERSHIP.md` | — |

---

## 3. The five values that must never be forked

These are the ones that have actually caused damage. A mechanical check enforces them — see `scripts/check_drift.py`.

| Value | Lives only in | If you find it elsewhere |
|---|---|---|
| A **hex color** | `DESIGN.md` | It's a fork. Replace with a token name. |
| An **endpoint path** (`/admin/...`, `/portal/...`) | `04-api-spec.md` | Either it's specced (cite it) or it's invented (add to the spec first). |
| A **table or column name** | `03-database-schema.md` | Cite it; don't redefine its type or constraints. |
| An **FR number** | `01-prd.md` | Cite it; don't restate the requirement in your own words — that paraphrase *will* drift (it already did, see §5). |
| A **gap ID** (`G1`…`G9`) | `GAPS.md` | Cite the ID. Don't say "this is blocked" without pointing at the register. |

### 3.1 The one sanctioned exception

`11-stitch-design-prompts.md` §17 and §18 **do** inline a condensed copy of the `DESIGN.md` tokens. This is deliberate: a single-paste Stitch prompt cannot reference another file.

They are marked in-file as **generated artifacts**. The rule is: *if `DESIGN.md` changes, regenerate those two sections.* Never hand-edit the tokens there. The drift check knows about this exception and will tell you when the two have diverged.

---

## 4. Change propagation — the protocol

**When you change an owning file, you own the sweep.** A fix that lands in one doc and not its dependents is worse than no fix, because now two files disagree and both look authoritative.

```
1. Change the owning doc.
2. Grep for everything that cites it.
3. Update every citation in the same commit.
4. Run scripts/check_drift.py.
5. Only then implement.
```

**Known dependency edges** (who reads whom):

| If you change… | You must sweep… |
|---|---|
| `DESIGN.md` | `11-stitch-design-prompts.md` (**incl. regenerating §17 + §18**), `13-ui-ux-flows.md` §4, `16-customer-spec/README.md` §4.7, `17-admin-spec/README.md` §4.5, any spec citing a status color |
| `03-database-schema.md` | every `16-`/`17-` spec's §7 "Data Touched", and **`GAPS.md`** — closing a schema gap does not close it in the specs that cite it |
| `04-api-spec.md` | every `16-`/`17-` spec's §6 "API Calls", and `GAPS.md` |
| `01-prd.md` | the specs citing that FR, `15-development-plan.md`, `11-stitch-design-prompts.md` |
| `GAPS.md` (closing a gap) | **every file that mentions that gap ID** — this is the sweep that was missed once already |

---

## 5. The failures this file exists to prevent

Real, from this project. Kept here because a rule without its scar tissue gets deleted by the next person who finds it inconvenient.

| # | What happened | Rule it produced |
|---|---|---|
| 1 | Two complete design systems coexisted; 33 specs cited the dead one | §2 — one owner per concept |
| 2 | A third prompt doc (`stitch-prompts.md`) appeared, duplicating doc 11 with no design system in it | §2 — a new file must claim an unowned concept, or it doesn't get created |
| 3 | Schema v1.1 closed G1/G2/`favorites`-uniqueness/`leads.user_id`; three portal specs still call them blocking | §4 — closing a gap requires the sweep |
| 4 | Doc 11 §4 paraphrased the PRD. The paraphrase was wrong. It was trusted, and produced a false bug report | §3 — cite FRs, never restate them |
| 5 | `SPRINT0_PLAN.md` specifies `psycopg2` (sync) against an async-mandatory architecture, plus a package that doesn't exist | §4 — a plan is checked against the rules before it's executed |
| 6 | 14 files modified, zero commits, two days of decisions with no revert path | `.claude/rules/devos.md` — checkpoint discipline |

---

## 6. Adding a new file

Before creating one, answer: **which concept does it own that nothing else owns?**

If the honest answer is "none — it summarizes things other files own," **do not create it.** That file will drift, and someone will trust it. That is exactly how failures 2 and 4 happened.
