# Active Search with Debounce

- **ID:** `htmx-pattern-active-search`
- **Category:** htmx-pattern
- **Source:** §4.2 Pattern: Active Search with Debounce
- **Tags:** `htmx`, `search`, `debounce`, `Q`

## Canonical pattern (Django / HTMX / Hyperscript way)
Search input with hx-trigger='keyup changed delay:300ms, search', hx-target a results div, hx-indicator spinner, and hx-push-url='true' so results are bookmarkable. The view filters with Q objects and returns only the results partial; value='{{ request.GET.q }}' restores state on full loads.

## Laravel / MVC default (what AI typically generates)
AI wires a React search component hitting /api/search?q= JSON endpoint, with useEffect debouncing and client-side rendering of results. Or jQuery keyup + $.get + manual .html().

## Why Django differs
Server-side Q-object filtering over icontains (or contrib.postgres full-text search) returns rendered HTML directly; hx-push-url keeps the address bar honest so refresh/back work - the React version needs a router and state hydration to match that.

## Example
<input type="search" name="q" placeholder="Search products..."
  hx-get="{% url 'product-search' %}" hx-target="#search-results"
  hx-trigger="keyup changed delay:300ms, search"
  hx-indicator="#search-spinner" hx-push-url="true" value="{{ request.GET.q }}">

# views.py
def product_search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    ).prefetch_related('category')[:20]
    return render(request, 'products/_results.html',
                  {'products': products, 'query': query})
