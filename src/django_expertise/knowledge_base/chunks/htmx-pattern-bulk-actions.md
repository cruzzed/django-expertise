# Bulk Actions with Checkboxes

- **ID:** `htmx-pattern-bulk-actions`
- **Category:** htmx-pattern
- **Source:** §4.2 Pattern: Bulk Actions with Checkboxes
- **Tags:** `htmx`, `forms`, `bulk-actions`

## Canonical pattern (Django / HTMX / Hyperscript way)
A single form wraps the table; checkboxes named task_ids carry selections, a select names the action, and the form hx-posts with hx-target the table (hx-swap='outerHTML') plus hx-confirm. The view reads request.POST.getlist('task_ids') and dispatches - mirroring the Django admin's actions pattern.

## Typical MVC default (what AI typically generates)
AI manages a selected-ids array in client-side component state, disables the Apply button until non-empty, and POSTs {ids: [...], action: '...'} JSON to an API - reimplementing what HTML forms already serialize for free.

## Why Django differs
Native form semantics mean the no-JS fallback is the same form doing a normal POST. The view is one code path (HX or not) and the pattern deliberately echoes ModelAdmin actions, so conventions carry over.

## Example
<form id="bulk-form" hx-post="{% url 'task-bulk-action' %}"
      hx-target="#task-table" hx-swap="outerHTML"
      hx-confirm="Perform this action on selected tasks?">
  <select name="action" required>
    <option value="complete">Mark Complete</option>
    <option value="delete">Delete</option>
  </select>
  <button type="submit">Apply</button>
  <table id="task-table"> ... checkboxes name="task_ids" ... </table>
</form>

# views.py
ids = request.POST.getlist('task_ids')
action = request.POST.get('action')
qs = Task.objects.filter(pk__in=ids)
if action == 'complete': qs.update(status='completed')
