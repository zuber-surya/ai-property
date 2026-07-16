#!/usr/bin/env python3
"""Drift checks for the PropVista docs set.

Every check here exists because the corresponding failure actually happened.
See docs/OWNERSHIP.md §5 for the incident each one prevents.

Usage:
    python scripts/check_drift.py           # report
    python scripts/check_drift.py --quiet   # exit code only (for hooks/CI)

Exit codes:  0 = clean   1 = drift found
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# --- The one file allowed to define visual values --------------------------
DESIGN = DOCS / "DESIGN.md"

# Docs that deliberately inline a copy of the DESIGN.md tokens, because a
# single-paste Stitch prompt cannot reference another file.
#
# Sanctioned in OWNERSHIP.md §3.1 — but "sanctioned" is not "unwatched". Each of
# these is a place the tokens can drift from DESIGN.md, and the whole brass/indigo
# incident was a fork nobody was watching. Being on this list means the
# generated-prompts-stale check WILL compare you against DESIGN.md.
GENERATED_PROMPT_DOCS = [
    DOCS / "11-stitch-design-prompts.md",
    DOCS / "stitch-prompts.md",
]


@dataclass
class Finding:
    check: str
    path: Path
    line: int
    text: str
    why: str

    def render(self) -> str:
        rel = self.path.relative_to(ROOT).as_posix()
        return f"  {rel}:{self.line}\n      {self.text.strip()[:100]}\n      → {self.why}"


@dataclass
class Check:
    name: str
    incident: str
    findings: list[Finding] = field(default_factory=list)


# ---------------------------------------------------------------------------
# The meta layer: files whose JOB is to describe the system's failures.
#
# An incident log has to be allowed to name the incident. A decision record has
# to quote the values it decided between ("the prose said #4F46E5, the token
# said #3525cd") or it cannot explain itself. A runbook has to name the symptom
# it is telling you to watch for.
#
# Exempting these is not a loophole — it is the difference between a record and
# a violation. Keep the list SHORT and path-exact: a spec must never end up here.
# ---------------------------------------------------------------------------
META_PATHS = {
    "docs/OWNERSHIP.md",             # the registry
    "docs/GAPS.md",                  # the gap register
    "docs/adr/README.md",            # decision records — must quote what was rejected
    "docs/20-operations-runbook.md",  # names the symptoms to watch for
    "docs/22-risk-register.md",      # names the risks
    ".claude/rules/devos.md",        # the protocol
}


def is_meta(path: Path) -> bool:
    return path.relative_to(ROOT).as_posix() in META_PATHS


# Vendored / generated trees. Their contents are not ours and not our problem:
# a chalk README full of ANSI hex codes is not a design-system fork.
IGNORED_DIRS = {".git", "node_modules", ".venv", "dist", "__pycache__", ".pytest_cache"}


def _vendored(path: Path) -> bool:
    return bool(IGNORED_DIRS.intersection(path.parts))


def md_files() -> list[Path]:
    """Every markdown file we actually own, excluding the meta layer."""
    return sorted(
        p for p in ROOT.rglob("*.md") if not _vendored(p) and not is_meta(p)
    )


def lines_of(path: Path) -> list[tuple[int, str]]:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    return list(enumerate(content.splitlines(), start=1))


# ---------------------------------------------------------------------------
# CHECK 1 — the dead design system must never come back
# Incident: 13-ui-ux-flows.md §4 defined brass/teal/Fraunces; 33 specs cited it.
# ---------------------------------------------------------------------------

DEAD_TOKENS = re.compile(
    r"\b(color-brass|color-teal|color-coral|color-ink|color-paper|color-slate"
    r"|color-amber|brass-hover|Fraunces|Newsreader|IBM Plex|General Sans"
    r"|#C17F3C|#1F6F63|#C0392B|#12253B|#F3F5F6|#D9A441|#5B6472)\b",
    re.IGNORECASE,
)

# A live DESIGN.md token name. Its presence on a line that also names a dead
# token means the line is a migration mapping (old -> new), not a live citation.
LIVE_TOKEN = re.compile(
    r"\b(primary|secondary|tertiary|success-container|warning-container"
    r"|error-container|neutral-container|inverse-surface|surface-container"
    r"|on-surface|outline-variant|headline-md|Plus Jakarta Sans)\b"
)

# Lines that legitimately NAME the dead system in order to bury it.
GRAVESTONE = re.compile(
    r"deleted|superseded|dead|no longer|removed|was:|old \(|migration|do not use"
    r"|used to|replaced|moot|\bWAS\b|~~",
    re.IGNORECASE,
)


def check_dead_design_system() -> Check:
    c = Check(
        "dead-design-system",
        "13-ui-ux-flows.md §4 defined a second design system (brass/teal). "
        "33 specs cited it instead of DESIGN.md.",
    )
    live = design_hexes()
    for path in md_files():
        for n, line in lines_of(path):
            if not DEAD_TOKENS.search(line):
                continue
            if GRAVESTONE.search(line):
                continue
            # A migration row maps old -> new on one line, so it necessarily names
            # a dead token AND its live replacement. Naming the replacement on the
            # same line IS the gravestone — that's what makes the row useful.
            if any(h.lower() in live for h in HEX.findall(line)):
                continue
            if LIVE_TOKEN.search(line):
                continue
            c.findings.append(
                Finding(
                    c.name,
                    path,
                    n,
                    line,
                    "Dead design token. The system is DESIGN.md. If you are "
                    "citing the old one to bury it, say so on the same line.",
                )
            )
    return c


# ---------------------------------------------------------------------------
# CHECK 2 — no forked hex colors
# Incident: DESIGN.md's prose and its own YAML disagreed on primary/canvas/text.
# ---------------------------------------------------------------------------

HEX = re.compile(r"#[0-9a-fA-F]{6}\b")

# Files allowed to carry hex values, and why.
HEX_ALLOWED = {
    "docs/DESIGN.md",  # the owner
    "docs/11-stitch-design-prompts.md",  # sanctioned generated artifact (OWNERSHIP §3.1)
    "docs/stitch-prompts.md",  # sanctioned generated artifact — watched, see below
    "docs/stitch_design/design.md",  # a VERBATIM copy fed to Stitch — watched by design_copy check
    "docs/13-ui-ux-flows.md",  # the migration table burying the old system
    "docs/GAPS.md",
    "docs/OWNERSHIP.md",
}

# A verbatim copy of DESIGN.md, handed to Stitch alongside the generated screens.
# Because it is MEANT to be a copy, the check is the strongest one available:
# byte-identity. Any divergence at all means it is stale.
DESIGN_COPY = DOCS / "stitch_design" / "design.md"


def design_hexes() -> set[str]:
    return {h.lower() for h in HEX.findall(DESIGN.read_text(encoding="utf-8"))}


def check_forked_hex() -> Check:
    c = Check(
        "forked-hex",
        "A hex color outside DESIGN.md is a fork waiting to drift. "
        "This is how brass and indigo coexisted.",
    )
    known = design_hexes()
    for path in md_files():
        rel = path.relative_to(ROOT).as_posix()
        if rel in HEX_ALLOWED:
            continue
        for n, line in lines_of(path):
            for hx in HEX.findall(line):
                c.findings.append(
                    Finding(
                        c.name,
                        path,
                        n,
                        line,
                        f"{hx} — hex colors live only in DESIGN.md. Cite the token name."
                        + ("" if hx.lower() in known else "  (and this hex is NOT in DESIGN.md at all)"),
                    )
                )
    return c


# ---------------------------------------------------------------------------
# CHECK 3 — the generated Stitch prompts must not diverge from DESIGN.md
# Incident: this is the exception that caused the original mess. Watch it.
# ---------------------------------------------------------------------------


def check_generated_prompts_current() -> Check:
    c = Check(
        "generated-prompts-stale",
        "The Stitch prompt docs inline a copy of the DESIGN.md tokens. If "
        "DESIGN.md changes and they don't, we are back where we started.",
    )
    design = design_hexes()
    for doc in GENERATED_PROMPT_DOCS:
        if not doc.exists():
            continue
        prompt_hexes = {h.lower() for h in HEX.findall(doc.read_text(encoding="utf-8"))}
        orphans = sorted(prompt_hexes - design)
        if orphans:
            c.findings.append(
                Finding(
                    c.name,
                    doc,
                    0,
                    ", ".join(orphans),
                    "These hexes appear in this Stitch prompt doc but NOT in DESIGN.md. "
                    "Either DESIGN.md moved and this doc is stale (regenerate it), "
                    "or someone hand-edited a token here (don't).",
                )
            )
    return c


# ---------------------------------------------------------------------------
# CHECK 4 — no mono/serif claims
# Incident: the type stack was Fraunces + Inter + IBM Plex Mono. It is now
# Plus Jakarta Sans only, and prices kept coming back as monospace.
# ---------------------------------------------------------------------------

MONO_CLAIM = re.compile(r"\b(mono font|monospace|data font|serif heading)\b", re.IGNORECASE)
MONO_NEGATED = re.compile(r"\bno\b.{0,30}\b(mono|serif)|never|not a different typeface|deleted", re.IGNORECASE)


def check_mono_serif() -> Check:
    c = Check(
        "mono-serif",
        "The system is Plus Jakarta Sans only. Prices are headline-md, not mono.",
    )
    for path in md_files():
        for n, line in lines_of(path):
            if MONO_CLAIM.search(line) and not MONO_NEGATED.search(line):
                c.findings.append(
                    Finding(c.name, path, n, line, "No monospace or serif face exists in this system.")
                )
    return c


# ---------------------------------------------------------------------------
# CHECK 5 — closed gaps must not still be cited as blocking
# Incident: schema v1.1 closed G1/G2/leads.user_id/favorites-uniqueness.
# Three portal specs STILL call them blocking open gaps.
# ---------------------------------------------------------------------------

# Only gaps that are FULLY closed. G6 is deliberately absent: its column exists
# but its endpoint does not, so citing it as open is still correct (see G8).
# A half-closed gap in this list would train people to ignore the check.
#
# --- EXTENDED 2026-07-16. It knew about exactly two gaps and reported 0 while
# G7, D1, P1, P2 and P3 were all closed and still cited as open across eight
# files — including GAPS.md itself, which was wrong about THREE OF ITS OWN ROWS.
#
# That is the inverse of the §5A failure: §5A was a false claim spreading
# outward from a stale summary; this was a true fix that never propagated back
# INTO the register. The register being wrong is worse than a spec being wrong,
# because the register is the thing every spec is told to trust.
#
# The rule this produced: when you close a gap, add it here in the same commit.
# The check then finds the citations for you — the findings ARE the sweep list.
CLOSED_GAPS = {
    "G1": "notifications table — added in schema v1.1 §3.20",
    "G2": "notification preferences — added in schema v1.1 §3.21",
    "G7": "agent-reply path for escalated chats — closed 2026-07-14, 04-api-spec.md §12A",
    "D1": "the `info` status colour — closed 2026-07-14, DESIGN.md + ADR-0018",
    "P1": "lead auto-assignment — DECIDED 2026-07-13: manual claim, 01-prd.md FR10.2",
    "P2": "01-prd.md FR10.1 — already corrected; stages are a fixed set",
    "P3": "04-api-spec.md §14 — already corrected; reports are stateless",
}
# --- REBUILT 2026-07-16, the moment CLOSED_GAPS grew past G1/G2 -------------
#
# The old pattern matched the bare words `gap` and `open`. That is TAUTOLOGICAL:
# a line citing a gap ID says "gap" almost by definition — "*(closes gap G7)*"
# was flagged as claiming G7 was open. It survived only because CLOSED_GAPS held
# two IDs that happened never to appear in prose. Adding five real IDs surfaced
# 9 findings and ALL 9 WERE FALSE — including the section that closes G7 and the
# DESIGN.md paragraph that closes D1.
#
# Shipping that would have been worse than no check: 9 false positives teaches
# everyone to skim past the one true finding (devos §4 — "a false positive that
# gets ignored trains everyone to ignore the true ones too").
#
# So it now matches a PRESENT-TENSE CLAIM OF BLOCKAGE, not the vocabulary of
# gaps. "still open" blocks; "sat open for three days" is history. "does not
# exist" blocks; "closes gap G7" is a closure.
BLOCKING_WORD = re.compile(
    r"\bis\s+(?:still\s+)?blocking\b|\bstill\s+blocking\b|\bblocks\b"
    r"|\bblocked\s+by\b|\bis\s+blocked\b|\bremains?\s+blocked\b"
    r"|\bstill\s+(?:an?\s+)?(?:open|missing|absent|blocking)\b"
    r"|\bstill\s+(?:calls?|lists?|promises?)\s+(?:it\s+)?(?:open|blocking)\b"
    r"|\bopen\s+gap\b|\bblocking\s+(?:schema\s+)?gap\b"
    r"|\bdoes\s+not\s+exist\b|\bdoesn['’]t\s+exist\b|\bdon['’]t\s+exist\b"
    r"|\bnot\s+currently\s+possible\b|\bnowhere\s+to\s+be\s+stored\b"
    r"|\bno\s+\w{0,20}\s?table\b"
    r"|\bunbuildable\b|\bcannot\s+be\s+built\b|\bhas\s+no\s+data\s+source\b",
    re.IGNORECASE,
)

# A line that names a closed gap in order to RECORD its closure, or to tell the
# story of when it was open, is a gravestone. Same principle as the
# dead-design-system and false-gap burial gates.
CLOSED_MARKER = re.compile(
    r"clos(?:ed|es|ing|ure)|✅|~~|resolved|added\s+in|fixed|swept|no\s+longer"
    r"|until\s+\d{4}-\d{2}-\d{2}|\bwas\s+never\b|\bnever\s+was\b|\bdecided\b"
    r"|\bcorrected\b|\bnow\s+(?:exists?|reads?)\b|\bhistor(?:y|ical)\b",
    re.IGNORECASE,
)

# Every fixture below is a VERBATIM line from the repo. The MUST_NOT_CATCH half
# is the 9 false positives this check produced the first time it was extended —
# locked shut so the next person to add a gap ID finds out immediately.
STALE_GAP_MUST_CATCH = [
    "| G1 | `GET /portal/notifications` was specified with nothing to back it. The notifications table does not exist. |",
    "This is a blocking schema gap: `leads` has no `user_id` (G1).",
    "D1 is still open — three of the five pipeline stages have no honest colour.",
    "FR10.2b is unbuildable: G9a means nothing fires on a timer.",
    "G2 — notification preferences have nowhere to be stored.",
]

STALE_GAP_MUST_NOT_CATCH = [
    "## 12A. Admin — Live Chat Handoff *(closes gap G7)*",
    "## 10A. The Handoff State Machine *(closes gap G7)*",
    "| **Status chips** | `New` and `Contacted` must be **visibly different colours** — neutral vs. info. If they look the same, the `info` token didn't land (gap D1). |",
    "> **SCREEN 10 (Agent Chat Console) is new.** It closes gap G7 — until 2026-07-14 the bot could escalate and no human could reply.",
    "Then the ramp shipped without an in-progress color, and **three of the five lead stages had to render `neutral`** — a placeholder, not an answer. `info` closes that (gap **D1**).",
    "| `/admin/chat` | **Live agent chat console** (handoff from chatbot) | `22-agent-chat-console.md` | agent, admin | MVP (Gap G7) |",
    "Until now it didn't exist, and neither did the endpoints. `POST /ai/chat/escalate` handed a conversation to a human who had no way to answer.",
    "> This checkbox sat open for three days *after* §14 answered it, and `GAPS.md` P3 cited that contradiction as evidence §14 was stale — when §14 was correct and this line was the residue.",
    "| **P2** | *\"`01-prd.md` FR10.1 is stale.\"* | **Closed — FR10.1 was corrected and this row was never swept.** |",
]


def _stale_gap_hit(line: str, gap_ref: re.Pattern) -> str | None:
    """Return the gap ID this line falsely calls blocking, or None."""
    m = gap_ref.search(line)
    if not m:
        return None
    if CLOSED_MARKER.search(line):
        return None  # naming the gap to record its closure, or its history
    return m.group(1) if BLOCKING_WORD.search(line) else None


def selftest_stale_gaps() -> list[str]:
    """Verify the stale-gap check against the false positives it once produced."""
    gap_ref = re.compile(r"\b(" + "|".join(list(CLOSED_GAPS) + ["G9a"]) + r")\b")
    failures = []
    for line in STALE_GAP_MUST_CATCH:
        if not _stale_gap_hit(line, gap_ref):
            failures.append(f"MISSED (should flag): {line[:95]}")
    for line in STALE_GAP_MUST_NOT_CATCH:
        if _stale_gap_hit(line, gap_ref):
            failures.append(f"FALSE POSITIVE (should pass): {line[:95]}")
    return failures


def check_stale_gap_citations() -> Check:
    c = Check(
        "stale-gap",
        "A gap was closed in its owning doc but the specs that cite it were "
        "never swept. Someone reads the spec and reports a blocker that is gone.",
    )
    gap_ref = re.compile(r"\b(" + "|".join(CLOSED_GAPS) + r")\b")
    for path in md_files():
        for n, line in lines_of(path):
            # One helper, shared with selftest_stale_gaps() — so the fixtures
            # test the code that actually runs, not a paraphrase of it.
            gid = _stale_gap_hit(line, gap_ref)
            if gid:
                c.findings.append(
                    Finding(
                        c.name,
                        path,
                        n,
                        line,
                        f"{gid} is CLOSED ({CLOSED_GAPS[gid]}). See docs/GAPS.md §5. "
                        "Update this citation or drop it.",
                    )
                )
    return c


# ---------------------------------------------------------------------------
# CHECK 6 — sync DB driver in an async-mandatory architecture
# Incident: SPRINT0_PLAN.md pins psycopg2-binary. CLAUDE.md requires async.
# ---------------------------------------------------------------------------

SYNC_DRIVER = re.compile(r"\bpsycopg2(-binary)?\b", re.IGNORECASE)
FAKE_PKG = re.compile(r"@vitejs/plugin-tsx", re.IGNORECASE)

# A line that names the banned thing in order to ban it is a gravestone, not a
# violation — "asyncpg, NOT psycopg2" must not trip the psycopg2 check. Same
# principle as the dead-design-system gravestones above: a warning is the
# opposite of a usage, and a check that can't tell them apart teaches people to
# stop writing warnings.
BANNED_NEGATED = re.compile(
    r"\bnot\b|\bnever\b|instead|does not exist|is not a real|blocks the event loop"
    r"|synchronous|⚠|deprecated|do not use|banned|forbidden",
    re.IGNORECASE,
)


def check_async_violation() -> Check:
    c = Check(
        "async-violation",
        "CLAUDE.md: every I/O endpoint is async. SQLAlchemy's async engine "
        "needs asyncpg; psycopg2 is sync-only and blocks the event loop.",
    )
    targets = (
        list(md_files())
        + [p for p in ROOT.rglob("requirements*.txt") if not _vendored(p)]
        + [p for p in ROOT.rglob("package.json") if not _vendored(p)]
    )
    for path in targets:
        if is_meta(path):
            continue
        for n, line in lines_of(path):
            if BANNED_NEGATED.search(line):
                continue  # the line is warning against it, not using it
            if SYNC_DRIVER.search(line):
                c.findings.append(
                    Finding(c.name, path, n, line, "Use asyncpg. psycopg2 is synchronous.")
                )
            if FAKE_PKG.search(line):
                c.findings.append(
                    Finding(
                        c.name,
                        path,
                        n,
                        line,
                        "@vitejs/plugin-tsx does not exist. @vitejs/plugin-react handles TSX.",
                    )
                )
    return c


# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# CHECK — false gaps
# Incident: CLAUDE.md summarised "no job scheduler" and "no email/SMS provider"
# a day AFTER 02-architecture.md §4.4/§3 decided both (pg_cron + jobs worker;
# SendGrid + Twilio). A spec-set README copied the summary; an agent copied the
# README; the claim spread to eight documents and a MANDATORY requirement
# (FR10.2b) was planned as unbuildable for a sprint.
#
# Nobody lied. Every step was a faithful copy of the one above it. That is what
# makes summary-drift dangerous: it doesn't look like an error, it looks like
# agreement. So the resurrection of these specific claims is now a hard failure.
# ---------------------------------------------------------------------------

# --- REBUILT 2026-07-16. It was reporting 0 with EIGHT live resurrections. ---
#
# Including one in 00-project-overview.md — the doc CLAUDE.md says to read
# first — sitting in the table row directly BELOW a correctly-buried G9a. One
# was swept, the other was not, and the gate said nothing. Two bugs:
#
#   1. It reused GRAVESTONE as its burial marker. GRAVESTONE matches \bWAS\b
#      case-insensitively, and 108 lines across 35 files contain "was". Any
#      line with the commonest verb in English bought an exemption. So did an
#      unrelated "dead toggles" (via |dead|). This check was not weak — it was
#      close to a no-op that printed "ok".
#
#   2. Its patterns encoded the ORIGINAL phrasing ("no email/SMS provider").
#      But drift does not reproduce phrasing — it paraphrases. "no provider
#      chosen", "a provider that hasn't been chosen", "not yet chosen", "Not
#      chosen anywhere" and "depends on chosen provider (not yet selected)"
#      all sailed straight through a check written to catch exactly this claim.
#
# So it now tests the CLAIM, not the phrasing: a SUBJECT (the email/SMS
# delivery provider) + a NEGATED CHOICE, anywhere on the line. The subject gate
# is what keeps it honest — a maps provider, a DNS provider, an identity
# provider, an error tracker and a PDF library are different decisions with
# different owners, and several are legitimately still open. Flagging those
# would teach everyone to ignore this check (devos §4).
#
# `--selftest` locks both bugs shut: every phrasing that escaped is a fixture.

# Burying a false gap means SAYING it is false. The old check accepted any line
# containing "was" — that is not a retraction, that is the English language.
FALSE_GAP_BURIED = re.compile(
    r"~~|✅|\bfalse\b|\bnever\s+(?:existed|was|were|real|a\s+gap|true)\b"
    r"|\bretracted\b|\bstale\s+summary\b|\bresurrection\b|§5A",
    re.IGNORECASE,
)

# The email/SMS DELIVERY provider — and nothing else that calls itself one.
DELIVERY_SUBJECT = re.compile(r"\b(?:e-?mail|sms|transactional|sendgrid|twilio)\b", re.I)

# "no provider", "no email/SMS provider", "not chosen", "not yet selected",
# "hasn't been chosen". A choice, negated.
NEGATED_CHOICE = re.compile(
    r"\bno\s+(?:\w+[-/\s]){0,3}provider\b"
    r"|\b(?:not|never)\s+(?:yet\s+)?(?:been\s+)?(?:chosen|selected|configured|decided|picked)\b"
    r"|\b(?:has|have|is|are|was|were|do|does)n['’]t\s+(?:yet\s+)?(?:been\s+)?"
    r"(?:chosen|selected|configured|decided|picked)\b"
    r"|\bunchosen\b|\bstill\s+(?:un)?decided\b",
    re.IGNORECASE,
)

SCHEDULER_ABSENT = re.compile(
    r"\bno\s+(?:job\s+|task\s+|cron\s+)?scheduler\b"
    r"|\bscheduler\b[^.;|]{0,40}?(?:does\s+not|doesn['’]t|never)\s+exist"
    r"|\bBackgroundTasks\b[^.;|]{0,30}?(?:cannot|can['’]t|is\s+unable)"
    r"|\bcannot\s+fire\s+on\s+a\s+timer\b"
    r"|\bnothing\s+(?:fires|runs)\s+on\s+a\s+(?:schedule|timer)\b",
    re.IGNORECASE,
)

# --- ADDED 2026-07-16 -------------------------------------------------------
# The claim above has a TWIN the check never saw: not "there is no scheduler",
# but "the scheduler is BackgroundTasks/Celery/SQS" — the mechanism that §4.4
# REPLACED, still being presented as the plan.
#
# It sat live in TWO docs for three days while false-gap reported 0:
#   10-deployment-devops.md §1  "BackgroundTasks initially → AWS SQS + a worker
#                                ... if promoted to Celery/RQ (per §4.3)"
#   12-srs.md NFR-SCALE-3       "promotable from BackgroundTasks to Celery/RQ"
#
# Both cite "§4.3" — a section that no longer holds background work at all. The
# decision moved to §4.4 and its dependents were never swept. This is the same
# incident as G9a wearing different words, which is precisely why phrasing-based
# checks fail: drift paraphrases. So test the CLAIM — "the job mechanism is one
# of the superseded ones" — not the sentence it arrived in.
STALE_JOB_MECHANISM = re.compile(r"\b(?:BackgroundTasks|Celery|RQ|SQS)\b")

# Naming the dead mechanism in order to bury it is the OPPOSITE of proposing it.
# "No Celery, no Redis" is the decision being stated; "Replaces the earlier
# BackgroundTasks note" is the history being recorded. Both must keep passing —
# a check that punishes the warning teaches people to delete the warning.
JOB_MECHANISM_BURIED = re.compile(
    r"\bno\s+(?:Celery|Redis|SQS|RQ)\b"
    r"|\bnot\s+viable\b|\breplaces?\b|\bsupersed\w+|\bearlier\b|\binstead\s+of\b"
    r"|\bnever\b|\bdeprecated\b|\bdo\s+not\s+use\b|\bwas\s+not\b|\bused\s+to\b"
    r"|~~|✅|§5A",
    re.IGNORECASE,
)

WHY_JOB_MECHANISM = (
    "The job mechanism is pg_cron + a Python worker polling the `jobs` table "
    "(02-architecture.md §4.4, decided 2026-07-13). No Celery, no Redis, no SQS. "
    "BackgroundTasks was REPLACED — a lost BackgroundTask is a published property "
    "that silently never enters the search index. If you are burying the old "
    "mechanism, say so on the same line. See GAPS.md §5A."
)

WHY_SCHEDULER = (
    "There IS a scheduler: 02-architecture.md §4.4 — pg_cron + a jobs worker, "
    "decided 2026-07-13. mark_stale_leads() is listed in it BY NAME. See GAPS.md §5A."
)
WHY_PROVIDER = (
    "The providers ARE chosen: 02-architecture.md §3 / 03-database-schema.md §3.21 — "
    "SendGrid (email), Twilio (SMS), decided 2026-07-13. See GAPS.md §5A."
)


def _false_gap_hits(line: str) -> list[str]:
    """Return the reasons this line resurrects a false gap. Empty means clean."""
    # The stale-mechanism claim has its OWN burial vocabulary ("no Celery",
    # "replaces the earlier ... note"), so it is tested before the generic
    # retraction gate — those lines are records, not resurrections.
    mechanism_hits = []
    if STALE_JOB_MECHANISM.search(line) and not JOB_MECHANISM_BURIED.search(line):
        mechanism_hits.append(WHY_JOB_MECHANISM)

    if FALSE_GAP_BURIED.search(line):
        return mechanism_hits  # the line names the claim in order to retract it

    hits = list(mechanism_hits)
    if SCHEDULER_ABSENT.search(line):
        hits.append(WHY_SCHEDULER)
    # The claim is "the email/SMS delivery provider is undecided" — it needs all
    # three parts. Any one alone is an ordinary sentence about an ordinary thing.
    if DELIVERY_SUBJECT.search(line) and "provider" in line.lower() and NEGATED_CHOICE.search(line):
        hits.append(WHY_PROVIDER)
    return hits


def check_false_gaps() -> Check:
    c = Check(
        "false-gap",
        "A gap that was never real, resurrected from a stale summary. This one "
        "cost a sprint plan.",
    )
    for path in md_files():
        for n, line in lines_of(path):
            for why in _false_gap_hits(line):
                c.findings.append(Finding(c.name, path, n, line, why))
    return c


# Every MUST-CATCH line below is a VERBATIM line that escaped the old check and
# sat live in the docs. Every MUST-NOT-CATCH line is a verbatim line that must
# keep passing: a different provider decision, or an honest retraction. Both
# halves matter. A check that misses the claim is useless; a check that flags
# the maps provider gets switched off, and then it is worse than useless.
FALSE_GAP_MUST_CATCH = [
    "| **No email/SMS provider chosen.** In-app notifications now work; email and SMS remain dead toggles. Recommend shipping **in-app only** for MVP rather than switches that do nothing. | `10-deployment-devops.md` | FR7.2, FR15.2 |",
    "| A12 | **No email/SMS provider chosen.** In-app notifications now work; email/SMS remain dead toggles. | [`19`](19-notification-rules.md) | `10-deployment-devops.md` |",
    "| Channel | Email / SMS / In-app. **Email and SMS need a provider that hasn't been chosen** |",
    "| Preferences grid | Event type × channel (FR7.2). **Email/SMS require a delivery provider that is not yet chosen** — see §11 |",
    "- **Email deliverability:** a real transactional provider (SES, etc.) is required. Not chosen anywhere in `10-deployment-devops.md`.",
    "- [ ] Whether the optional SMS/email confirmation (FR6.3) ships at MVP. It requires a transactional email/SMS provider, which is not chosen in `10-deployment-devops.md`.",
    "- SMS/email confirmation (FR6.3) depends on chosen provider (not yet selected).",
    "- [ ] **No email/SMS provider is chosen** in `10-deployment-devops.md`. Without one, \"email/SMS\" in FR7.2 is aspirational and only the in-app channel can ship, rather than shipping dead toggles.",
    "No job scheduler exists, so FR10.2b cannot be built.",
    "BackgroundTasks cannot fire on a timer.",
    # --- ADDED 2026-07-16. Both VERBATIM, both live for three days while this
    # check reported 0. The G9a claim, wearing the mechanism instead of denying
    # the scheduler — and both citing a §4.3 that no longer holds background work.
    "| Background jobs | FastAPI `BackgroundTasks` initially → AWS SQS + a worker (ECS task or Lambda) if promoted to Celery/RQ (per `02-architecture.md` Section 4.3) | |",
    "| `NFR-SCALE-3` | Background job processing (embedding generation, notifications) must be promotable from FastAPI `BackgroundTasks` to a queue-based worker (Celery/RQ) without changing the public API contract, per the upgrade path already noted in `02-architecture.md` Section 4.3. |",
]

FALSE_GAP_MUST_NOT_CATCH = [
    # Different provider decisions. Some are genuinely open — that is not this check's business.
    "- Map provider not chosen (cost/API‑key implications).",
    '**"Nearby landmarks" (FR5.1) has no data source.** No column, no endpoint, and no maps-provider integration is specified.',
    "| **No error tracking** chosen (Sentry suggested, unconfirmed) | You find out from a user |",
    "**PDF generation** needs a library and, for charts, a rendering step. Not chosen in `10-deployment-devops.md`.",
    "**Supabase Auth as-is** as the identity provider for all users — no second auth system.",
    # Real statements about the providers that WERE chosen.
    "a bulk import produces batched notifications, not 200 per recipient; a provider outage does not prevent lead capture.",
    "| `jobs` queue → SendGrid / Twilio | Dispatch runs in the jobs worker, never inline — a provider outage must not fail lead creation |",
    # Honest retractions. These name the claim in order to kill it.
    '| ~~**G9b**~~ | *"No email/SMS provider chosen."* | **False.** `02-architecture.md` §3 names SendGrid + Twilio. |',
    "| ~~No job scheduler~~ ✅ **RESOLVED — and it never was a gap.** `02-architecture.md` §4.4 specifies pg_cron. |",
    '`CLAUDE.md` carried a stale summary — *"no job scheduler, no email/SMS provider"* — long after `02-architecture.md` decided both.',
    'a `false-gap` check that fails on any resurrection of "no scheduler" or "no email/SMS provider".',
    # --- ADDED 2026-07-16. The mechanism check must not punish the docs that
    # BURY the old mechanism. These are verbatim and every one must keep passing:
    # a check that flags the gravestone gets the gravestone deleted.
    "| Async Jobs | **Python worker polling a `jobs` table** | Embedding generation, de-indexing, bulk CSV import, notification dispatch. **No Celery, no Redis** |",
    "Background work runs as **pg_cron (SQL-only time jobs) + a Python worker polling this table** (decided 2026-07-13). No Celery, no Redis. See `02-architecture.md` §4.4.",
    '*Decided 2026-07-13. Replaces the earlier "FastAPI BackgroundTasks, promote to Celery later" note, which was not viable: a lost `BackgroundTask` means a published property that silently never enters the search index.*',
    "- [x] ~~Whether background jobs start with FastAPI `BackgroundTasks` or Celery/RQ.~~ **DECIDED 2026-07-13 — see §4.4: `pg_cron` + a Python jobs worker.**",
    "| 6 | **pg_cron (SQL jobs) + a Python worker polling `jobs`** | No Celery, no Redis. Retry/backoff/dead-lettering are hand-rolled (§3.26, §7) |",
]


def selftest_false_gaps() -> list[str]:
    """Verify the false-gap check against the phrasings that already beat it once."""
    failures = []
    for line in FALSE_GAP_MUST_CATCH:
        if not _false_gap_hits(line):
            failures.append(f"MISSED (should flag): {line[:95]}")
    for line in FALSE_GAP_MUST_NOT_CATCH:
        if _false_gap_hits(line):
            failures.append(f"FALSE POSITIVE (should pass): {line[:95]}")
    return failures


# ---------------------------------------------------------------------------
# CHECK — a hex literal in frontend source
#
# The Stitch HTML carries ~55 hardcoded hexes per screen (≈550 across the admin
# portal). It looks right, so the temptation to paste it is enormous. One pasted
# line and DESIGN.md stops being the source of truth.
#
# gen_tokens.py generates the token files FROM DESIGN.md; this check makes sure
# nobody routes around them. The generated files are the only exception, and
# they carry a banner saying so.
# ---------------------------------------------------------------------------

FRONTEND_APPS = ["frontend"]  # one route-based app (ADR-0020)
GENERATED_MARK = "GENERATED FROM docs/DESIGN.md"
SRC_SUFFIXES = {".tsx", ".ts", ".jsx", ".js", ".css", ".scss"}


def check_forked_hex_frontend() -> Check:
    c = Check(
        "forked-hex-frontend",
        "A hex literal in frontend source. DESIGN.md is the only file that "
        "defines a colour; the token files are generated from it. Pasting Stitch "
        "HTML forks the design system ~550 ways.",
    )
    for app in FRONTEND_APPS:
        src = ROOT / app / "src"
        if not src.exists():
            continue
        for path in src.rglob("*"):
            if path.suffix not in SRC_SUFFIXES or _vendored(path):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if GENERATED_MARK in text:
                continue  # generated from DESIGN.md — that's the whole point
            for n, line in enumerate(text.splitlines(), start=1):
                for hx in HEX.findall(line):
                    c.findings.append(
                        Finding(
                            c.name,
                            path,
                            n,
                            line,
                            f"{hx} — use a token class (bg-primary, .chip-status-published). "
                            "If the colour isn't in DESIGN.md, it goes there FIRST.",
                        )
                    )
    return c


def check_design_copy_identical() -> Check:
    """docs/stitch_design/design.md must be byte-identical to DESIGN.md."""
    c = Check(
        "design-copy-stale",
        "stitch_design/design.md is a verbatim copy of DESIGN.md, handed to "
        "Stitch. A copy that has diverged is a second design system wearing a "
        "familiar name — which is exactly how this project got two of them.",
    )
    if not DESIGN_COPY.exists():
        return c
    if DESIGN_COPY.read_bytes() != DESIGN.read_bytes():
        c.findings.append(
            Finding(
                c.name,
                DESIGN_COPY,
                0,
                "diverged from docs/DESIGN.md",
                "This file must be a VERBATIM copy. Regenerate it:\n"
                "        cp docs/DESIGN.md docs/stitch_design/design.md\n"
                "      Never hand-edit it. If the design changed, change DESIGN.md "
                "and re-copy — and regenerate the Stitch screens, because they were "
                "built from the old one.",
            )
        )
    return c


CHECKS = [
    check_dead_design_system,
    check_forked_hex,
    check_forked_hex_frontend,
    check_generated_prompts_current,
    check_design_copy_identical,
    check_mono_serif,
    check_stale_gap_citations,
    check_false_gaps,
    check_async_violation,
]


BASELINE = ROOT / ".drift-baseline.json"


def load_baseline() -> dict[str, int]:
    if not BASELINE.exists():
        return {}
    try:
        return json.loads(BASELINE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def main() -> int:
    # Windows consoles default to cp1252 and choke on the arrows/box-drawing
    # that live throughout these docs. Force UTF-8 rather than degrade the report.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quiet", action="store_true", help="exit code only")
    ap.add_argument(
        "--accept",
        action="store_true",
        help="record current counts as the accepted baseline (only ever to LOWER it)",
    )
    ap.add_argument(
        "--selftest",
        action="store_true",
        help="run the checks against their own fixtures and exit (also runs on every report)",
    )
    args = ap.parse_args()

    # The false-gap check silently reported 0 for a sprint while eight
    # resurrections sat live in the docs. A gate nobody tests is a gate nobody
    # has. This runs on every invocation — it is microseconds, and the one thing
    # worse than no check is a check that reassures you while it fails.
    selftest_failures = selftest_false_gaps() + selftest_stale_gaps()
    if selftest_failures:
        print("\nSELFTEST FAILED — a check no longer catches what it must:")
        for f in selftest_failures:
            print(f"  {f}")
        print("\nFix the check. Do not delete the fixture. See GAPS.md §5A.\n")
        return 1
    if args.selftest:
        n = len(FALSE_GAP_MUST_CATCH) + len(FALSE_GAP_MUST_NOT_CATCH)
        n += len(STALE_GAP_MUST_CATCH) + len(STALE_GAP_MUST_NOT_CATCH)
        print(f"selftest ok — {n} false-gap + stale-gap fixtures pass")
        return 0

    results = [fn() for fn in CHECKS]
    counts = {r.name: len(r.findings) for r in results}
    total = sum(counts.values())
    base = load_baseline()

    if args.accept:
        BASELINE.write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")
        print(f"Baseline recorded: {total} known finding(s) in {BASELINE.name}")
        return 0

    # A check that always fails is a check everyone learns to skip. So we gate on
    # REGRESSION, not on absolute zero: known debt is recorded in docs/GAPS.md and
    # in the baseline; adding NEW drift is what fails a commit.
    regressions = {
        name: (counts[name], base.get(name, 0))
        for name in counts
        if counts[name] > base.get(name, 0)
    }

    if args.quiet:
        return 1 if regressions else 0

    print("\nPropVista drift check\n" + "=" * 60)
    for r in results:
        known = base.get(r.name, 0)
        now = len(r.findings)
        if now > known:
            mark, note = "FAIL", f"  <-- REGRESSION (was {known})"
        elif now:
            mark, note = "debt", f"  (known, tracked in docs/GAPS.md)"
        else:
            mark, note = "ok  ", ""
        print(f"\n[{mark}] {r.name}  ({now}){note}")
        if now > known:
            print(f"       why: {r.incident}")
            for f in r.findings[:20]:
                print(f.render())
            if now > 20:
                print(f"      … and {now - 20} more")

    print("\n" + "=" * 60)
    if regressions:
        print(f"NEW drift introduced in: {', '.join(regressions)}")
        print("Fix it, or if the finding is wrong, fix the check.")
        print("See docs/OWNERSHIP.md for who owns what.\n")
        return 1
    if total:
        print(f"No new drift. {total} known finding(s) tracked in docs/GAPS.md.\n")
    else:
        print("Clean. No forked truth.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
