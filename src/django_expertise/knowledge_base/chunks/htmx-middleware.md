# HTMXMiddleware for request.htmx flags

- **ID:** `htmx-middleware`
- **Category:** htmx-pattern
- **Source:** §4.3 HTMX + Django Middleware
- **Tags:** `htmx`, `middleware`, `vary`

## Canonical pattern (Django / HTMX / Hyperscript way)
A custom middleware (spec §4.3) decorates the request with request.htmx, request.htmx_target, request.htmx_trigger, request.htmx_current_url parsed from HX-* headers, and adds response['Vary'] = 'HX-Request' so caches distinguish HTMX from full responses. Register in MIDDLEWARE in settings.py.

## Laravel / MVC default (what AI typically generates)
Laravel: checking $request->header('HX-Request') inline in every controller, or writing a helper macro; Rails: request.headers in before_action. AI scatters header sniffing through views instead of centralizing it.

## Why Django differs
Django middleware is the canonical cross-cutting hook (see core-middleware-hooks). Centralizing header parsing keeps views clean (if request.htmx:) and the Vary header prevents shared caches from serving partials to full-page requests - a subtle bug the inline approach misses.

## Example
class HTMXMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.htmx = request.headers.get('HX-Request') == 'true'
        request.htmx_target = request.headers.get('HX-Target', None)
        request.htmx_trigger = request.headers.get('HX-Trigger', None)
        request.htmx_current_url = request.headers.get('HX-Current-URL', None)
        response = self.get_response(request)
        if request.htmx:
            response['Vary'] = 'HX-Request'
        return response
