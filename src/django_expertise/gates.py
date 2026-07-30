"""
gates.py — Reusable quality-gate checks implementing spec §8 (Quality Gates).

Each check returns a GateResult(passed, gate, message). These are pure
stdlib functions over source text so they can be reused by router.py,
CI hooks, or an anti-pattern sentinel.

Gates (spec §8):
  1. RTFM Gate                    — heuristic: no third-party imports when a
                                    django.contrib battery exists (checked in views).
  2. MVT Gate                     — no queries in templates, no model-layer
                                    business logic smells in views.
  3. HTMX Gate                    — interactivity via hx-on (Phase 1) or
                                    hyperscript (Phase 2); no inline <script>.
  4. Hyperscript Gate             — Phase 2: no hx-on remains, TRANSLATED-BY present.
  5. Graceful Degradation Gate    — view handles both HX-Request and normal requests.
  6. Query Optimization Gate      — select_related/prefetch_related when template
                                    loops over related objects.
  7. Security Gate                — CSRF token in forms, permission checks in views.
"""

from dataclasses import dataclass
import re

# --- Shared patterns ---------------------------------------------------------

HX_ON_RE = re.compile(r'\bhx-on:[\w:.\-]+\s*=', re.IGNORECASE)
HYPERSCRIPT_ATTR_RE = re.compile(r'(?:^|[\s<])_\s*=\s*["\']', re.MULTILINE)
SCRIPT_TAG_RE = re.compile(r'<script\b([^>]*)>(.*?)</script>', re.IGNORECASE | re.DOTALL)
HYPERSCRIPT_TODO_RE = re.compile(r'<!--\s*HYPERSCRIPT-TODO', re.IGNORECASE)
TRANSLATED_BY_RE = re.compile(r'<!--\s*TRANSLATED-BY:\s*spa-evolver', re.IGNORECASE)
HX_REQUEST_ATTR_RE = re.compile(r'\bhx-(?:get|post|put|delete|patch)\s*=', re.IGNORECASE)


@dataclass
class GateResult:
    passed: bool
    gate: str
    message: str

    def __str__(self):
        mark = "PASS" if self.passed else "FAIL"
        return f"[{mark}] {self.gate}: {self.message}"


# --- Gate 3: HTMX Gate -------------------------------------------------------

def check_no_inline_scripts(html: str) -> GateResult:
    """§8.3 HTMX Gate: no inline <script> tags.

    External CDN scripts (htmx, hyperscript, _hyperscript) with a src= and an
    empty body are allowed; any <script> with a non-empty inline body fails.
    """
    offenders = []
    for m in SCRIPT_TAG_RE.finditer(html):
        attrs, body = m.group(1), m.group(2).strip()
        if body and "src" not in attrs.lower():
            line = html.count("\n", 0, m.start()) + 1
            offenders.append(line)
    if offenders:
        return GateResult(False, "HTMX Gate (no inline <script>)",
                          f"inline <script> tag(s) at line(s) {offenders}; use hx-on:* or hyperscript instead")
    return GateResult(True, "HTMX Gate (no inline <script>)", "no inline <script> tags found")


def check_phase1_shape(html: str) -> list:
    """Phase 1 (htmx-writer) structural checks. Returns list[GateResult]."""
    results = []
    if HX_ON_RE.search(html):
        results.append(GateResult(True, "Phase 1 (hx-on present)",
                                  "found hx-on:* handler(s)"))
    else:
        results.append(GateResult(False, "Phase 1 (hx-on present)",
                                  "no hx-on:* handlers found; Phase 1 must implement interactivity via hx-on:*"))
    if HYPERSCRIPT_TODO_RE.search(html):
        results.append(GateResult(True, "Phase 1 (HYPERSCRIPT-TODO present)",
                                  "handoff comment(s) found"))
    else:
        results.append(GateResult(False, "Phase 1 (HYPERSCRIPT-TODO present)",
                                  "missing <!-- HYPERSCRIPT-TODO: ... --> handoff comments (§6.1)"))
    if HYPERSCRIPT_ATTR_RE.search(html):
        results.append(GateResult(False, "Phase 1 (no hyperscript yet)",
                                  "found `_=` hyperscript attribute; hyperscript belongs to Phase 2 (spa-evolver)"))
    else:
        results.append(GateResult(True, "Phase 1 (no hyperscript yet)",
                                  "no `_=` attributes present"))
    results.append(check_no_inline_scripts(html))
    return results


