# Inline Editing (The HTMX Way)

- **ID:** `htmx-pattern-inline-editing`
- **Category:** htmx-pattern
- **Source:** §4.2 Pattern: Inline Editing
- **Tags:** `htmx`, `inline-edit`, `partials`

## Canonical pattern (Django / HTMX / Hyperscript way)
Click-to-edit: a span with hx-get to an edit-form endpoint swapping hx-target='closest td' innerHTML; the returned form hx-posts back with hx-target the row id and hx-swap='outerHTML', receiving the updated read-only row. Escape key re-triggers the view mode via hx-on:keydown.

## Typical MVC default (what AI typically generates)
AI builds an inline-editable component-based table row with controlled inputs, local state, and a PATCH JSON call - or a server-driven component with wire-style attributes. Heavy client state machinery for what is two partial templates.

## Why Django differs
The HTMX way swaps server-rendered HTML for each state (display form, edit form, updated row), so validation errors render server-side in the returned partial and the row id anchors the swap. No client-side model of the data is ever created.

## Example
<!-- _task_row.html -->
<span class="editable"
      hx-get="{% url 'task-edit-form' task.id %}"
      hx-target="closest td" hx-swap="innerHTML">{{ task.title }}</span>

<!-- _task_edit_form.html -->
<form hx-post="{% url 'task-update' task.id %}"
      hx-target="#task-{{ task.id }}" hx-swap="outerHTML">
  <input type="text" name="title" value="{{ task.title }}" autofocus
    hx-on:keydown[key=='Escape']="
      htmx.trigger(this.closest('td').querySelector('.editable'), 'click');">
</form>
