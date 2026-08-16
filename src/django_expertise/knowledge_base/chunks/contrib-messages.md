# django.contrib.messages (flash messages)

- **ID:** `contrib-messages`
- **Category:** contrib
- **Source:** §3.2 Contrib Modules, §4.2 OOB Toast
- **Tags:** `messages`, `flash`, `htmx`

## Canonical pattern (Django / HTMX / Hyperscript way)
django.contrib.messages provides one-time user notifications: messages.success(request, 'Saved!') in the view, rendered once in the template via {% for message in messages %}. With HTMX, prefer an out-of-band toast element over a full-page messages block.

## Typical MVC default (what AI typically generates)
Typical MVC frameworks use flash messages in the session plus alert partials. API-first AI returns {message: '...'} JSON for a client-side toast system instead of server-rendered feedback.

## Why Django differs
Django's messages framework integrates with the template layer and is the canonical full-page-feedback mechanism; in HTMX flows it degrades gracefully - the non-HTMX branch uses messages.success + redirect, while the HTMX branch returns an OOB toast (spec §4.2).

## Example
from django.contrib import messages

def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.status = 'completed'; task.save()
    if request.headers.get('HX-Request'):
        return render(request, 'tasks/_oob_response.html',
                      {'task': task, 'message': f"Task '{task.title}' completed!"})
    messages.success(request, f"Task '{task.title}' completed!")
    return redirect('task-list')
