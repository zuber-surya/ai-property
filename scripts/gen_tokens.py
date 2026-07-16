#!/usr/bin/env python3
"""Generate the frontend design tokens FROM docs/DESIGN.md.

DESIGN.md is the only file allowed to define a colour (OWNERSHIP.md §3). The
Tailwind config and the CSS custom properties are therefore *generated*, never
hand-typed — a hand-typed token file is a sixth fork of the design system, and
this project has already had five.

Emits, into every frontend app:
    src/styles/tokens.css   — CSS custom properties + semantic component classes
    tailwind.tokens.cjs     — the `theme.extend` block for tailwind.config

Usage:
    python scripts/gen_tokens.py            # write
    python scripts/gen_tokens.py --check    # exit 1 if the files are stale (CI)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESIGN = ROOT / "docs" / "DESIGN.md"
APPS = ["frontend"]  # one route-based app (ADR-0020)

BANNER = "GENERATED FROM docs/DESIGN.md — DO NOT EDIT. Run: python scripts/gen_tokens.py"


# --- parse the DESIGN.md YAML front matter --------------------------------
# Deliberately a tiny hand-rolled parser rather than a PyYAML dependency: the
# front matter is a fixed two-level shape we control, and the backend has no
# reason to grow a YAML dep for this.

def parse_front_matter(text: str) -> dict[str, dict[str, object]]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        sys.exit("DESIGN.md has no YAML front matter — cannot generate tokens.")

    out: dict[str, dict[str, object]] = {}
    section: str | None = None
    subkey: str | None = None

    for raw in m.group(1).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()

        if indent == 0 and line.endswith(":"):
            section = line[:-1]
            out[section] = {}
            subkey = None
            continue
        if section is None:
            continue

        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip().strip("'\"")

        if indent == 2:
            if val == "":            # a nested block, e.g. typography.display-lg
                subkey = key
                out[section][subkey] = {}
            else:
                subkey = None
                out[section][key] = val
        elif indent >= 4 and subkey:
            out[section][subkey][key] = val  # type: ignore[index]

    return out


# --- emit -----------------------------------------------------------------

def css_vars(design: dict) -> str:
    lines = [f"/* {BANNER} */", "", ":root {"]

    lines.append("  /* colour */")
    for name, hexv in design.get("colors", {}).items():
        lines.append(f"  --{name}: {hexv};")

    lines.append("")
    lines.append("  /* radius */")
    for name, val in design.get("rounded", {}).items():
        key = "DEFAULT" if name == "DEFAULT" else name
        lines.append(f"  --radius-{key.lower()}: {val};")

    lines.append("")
    lines.append("  /* spacing */")
    for name, val in design.get("spacing", {}).items():
        lines.append(f"  --space-{name}: {val};")

    lines.append("")
    lines.append("  /* elevation — on-surface at 4%, per DESIGN.md */")
    lines.append("  --shadow-soft: 0 10px 30px rgba(11, 28, 48, 0.04);")
    lines.append("  --glass-fill: rgba(255, 255, 255, 0.7);")
    lines.append("  --glass-blur: 20px;")
    lines.append("}")

    # Semantic classes, so a component never touches a raw token. This is what
    # keeps a hex out of a .tsx: there is always a named class to reach for.
    lines += [
        "",
        "/* ---------------------------------------------------------------",
        "   Semantic classes. A component should reach for THESE, never for a",
        "   raw token and never for a hex. If you need a colour that isn't",
        "   here, it belongs in DESIGN.md first.",
        "   --------------------------------------------------------------- */",
        "",
        ".chip {",
        "  display: inline-flex; align-items: center;",
        "  border-radius: var(--radius-full);",
        "  padding: 0.25rem 0.7rem;",
        "  font-size: 12px; font-weight: 600;",
        "  white-space: nowrap;",
        "}",
        "",
        "/* Colour modifiers. Apply ALONGSIDE the base `.chip` in markup:",
        "     <span class=\"chip chip-info\">Contacted</span>",
        "   NOTE: plain global CSS, so these set colour DIRECTLY — `composes:` is a",
        "   CSS-Modules-only feature and is silently inert here. Do not use it. */",
        ".chip-neutral { background: var(--neutral-container); color: var(--on-neutral-container); }",
        ".chip-info    { background: var(--info-container);    color: var(--on-info-container); }",
        ".chip-success { background: var(--success-container); color: var(--on-success-container); }",
        ".chip-warning { background: var(--warning-container); color: var(--on-warning-container); }",
        ".chip-error   { background: var(--error-container);   color: var(--on-error-container); }",
        ".chip-terminal{ background: var(--inverse-surface);   color: var(--inverse-on-surface); }",
        "",
        "/* Semantic aliases — self-contained (no composes). Apply with `.chip`.",
        "   Property status → DESIGN.md Canonical status mappings. */",
        ".chip-status-draft    { background: var(--neutral-container); color: var(--on-neutral-container); }",
        ".chip-status-pending  { background: var(--warning-container); color: var(--on-warning-container); }",
        ".chip-status-published{ background: var(--success-container); color: var(--on-success-container); }",
        ".chip-status-onhold   { background: var(--info-container);    color: var(--on-info-container); }",
        ".chip-status-rejected { background: var(--error-container);   color: var(--on-error-container); }",
        ".chip-status-sold     { background: var(--inverse-surface);   color: var(--inverse-on-surface); }",
        "",
        "/* Lead stage. The three in-progress stages SHARE info (ADR-0018) — the",
        "   text label distinguishes them. Do not invent three blues. */",
        ".chip-stage-new         { background: var(--neutral-container); color: var(--on-neutral-container); }",
        ".chip-stage-contacted   { background: var(--info-container);    color: var(--on-info-container); }",
        ".chip-stage-visit       { background: var(--info-container);    color: var(--on-info-container); }",
        ".chip-stage-negotiation { background: var(--info-container);    color: var(--on-info-container); }",
        ".chip-stage-won         { background: var(--success-container); color: var(--on-success-container); }",
        ".chip-stage-lost        { background: var(--neutral-container); color: var(--on-neutral-container); opacity: 0.7; }",
        "",
        "/* Lead source. tertiary marks AI-DERIVED sources ONLY (ADR-0007). */",
        ".chip-source-ai    { background: var(--tertiary-fixed); color: var(--tertiary); }",
        ".chip-source-human { background: var(--surface-container); color: var(--on-surface-variant); }",
        "",
        "/* The AI widget: model output, and nothing else. */",
        ".ai-widget {",
        "  border-radius: var(--radius-xl);",
        "  border: 1px solid transparent;",
        "  background:",
        "    linear-gradient(var(--surface-container-lowest), var(--surface-container-lowest)) padding-box,",
        "    linear-gradient(135deg, var(--primary), var(--tertiary)) border-box;",
        "}",
        "",
        "/* Focus is PRIMARY, never tertiary (ADR-0008). A focused field is a",
        "   user action, not a model output. */",
        ".focus-ring:focus-visible {",
        "  outline: none;",
        "  box-shadow: 0 0 0 2px var(--primary);",
        "}",
        "",
    ]
    return "\n".join(lines) + "\n"


def tailwind_tokens(design: dict) -> str:
    colors = design.get("colors", {})
    rounded = design.get("rounded", {})
    spacing = design.get("spacing", {})
    typo = design.get("typography", {})

    def block(d: dict, fmt=lambda k, v: f"      '{k}': '{v}',") -> str:
        return "\n".join(fmt(k, v) for k, v in d.items())

    font_sizes = []
    for name, spec in typo.items():
        if not isinstance(spec, dict):
            continue
        size = spec.get("fontSize", "16px")
        lh = spec.get("lineHeight", "1.5")
        ls = spec.get("letterSpacing")
        extra = f", letterSpacing: '{ls}'" if ls else ""
        w = spec.get("fontWeight", "400")
        font_sizes.append(
            f"      '{name}': ['{size}', {{ lineHeight: '{lh}', fontWeight: '{w}'{extra} }}],"
        )

    return f"""// {BANNER}
