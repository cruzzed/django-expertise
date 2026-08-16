# Dual-Response View (full page + partial from one view)

- **ID:** `htmx-pattern-dual-response`
- **Category:** htmx-pattern
- **Source:** §4.2 Pattern: The Dual-Response View
- **Tags:** `htmx`, `partial`, `graceful-degradation`

## Canonical pattern (Django / HTMX / Hyperscript way)
One Django view serves both worlds: check request.headers.get('HX-Request') and return a partial template (_task_row.html / _task_list.html) for HTMX requests, the full page template otherwise. Handles GET and POST branches separately so POST+HX returns just the new row.

## Typical MVC default (what AI typically generates)
AI defaults to separate /api/tasks JSON endpoints plus a JS frontend, or two parallel controllers (web + api) in typical MVC frameworks. Duplicated endpoints and a client-side renderer.

## Why Django differs
A single view with a template switch preserves one URL, one permission check, one queryset - and gives graceful degradation for free (no-JS browsers get the full page). Returning HTML partials instead of JSON is explicitly the HTMX way (A-010).

## Example
@require_http_methods(["GET", "POST"])
def task_list(request):
    tasks = Task.objects.prefetch_related('assignee')
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            if request.headers.get('HX-Request'):
                return render(request, 'tasks/_task_row.html', {'task': task})
    else:
        form = TaskForm()
    if request.headers.get('HX-Request'):
        return render(request, 'tasks/_task_list.html',
                      {'tasks': tasks, 'form': form})
    return render(request, 'tasks/list.html', {'tasks': tasks, 'form': form})
