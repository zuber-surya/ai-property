# Rule: The Development Operating System

Applies to: every session, human or agent. Source: `docs/OWNERSHIP.md`, `docs/GAPS.md`, `scripts/check_drift.py`.

This project is **docs-as-source-of-truth, executed by agents**. Its characteristic failure is not bad code — it's **drift**: two files quietly claiming the same authority, or a fix landing in one doc and never reaching its dependents. Every rule below exists because that already happened. See `OWNERSHIP.md` §5 for the incident log.

---

## 1. One owner per concept

Before you write a value, ask **who owns it** (`docs/OWNERSHIP.md`).

- A hex color → `DESIGN.md`. Cite the token name, never the value.
- An endpoint → `04-api-spec.md`. If it isn't there, it doesn't exist — add it to the spec first.
- A table or column → `03-database-schema.md`.
- An FR → `01-prd.md`. **Cite the number. Never restate the requirement in your own words** — that paraphrase will drift, and someone will trust it. (This is not hypothetical: doc 11 paraphrased the PRD, the paraphrase was wrong, and it produced a false bug report.)
- A gap → `docs/GAPS.md`. Never declare something "blocked" locally without a gap ID.

## 2. Never fork the truth

If a value appears in two files, one of them is already wrong — you just don't know which yet.

**The one sanctioned exception** is `11-stitch-design-prompts.md` §17/§18, which inline a condensed copy of the `DESIGN.md` tokens because a single-paste Stitch prompt can't reference a file. They are labelled generated artifacts. **If `DESIGN.md` changes, regenerate them.** Never hand-edit a token there. `check_drift.py` watches this pair.

## 3. Changing an owning doc means owning the sweep

```
1. Change the owning doc.
2. Grep for every file that cites it.
3. Update every citation IN THE SAME COMMIT.
4. Run: python scripts/check_drift.py
5. Only then implement.
```

A fix that lands in one doc and not its dependents is **worse than no fix** — now two files disagree and both look authoritative. Closing a gap in `GAPS.md` without sweeping the specs that cite it is the exact failure this rule exists to stop.

Dependency edges are listed in `OWNERSHIP.md` §4.

## 4. Run the check

```bash
python scripts/check_drift.py          # full report
python scripts/check_drift.py --quiet  # exit code only
```

**Nine** checks, each named after the failure it prevents. It is wired to `.githooks/pre-commit` (`git config core.hooksPath .githooks`). **Do not `--no-verify` past it.** If a finding is wrong, fix the check — a false positive that gets ignored trains everyone to ignore the true ones too.

```bash
python scripts/check_drift.py --selftest   # the checks' own fixtures
```

**The checks are themselves tested**, because two of them have already been silently broken:

- `false-gap` reported **0 while eight resurrections sat live** — it had borrowed a burial pattern that matched the word *"was"*, so any line containing the commonest verb in English bought an exemption.
- `stale-gap` matched the bare word **`gap`** — tautological, since every citation of a gap ID contains it. The moment `CLOSED_GAPS` grew past G1/G2 it produced **9 findings, all false**, including the very section that closes G7.

Every phrasing that beat a check is now a fixture. **When you close a gap, add its ID to `CLOSED_GAPS` in the same commit** — the check then finds the citations for you, and the findings *are* the sweep list.

**The baseline is currently all zeros** (`.drift-baseline.json`) — the 25 stale-gap citations and 2 async violations that used to sit here were swept (tasks `P.4`/`P.5`). **Zero is not "nothing left to check"** — it is the state the gate is meant to hold. Adding drift is what fails a commit (ADR-0016); if you genuinely reduce it, re-baseline with `--accept`. **Lowering the baseline is the only sanctioned direction.**

## 5. Checkpoint discipline

Two days of decisions once sat in an uncommitted working tree with no diff and no revert path.

- Branch: `feature/<module>-<desc>` or `fix/<desc>`. **No direct commits to `main`.**
- Commit at each coherent decision, not at the end of the session.
- Reference the PRD module in the message.

## 6. A plan is checked against the rules before it is executed

`SPRINT0_PLAN.md` pinned `psycopg2` (synchronous) against a `CLAUDE.md` rule that every I/O endpoint is `async` — and listed an npm package that doesn't exist. Nobody checked the plan against the rules, because nothing said to.

**Now something does.** Before executing any plan, run the drift check against it and read it against `.claude/rules/`.

## 7. Don't create a file that owns nothing

Before adding a doc, answer: **which concept does it own that nothing else owns?**

If the honest answer is "none — it summarizes things other files own," **don't create it.** It will drift, and someone will trust it. That is precisely how `docs/stitch-prompts.md` came to exist: a third prompt doc, containing no design system, instructing people to paste design-free text into Stitch.

## 8. Before "done"

- [ ] Did I change an owning doc? Then did I sweep its dependents (§3)?
- [ ] Does every value I wrote trace to its owner (§1)?
- [ ] `python scripts/check_drift.py` — no *new* findings?
- [ ] The `docs/09-coding-standards.md` §8 self-check?
- [ ] Committed, on a branch, with a real message?