module.exports = {{
  colors: {{
{block(colors)}
  }},
  borderRadius: {{
{block(rounded)}
  }},
  spacing: {{
{block(spacing)}
  }},
  fontFamily: {{
    sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
  }},
  fontSize: {{
{chr(10).join(font_sizes)}
  }},
  boxShadow: {{
    soft: '0 10px 30px rgba(11, 28, 48, 0.04)',
  }},
}};
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="exit 1 if generated files are stale")
    args = ap.parse_args()

    design = parse_front_matter(DESIGN.read_text(encoding="utf-8"))
    css = css_vars(design)
    tw = tailwind_tokens(design)

    stale: list[str] = []
    for app in APPS:
        targets = {
            ROOT / app / "src" / "styles" / "tokens.css": css,
            ROOT / app / "tailwind.tokens.cjs": tw,
        }
        for path, content in targets.items():
            if args.check:
                if not path.exists() or path.read_text(encoding="utf-8") != content:
                    stale.append(path.relative_to(ROOT).as_posix())
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"  wrote {path.relative_to(ROOT).as_posix()}")

    if args.check:
        if stale:
            print("STALE — DESIGN.md changed and these were not regenerated:")
            for s in stale:
                print(f"  {s}")
            print("\nRun: python scripts/gen_tokens.py")
            return 1
        print("Tokens are current with DESIGN.md.")
        return 0

    n = len(design.get("colors", {}))
    print(f"\n{n} colours generated from docs/DESIGN.md. Do not hand-edit the output.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
