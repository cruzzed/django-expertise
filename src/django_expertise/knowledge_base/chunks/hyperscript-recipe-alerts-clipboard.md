# Recipes: auto-dismiss alerts and copy-to-clipboard

- **ID:** `hyperscript-recipe-alerts-clipboard`
- **Category:** hyperscript
- **Source:** §5.3 Common Hyperscript Recipes
- **Tags:** `hyperscript`, `alerts`, `clipboard`, `wait`

## Canonical pattern (Django / HTMX / Hyperscript way)
Auto-dismiss alert: on load wait 5s then transition opacity to 0 over 1s then remove me. Copy button: on click writeText(...) on navigator.clipboard, give 'Copied!' feedback, wait 2s, restore label - all inline in the _ attribute.

## Laravel / MVC default (what AI typically generates)
AI pulls in a toast/notification library and a clipboard JS package, or writes addEventListener + setTimeout + classList boilerplate per element in a <script> block (forbidden by the HTMX gate).

## Why Django differs
Hyperscript's temporal commands (wait, transition) express UI timing declaratively where vanilla JS needs nested setTimeouts. Keeping behavior in the element's attribute preserves locality of behavior - no selector wiring between script and markup.

## Example
<div class="alert alert-success"
     _="on load wait 5s then transition opacity to 0 over 1s then remove me">
  {{ message }}
</div>

<button _="on click
    writeText(my previousElementSibling's innerText) on navigator.clipboard
    put 'Copied!' into me
    wait 2s
    put 'Copy' into me
  end">Copy</button>
