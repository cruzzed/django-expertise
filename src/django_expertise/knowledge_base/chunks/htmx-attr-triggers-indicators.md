# Triggers, indicators, values: hx-trigger, hx-indicator, hx-vals, hx-confirm

- **ID:** `htmx-attr-triggers-indicators`
- **Category:** htmx-attribute
- **Source:** §4.1 Core Attribute Reference, A-012
- **Tags:** `hx-trigger`, `hx-indicator`, `hx-vals`, `debounce`

## Canonical pattern (Django / HTMX / Hyperscript way)
hx-trigger names the event and modifiers (click, change, keyup changed delay:300ms, revealed, every 2s, from:body). hx-indicator shows a loading element (paired with the .htmx-indicator/.htmx-request CSS classes, not inline styles - spec A-012). hx-vals adds extra parameters (JSON or js:{...}); hx-confirm shows a browser confirm before issuing.

## Typical MVC default (what AI typically generates)
AI defaults: debounce implemented by hand with setTimeout in a keyup listener, loading spinners toggled via element.style.display = 'block' inline styles, extra params appended by string-building URLs in JS.

## Why Django differs
HTMX provides declarative debouncing (delay:), request deduping, and a CSS-class-based indicator contract so behavior is consistent and stylable. Django views receive hx-vals as normal request.POST/GET params - no client-side state machine needed.

## Example
<input type="search" name="q"
  hx-get="{% url 'product-search' %}"
  hx-target="#search-results"
  hx-trigger="keyup changed delay:300ms, search"
  hx-indicator="#search-spinner"
  hx-vals='{"sort": "price"}'
  hx-confirm="Apply filter?">
<div id="search-spinner" class="htmx-indicator">Searching...</div>
