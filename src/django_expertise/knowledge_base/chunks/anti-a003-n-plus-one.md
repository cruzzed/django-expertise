# A-003: N+1 queries in templates

- **ID:** `anti-a003-n-plus-one`
- **Category:** anti-pattern
- **Source:** §7 A-003
- **Tags:** `n+1`, `anti-pattern`, `prefetch`

## Canonical pattern (Django / HTMX / Hyperscript way)
Optimize in the View: Product.objects.select_related('category') / prefetch_related('tags') in get_queryset(), so {{ product.category.name }} in a loop costs zero extra queries.

## Laravel / MVC default (what AI typically generates)
Blade/Eloquent-style lazy loading: {{ product.category.name }} triggering a query per row (or $product->category->name in Blade), because AI examples rarely show eager loading.

## Why Django differs
Django never eager-loads implicitly; each relation traversal in a template loop is a SQL round-trip. 100 rows become 101 queries. Prefetching in the view is one extra line and is the View layer's responsibility per MVT.

## Example
# WRONG: template loop hits DB per row
def get_queryset(self):
    return Product.objects.all()

# RIGHT
def get_queryset(self):
    return Product.objects.select_related('category').prefetch_related('tags')
