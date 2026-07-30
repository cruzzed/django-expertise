#!/usr/bin/env python3
"""
router.py — Two-Phase Interactivity Pipeline router and validator.

Implements spec deliverable #3 (§6 pipeline, §8 quality gates):
routes interactivity tasks to htmx-writer first, validates Phase 1 output,
generates the handoff brief for spa-evolver, and validates the Phase 2
hyperscript translation.

Usage:
    django-expertise-router route "<task description>"
    django-expertise-router validate-phase1 <file.html>
    django-expertise-router validate-phase2 <file.html>
    django-expertise-router handoff <file.html>

Exit codes: 0 = gate pass / success, 1 = gate fail / usage error.
"""

import re
import sys
from pathlib import Path

from django_expertise.gates import (
    check_phase1_shape,
    check_phase2_shape,
    HYPERSCRIPT_TODO_RE,
)

# --- Router rules -------------------------------------------------------------
# Evaluated in order; first match wins. See pipeline.md §1.

_RULES = [
    (
        "spa-evolver",
        re.compile(r"\b(hyperscript|_hyperscript|translated-by|phase\s*2\b|"
                   r"translate\s+(to|into)\s+hyperscript|hyperscript-todo)\b", re.I),
        "Phase 2 translation request — only valid on Gate-P1-passed artifacts.",
    ),
    (
        "htmx-writer",
        re.compile(r"\b(htmx|hx-on|hx-get|hx-post|hx-put|hx-delete|hx-patch|hx-boost|"
                   r"hx-swap|hx-trigger|interactiv|live[- ]?search|inline[- ]?edit|"
                   r"modal|toast|drag[- ]?and[- ]?drop|drag|drop|sortable|infinite[- ]?scroll|"
                   r"debounce|toggle|without (a )?(page )?reload|spa-like|spa\b|"
                   r"client[- ]?side|dynamic (ui|page|interface)|ajax|autosave|"
                   r"keyboard shortcut|command palette|accordion|dropdown|"
                   r"react|vue|angular)\b", re.I),
        "All client-side interactivity starts in Phase 1 (vanilla JS via hx-on:*). "
        "React/Vue/Angular requests are redirected here per success criteria.",
    ),
    (
        "django-rtfm-dev",
        re.compile(r"\b(built-?in|batteries|django\.contrib|which (package|library)|"
                   r"third[- ]?party|package|library|plugin|auth(entication)?\b|"
                   r"admin\b|modeladmin|form(s)?\b|pagination|paginator|cach(e|ing)\b|"
                   r"email|rss|atom|feed(s)?\b|sitemap|syndication|signal(s)?\b|jwt|"
                   r"oauth|crud\b|should i (use|install))\b", re.I),
        "Check the batteries first: verify django.contrib before any third-party package.",
    ),
    (
        "mvt-analyst",
        re.compile(r"\b(mvt|mvc|architecture|layer|model(s)?\b|view(s)?\b|template(s)?\b|"
                   r"cbv|fbv|class-based|function-based|queryset|n\+1|prefetch|"
                   r"select_related|prefetch_related|manager\b|orm\b|url(s)?\b|"
                   r"where (should|does)|business logic|fat (model|view)|refactor|"
                   r"structure|design)\b", re.I),
        "Enforce MVT layer contracts: models own rules, views orchestrate, templates present.",
    ),
]

DEFAULT_PERSONA = "mvt-analyst"
DEFAULT_REASON = ("Ambiguous request — default to architecture triage; "
                  "mvt-analyst re-routes to htmx-writer if it is really interactivity.")


def route(description: str) -> int:
    for persona, pattern, reason in _RULES:
        if pattern.search(description):
            print(f"ROUTE -> {persona}")
            print(f"Reason: {reason}")
            return 0
    print(f"ROUTE -> {DEFAULT_PERSONA}")
    print(f"Reason: {DEFAULT_REASON}")
    return 0


# --- Validators ---------------------------------------------------------------

def _run_gate(path: str, check_fn, gate_name: str) -> int:
    p = Path(path)
    if not p.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 1
    html = p.read_text(encoding="utf-8")
    results = check_fn(html)
    print(f"{gate_name}: {path}")
    ok = True
    for r in results:
        print(f"  {r}")
        ok = ok and r.passed
    if ok:
        print(f"{gate_name}: PASS — all {len(results)} checks green.")
        return 0
    failed = sum(1 for r in results if not r.passed)
    print(f"{gate_name}: FAIL — {failed} check(s) failed. Return to author for revision "
          f"(max 3 retries, then escalate).")
    return 1


def validate_phase1(path: str) -> int:
    return _run_gate(path, check_phase1_shape, "GATE P1 (htmx-writer output)")


def validate_phase2(path: str) -> int:
    return _run_gate(path, check_phase2_shape, "GATE P2 (spa-evolver output)")


# --- Handoff brief ------------------------------------------------------------

_TODO_BLOCK_RE = re.compile(
    r'<!--\s*(HYPERSCRIPT-TODO:.*?)-->', re.IGNORECASE | re.DOTALL)


def handoff(path: str) -> int:
    p = Path(path)
    if not p.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 1
    html = p.read_text(encoding="utf-8")
    blocks = _TODO_BLOCK_RE.findall(html)
    print(f"HANDOFF BRIEF for spa-evolver — source: {path}")
    print("=" * 60)
    if not blocks:
        print("No HYPERSCRIPT-TODO comments found.")
        if not HYPERSCRIPT_TODO_RE.search(html):
            print("Phase 1 artifact is missing handoff comments; send back to htmx-writer.")
        return 1
    for i, block in enumerate(blocks, 1):
        print(f"\n--- TODO #{i} ---")
        for line in block.splitlines():
            line = line.strip()
            if line:
                print(f"  {line}")
    print("\n" + "=" * 60)
    print("Instructions for spa-evolver:")
    print("  1. Replace each hx-on:* handler with behaviorally identical hyperscript in `_=`.")
    print("  2. Preserve State/Edge case items exactly (§2.4 translation rules).")
    print("  3. Remove ALL hx-on:* attributes (clean handoff).")
    print("  4. Add <!-- TRANSLATED-BY: spa-evolver --> with features used + verification note.")
    print("  5. Submit for Gate P2: router.py validate-phase2 <file>.")
    return 0


# --- CLI ----------------------------------------------------------------------

USAGE = __doc__.strip()


def main(argv) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(USAGE)
        return 0 if len(argv) >= 2 else 1
    cmd = argv[1]
    if cmd == "route":
        if len(argv) < 3:
            print('ERROR: route requires a task description: route "<task>"', file=sys.stderr)
            return 1
        return route(" ".join(argv[2:]))
    if cmd == "validate-phase1" and len(argv) == 3:
        return validate_phase1(argv[2])
    if cmd == "validate-phase2" and len(argv) == 3:
        return validate_phase2(argv[2])
    if cmd == "handoff" and len(argv) == 3:
        return handoff(argv[2])
    print(f"ERROR: unknown/ill-formed command: {' '.join(argv[1:])}\n", file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
