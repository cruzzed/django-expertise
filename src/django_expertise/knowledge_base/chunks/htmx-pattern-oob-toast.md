# OOB Toast + Content Update (multiple elements per response)

- **ID:** `htmx-pattern-oob-toast`
- **Category:** htmx-pattern
- **Source:** §4.2 Pattern: OOB Toast + Content Update
- **Tags:** `htmx`, `oob`, `toast`, `messages`

## Canonical pattern (Django / HTMX / Hyperscript way)
Return a partial containing several fragments, each marked hx-swap-oob, so one request updates the changed row AND appends a toast notification. Pair with django.contrib.messages on the non-HTMX fallback path.

## Laravel / MVC default (what AI typically generates)
AI returns JSON {task: ..., message: ...} and writes client JS that updates the row DOM and calls a toast library (toastr/sweetalert) - two code paths to keep in sync.

## Why Django differs
hx-swap-oob lets the server compose multi-region updates declaratively in one template. The Django view stays the single source of truth for both the data change and the user feedback, using the same context dict.

## Example
# _oob_response.html
<tr id="task-{{ task.id }}" hx-swap-oob="true">
  <td colspan="4" class="completed">{{ task.title }} — Completed</td>
</tr>
<div id="toast-container" hx-swap-oob="beforeend">
  <div class="toast toast-success">{{ message }}</div>
</div>

# view
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.status = 'completed'; task.save()
    if request.headers.get('HX-Request'):
        return render(request, 'tasks/_oob_response.html',
                      {'task': task, 'message': f"Task '{task.title}' completed!"})
    messages.success(request, f"Task '{task.title}' completed!")
    return redirect('task-list')
