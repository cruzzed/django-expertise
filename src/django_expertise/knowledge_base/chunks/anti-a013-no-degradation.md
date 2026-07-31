# A-013: Missing graceful degradation

- **ID:** `anti-a013-no-degradation`
- **Category:** anti-pattern
- **Source:** §7 A-013, §8 gate 5
- **Tags:** `htmx`, `degradation`, `anti-pattern`

## Canonical pattern (Django / HTMX / Hyperscript way)
Every HTMX view also handles normal requests: check HX-Request and return the partial only for HTMX, else the full page (dual-response). Forms keep action= real URLs so they work with JS disabled.

## Laravel / MVC default (what AI typically generates)
Building endpoints that only return fragments (500s or blank pages without JS), or a pure SPA that renders nothing if the bundle fails - AI rarely adds the fallback path.

## Why Django differs
Graceful degradation is a quality gate (§8 gate 5): without it, a JS failure bricks the app, deep links to partials render unstyled fragments, and SEO/accessibility suffer. The check is one if statement per view.

## Example
def product_quick_preview(request, pk):
    product = get_object_or_404(Product.objects.prefetch_related('images'), pk=pk)
    if request.headers.get('HX-Request'):
        return render(request, 'products/_preview.html', {'product': product})
    # Graceful degradation: full page
    return render(request, 'products/detail.html', {'product': product})
