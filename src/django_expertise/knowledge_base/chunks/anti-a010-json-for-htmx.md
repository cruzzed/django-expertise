# A-010: JSON API for HTMX endpoints

- **ID:** `anti-a010-json-for-htmx`
- **Category:** anti-pattern
- **Source:** §7 A-010
- **Tags:** `htmx`, `json`, `anti-pattern`, `partials`

## Canonical pattern (Django / HTMX / Hyperscript way)
HTMX endpoints return HTML partial templates (render(request, 'app/_partial.html', ctx)). The same view can serve full pages to non-HTMX requests (dual-response pattern).

## Laravel / MVC default (what AI typically generates)
Returning JsonResponse({...}) and writing client JS to template the result - because AI assumes all dynamic endpoints are REST/JSON APIs (DRF serializers, Laravel apiResource controllers).

## Why Django differs
HTMX swaps HTML, not data; returning JSON forces a client-side rendering layer you were trying to avoid. Django's template engine already renders the fragment server-side with full context, escaping, and {% url %} resolution.

## Example
# WRONG
return JsonResponse({'id': task.id, 'title': task.title, 'status': task.status})

# RIGHT
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    form = TaskForm(request.POST, instance=task)
    if form.is_valid():
        task = form.save()
    return render(request, 'tasks/_task_row.html', {'task': task})
