# A-014: Over-prefetching

- **ID:** `anti-a014-over-prefetching`
- **Category:** anti-pattern
- **Source:** §7 A-014
- **Tags:** `performance`, `prefetch`, `anti-pattern`

## Canonical pattern (Django / HTMX / Hyperscript way)
Prefetch exactly what the template renders: audit the partial/full template and select_related/prefetch_related only those relations. Drop prefetches when trimming the template.

## Typical MVC default (what AI typically generates)
select_related('*')-style 'prefetch everything to be safe' (typical MVC ORMs: eager-loading the entire relation graph), which AI does to preempt N+1 warnings.

## Why Django differs
Every prefetch is extra SQL + memory for hydrated objects. Prefetching relations the template never touches inflates query time and RAM - the cure becomes worse than one N+1. The spec calls for prefetching 'only what the template needs'.

## Example
# WRONG: grabs everything
Product.objects.select_related('category', 'vendor', 'warehouse')                .prefetch_related('tags', 'reviews', 'images', 'discounts')

# RIGHT: template shows name + category.name only
Product.objects.select_related('category')
