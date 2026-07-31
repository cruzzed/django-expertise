# Infinite Scroll via hx-trigger='revealed'

- **ID:** `htmx-pattern-infinite-scroll`
- **Category:** htmx-pattern
- **Source:** §4.2 Pattern: Infinite Scroll
- **Tags:** `htmx`, `pagination`, `revealed`

## Canonical pattern (Django / HTMX / Hyperscript way)
A sentinel div after the page items issues hx-get for the next page when it scrolls into view (hx-trigger='revealed'), appending with hx-swap='beforeend'. The view paginates with Django's Paginator/ListView and the partial re-renders the next sentinel only if page_obj.has_next.

## Laravel / MVC default (what AI typically generates)
AI installs a JS infinite-scroll library (or IntersectionObserver by hand) plus a JSON paginated API, then client-renders each item from a template literal. Laravel default: cursor pagination API consumed by axios.

## Why Django differs
Django's Paginator already paginates; the sentinel + revealed trigger turns pagination into progressive enhancement. Because the response includes the next sentinel only when has_next, the mechanism terminates naturally with zero client state.

## Example
{% if page_obj.has_next %}
  <div hx-get="{% url 'product-list' %}?page={{ page_obj.next_page_number }}"
       hx-target="#product-container" hx-swap="beforeend"
       hx-trigger="revealed" hx-indicator="#scroll-indicator">
    <span id="scroll-indicator" class="htmx-indicator">Loading more...</span>
  </div>
{% endif %}

# view
paginator = Paginator(Product.objects.all(), 20)
page_obj = paginator.get_page(request.GET.get('page', 1))
return render(request, 'products/_product_list.html', {'page_obj': page_obj})
