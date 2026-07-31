# Targeting and swapping: hx-target, hx-swap, hx-select, hx-swap-oob

- **ID:** `htmx-attr-swap-target`
- **Category:** htmx-attribute
- **Source:** §4.1 Core Attribute Reference
- **Tags:** `hx-target`, `hx-swap`, `hx-swap-oob`, `hx-select`

## Canonical pattern (Django / HTMX / Hyperscript way)
hx-target picks the element to update (CSS selector, closest/find/this); hx-swap controls how (innerHTML default, outerHTML, beforeend, afterbegin, beforebegin, afterend, delete, none - plus modifiers like transition:true). hx-select extracts a subset of the response; hx-swap-oob on response elements swaps extra targets out-of-band.

## Laravel / MVC default (what AI typically generates)
React/Vue-trained AI: re-render a client-side component subtree from JSON state, or manually element.innerHTML = data in a fetch callback with no swap semantics. jQuery default: $('#list').html(response).

## Why Django differs
HTMX pushes swap mechanics into declarative HTML so the Django view just returns a partial template. outerHTML replacing the triggering row is the canonical 'row update' idiom, and OOB swaps let one request update several page regions - something JSON APIs need extra client code for.

## Example
<tr id="task-{{ task.id }}">
  <td hx-get="{% url 'task-edit-form' task.id %}"
      hx-target="closest td" hx-swap="innerHTML">{{ task.title }}</td>
</tr>

<!-- response with out-of-band updates -->
<tr id="task-{{ task.id }}" hx-swap-oob="true">...</tr>
<div id="toast-container" hx-swap-oob="beforeend"><div class="toast">{{ message }}</div></div>
