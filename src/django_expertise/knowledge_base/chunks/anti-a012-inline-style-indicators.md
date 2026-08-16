# A-012: Inline styles for HTMX indicators

- **ID:** `anti-a012-inline-style-indicators`
- **Category:** anti-pattern
- **Source:** §7 A-012
- **Tags:** `htmx`, `css`, `indicator`, `anti-pattern`

## Canonical pattern (Django / HTMX / Hyperscript way)
Use hx-indicator='#spinner' with the standard CSS contract: .htmx-indicator {opacity: 0} and .htmx-request .htmx-indicator {opacity: 1} (or .htmx-request.htmx-indicator for the triggering element itself).

## Typical MVC default (what AI typically generates)
Toggling element.style.display in hx-on handlers or sprinkling style='display:none' inline - the legacy-AJAX habit of imperative show/hide per element.

## Why Django differs
HTMX already adds/removes the htmx-request class around requests; a single CSS rule pair drives every indicator consistently. Inline styles per element are un-maintainable and inconsistent (spec A-012).

## Example
/* stylesheet */
.htmx-indicator { opacity: 0; transition: opacity 200ms; }
.htmx-request .htmx-indicator,
.htmx-request.htmx-indicator { opacity: 1; }

<!-- template -->
<button hx-post="{% url 'save' %}" hx-indicator="#spinner">Save</button>
<span id="spinner" class="htmx-indicator">⏳</span>
