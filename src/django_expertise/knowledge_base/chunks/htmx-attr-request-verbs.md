# Request attributes: hx-get/post/put/delete/patch

- **ID:** `htmx-attr-request-verbs`
- **Category:** htmx-attribute
- **Source:** §4.1 Core Attribute Reference
- **Tags:** `hx-get`, `hx-post`, `hx-delete`, `csrf`

## Canonical pattern (Django / HTMX / Hyperscript way)
Issue AJAX requests with hx-get, hx-post, hx-put, hx-delete, hx-patch whose value is a Django URL resolved with {% url 'name' args %}. The server responds with an HTML fragment; non-GET verbs require Django's CSRF token (send via {% csrf_token %} in a form or the X-CSRFToken header).

## Laravel / MVC default (what AI typically generates)
Laravel + JS-stack AI: fetch('/api/products', {method:'POST', body: JSON.stringify(...)}) against a JSON API, or axios calls wired in a bundled component. Also common: wire:click Livewire-style or jQuery $.ajax.

## Why Django differs
Django + HTMX keeps routing server-side: the attribute embeds the named URL at render time, so URL changes never break clients. Responses are HTML partials from normal Django views - no separate JSON API layer is needed.

## Example
<button hx-post="{% url 'task-update' task.id %}"
        hx-target="#task-{{ task.id }}" hx-swap="outerHTML">
  Save
</button>
<button hx-delete="{% url 'task-delete' task.id %}"
        hx-confirm="Delete this task?" hx-target="closest tr" hx-swap="outerHTML">
  Delete
</button>
