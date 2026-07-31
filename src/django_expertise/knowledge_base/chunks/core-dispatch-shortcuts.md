# View.dispatch() and django.shortcuts helpers

- **ID:** `core-dispatch-shortcuts`
- **Category:** django-core
- **Source:** §3.1 Core Framework, §2.2 View Layer
- **Tags:** `dispatch`, `shortcuts`, `views`

## Canonical pattern (Django / HTMX / Hyperscript way)
View.dispatch() routes HTTP methods to get()/post()/etc. handler methods on a CBV. django.shortcuts.render() renders a template with context, get_object_or_404() fetches or raises Http404, redirect() returns an HttpResponseRedirect (accepting a model, view name, or URL).

## Laravel / MVC default (what AI typically generates)
Laravel: Route::get -> closure or Controller@method with abort(404) via findOrFail($id); return view(...)->with(...). Rails: render/redirect_to. AI often writes HttpResponse with manual template loader calls or Model.objects.get wrapped in try/except.

## Why Django differs
Django codifies the request lifecycle in dispatch() so overriding it is the canonical interception point, and the shortcuts module removes boilerplate (manual Http404 raising, template rendering) that AI-generated code often reinvents.

## Example
from django.shortcuts import render, get_object_or_404, redirect

def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related('category'), pk=pk)
    if request.headers.get('HX-Request'):
        return render(request, 'products/_preview.html', {'product': product})
    return render(request, 'products/detail.html', {'product': product})
