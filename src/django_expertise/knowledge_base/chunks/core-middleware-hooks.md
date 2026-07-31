# Middleware: MiddlewareMixin, process_view, process_template_response

- **ID:** `core-middleware-hooks`
- **Category:** django-core
- **Source:** §3.1 Core Framework, §4.3
- **Tags:** `middleware`, `process_view`, `htmx`

## Canonical pattern (Django / HTMX / Hyperscript way)
Custom middleware subclasses django.utils.deprecation.MiddlewareMixin (or plain __call__ style). Hooks: process_request, process_view (runs before the view, can short-circuit with a response), process_template_response (post-view, can modify/replace the template of a TemplateResponse).

## Laravel / MVC default (what AI typically generates)
Laravel: middleware with handle($request, Closure $next) classes registered in Kernel; the before/after mental model is similar, but AI also suggests Express-style app.use() chains or doing request-flag decoration in each controller manually.

## Why Django differs
Django middleware is onion-ordered around the view and is the canonical place for cross-cutting request decoration - e.g. attaching request.htmx for HTMX-aware views (spec §4.3) - instead of repeating header checks in every view.

## Example
class HTMXMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.htmx = request.headers.get('HX-Request') == 'true'
        response = self.get_response(request)
        if request.htmx:
            response['Vary'] = 'HX-Request'
        return response
# settings.py: MIDDLEWARE = [..., 'myapp.middleware.HTMXMiddleware']