def check_phase2_shape(html: str) -> list:
    """Phase 2 (spa-evolver) structural checks. Returns list[GateResult]."""
    results = []
    if HYPERSCRIPT_ATTR_RE.search(html):
        results.append(GateResult(True, "Phase 2 (hyperscript present)",
                                  "found `_=` hyperscript attribute(s)"))
    else:
        results.append(GateResult(False, "Phase 2 (hyperscript present)",
                                  "no `_=` hyperscript attributes found; Phase 2 must translate to hyperscript"))
    if HX_ON_RE.search(html):
        results.append(GateResult(False, "Hyperscript Gate (clean handoff)",
                                  "hx-on:* attributes remain; spa-evolver must remove all of them (§2.4)"))
    else:
        results.append(GateResult(True, "Hyperscript Gate (clean handoff)",
                                  "no hx-on:* attributes remain"))
    if TRANSLATED_BY_RE.search(html):
        results.append(GateResult(True, "Phase 2 (TRANSLATED-BY present)",
                                  "translation provenance comment found"))
    else:
        results.append(GateResult(False, "Phase 2 (TRANSLATED-BY present)",
                                  "missing <!-- TRANSLATED-BY: spa-evolver --> comment (§6.1)"))
    if HX_REQUEST_ATTR_RE.search(html):
        results.append(GateResult(True, "Phase 2 (core hx-* intact)",
                                  "hx-get/post/put/delete/patch request attribute(s) preserved"))
    else:
        results.append(GateResult(False, "Phase 2 (core hx-* intact)",
                                  "core hx-* request attributes lost in translation; server round-trips must remain"))
    results.append(check_no_inline_scripts(html))
    return results


# --- Gate 5: Graceful Degradation --------------------------------------------

def check_graceful_degradation(view_source: str) -> GateResult:
    """§8.5: view handles both HX-Request and normal requests.

    Passes if the view source inspects the HX-Request header (or an
    HTMXMiddleware-style request.htmx flag) AND has a fallback render/redirect
    for non-HTMX requests.
    """
    detects_htmx = (
        "HX-Request" in view_source
        or "request.htmx" in view_source
    )
    has_fallback = (
        view_source.count("render(") >= 2
        or "redirect(" in view_source
        or re.search(r'else\s*:\s*\n\s*return\s+render\(', view_source) is not None
    )
    if not detects_htmx:
        return GateResult(False, "Graceful Degradation Gate",
                          "view never checks HX-Request / request.htmx; HTMX endpoints must degrade gracefully (A-013)")
    if not has_fallback:
        return GateResult(False, "Graceful Degradation Gate",
                          "view checks HX-Request but has no full-page fallback (render/redirect) for normal requests")
    return GateResult(True, "Graceful Degradation Gate",
                      "view branches on HX-Request and provides a full-page fallback")


# --- Gate 1: RTFM Gate (heuristic) -------------------------------------------

#: third-party import fragments -> the django.contrib battery that likely replaces them
THIRD_PARTY_RED_FLAGS = {
    "jwt": "django.contrib.auth (session auth) covers most auth needs",
    "rest_framework": "consider whether Django views + partial templates suffice for HTMX endpoints",
    "redis": "django.core.cache first; external backends only when scale demands",
    "requests": "urllib/httpx are fine, but check django.core.mail / contrib first for comms",
    "sendgrid": "django.core.mail",
}


