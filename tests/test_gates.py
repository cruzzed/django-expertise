"""Tests for the Django expertise quality gates."""

import unittest

from django_expertise import gates


class Phase1GateTests(unittest.TestCase):
    def test_valid_phase1_passes(self):
        html = """<!--
  HYPERSCRIPT-TODO:
  - Event: click on this button
  - Action: toggle visibility
-->
<button hx-post="/action/" hx-on:click="this.classList.toggle('active')">Go</button>
"""
        results = gates.check_phase1_shape(html)
        self.assertTrue(all(r.passed for r in results), results)

    def test_missing_hx_on_fails(self):
        html = """<!-- HYPERSCRIPT-TODO: event: click --><button hx-post="/action/">Go</button>"""
        results = gates.check_phase1_shape(html)
        self.assertFalse(all(r.passed for r in results))

    def test_hyperscript_in_phase1_fails(self):
        html = """<!-- HYPERSCRIPT-TODO: event: click -->
<button hx-post="/action/" _="on click toggle .active on me">Go</button>"""
        results = gates.check_phase1_shape(html)
        self.assertFalse(all(r.passed for r in results))

    def test_inline_script_fails(self):
        html = """<!-- HYPERSCRIPT-TODO: event: click -->
<button hx-post="/action/" hx-on:click="go()">Go</button>
<script>function go() {}</script>"""
        results = gates.check_phase1_shape(html)
        self.assertFalse(all(r.passed for r in results))


class Phase2GateTests(unittest.TestCase):
    def test_valid_phase2_passes(self):
        html = """<!-- TRANSLATED-BY: spa-evolver -->
<button hx-post="/action/" _="on click toggle .active on me end">Go</button>
"""
        results = gates.check_phase2_shape(html)
        self.assertTrue(all(r.passed for r in results), results)

    def test_remaining_hx_on_fails(self):
        html = """<!-- TRANSLATED-BY: spa-evolver -->
<button hx-post="/action/" hx-on:click="go()" _="on click go() end">Go</button>"""
        results = gates.check_phase2_shape(html)
        self.assertFalse(all(r.passed for r in results))


class GracefulDegradationTests(unittest.TestCase):
    def test_view_with_fallback_passes(self):
        src = """def preview(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    if request.headers.get('HX-Request'):
        return render(request, 'products/_preview.html', {'obj': obj})
    return render(request, 'products/detail.html', {'obj': obj})
"""
        result = gates.check_graceful_degradation(src)
        self.assertTrue(result.passed, result)

    def test_partial_only_fails(self):
        src = """def preview(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    return render(request, 'products/_preview.html', {'obj': obj})
"""
        result = gates.check_graceful_degradation(src)
        self.assertFalse(result.passed)


if __name__ == "__main__":
    unittest.main()