def check_rtfm(view_source: str) -> GateResult:
    """§8.1: heuristic scan for third-party imports with a built-in alternative."""
    hits = [f"{pkg} -> {why}" for pkg, why in THIRD_PARTY_RED_FLAGS.items()
            if re.search(rf'^\s*(?:import|from)\s+{re.escape(pkg)}\b', view_source, re.MULTILINE)]
    if hits:
        return GateResult(False, "RTFM Gate",
                          "third-party import(s) detected; verify django.contrib first: " + "; ".join(hits))
    return GateResult(True, "RTFM Gate", "no third-party imports shadowing a Django built-in")


# --- Gate 2: MVT Gate ---------------------------------------------------------

def check_mvt_boundaries(template_source: str) -> GateResult:
    """§8.2: template must not run queries or heavy logic (presentation only)."""
    problems = []
    if re.search(r'\{\{[^}]*\.objects\.', template_source):
        problems.append("queryset access (`.objects.`) inside template expression")
    if re.search(r'\{%\s*\w+\s+(?:in|with)[^%]*\.objects\.', template_source):
        problems.append("ORM query inside {% %} tag")
    if problems:
        return GateResult(False, "MVT Gate",
                          "template-layer violation(s): " + "; ".join(problems) +
                          " — move queries to the View (A-003/A-004)")
    return GateResult(True, "MVT Gate", "template appears presentation-only")


# --- Gate 6: Query Optimization ----------------------------------------------

def check_query_optimization(view_source: str, template_source: str = "") -> GateResult:
    """§8.6: related-object access in loops should be prefetched in the view.

    Heuristic: if a template loops and dereferences through a FK/M2M
    (`{{ item.rel.attr }}`), the view should use select_related/prefetch_related.
    """
    template_needs_prefetch = bool(
        re.search(r'\{%\s*for\s+\w+\s+in\s+\w+\s*%\}.*?\{\{\s*\w+\.\w+\.\w+', template_source, re.DOTALL)
    )
    optimized = "select_related" in view_source or "prefetch_related" in view_source
    if template_needs_prefetch and not optimized:
        return GateResult(False, "Query Optimization Gate",
                          "template dereferences related objects in a loop but view lacks "
                          "select_related/prefetch_related (A-003 N+1)")
    return GateResult(True, "Query Optimization Gate",
                      "no N+1 risk detected (or related data already prefetched)")


# --- Gate 7: Security Gate ----------------------------------------------------

def check_csrf(template_source: str) -> GateResult:
    """§8.7: every mutating <form> needs a CSRF token."""
    forms = re.findall(r'<form\b.*?</form>', template_source, re.IGNORECASE | re.DOTALL)
    missing = []
    for i, form in enumerate(forms, 1):
        is_mutating = re.search(r'method\s*=\s*["\']?post', form, re.IGNORECASE) or "hx-post" in form \
            or "hx-put" in form or "hx-delete" in form or "hx-patch" in form
        if is_mutating and "{% csrf_token %}" not in form:
            missing.append(i)
    if missing:
        return GateResult(False, "Security Gate (CSRF)",
                          f"mutating form(s) #{missing} missing {{% csrf_token %}}")
    return GateResult(True, "Security Gate (CSRF)", "all mutating forms carry {% csrf_token %}")


def check_permissions(view_source: str) -> GateResult:
    """§8.7: views performing mutations should be protected."""
    mutates = re.search(r'\.save\(\)|\.delete\(\)|\.create\(|hx-(?:post|put|delete|patch)', view_source)
    protected = ("login_required" in view_source or "LoginRequiredMixin" in view_source
                 or "PermissionRequiredMixin" in view_source or "permission_required" in view_source
                 or "UserPassesTestMixin" in view_source)
    if mutates and not protected:
        return GateResult(False, "Security Gate (permissions)",
                          "mutating view lacks login_required / *Mixin protection")
    return GateResult(True, "Security Gate (permissions)", "mutations are permission-protected (or none found)")
