# select_related() and prefetch_related()

- **ID:** `core-select-prefetch-related`
- **Category:** django-core
- **Source:** §3.1 Core Framework
- **Tags:** `n+1`, `query-optimization`, `select_related`, `prefetch_related`

## Canonical pattern (Django / HTMX / Hyperscript way)
Use select_related() for foreign-key and one-to-one relations (single SQL JOIN) and prefetch_related() for many-to-many and reverse-FK relations (separate batched queries). Call them in the View's get_queryset(), never rely on the template to trigger lazy lookups.

## Typical MVC default (what AI typically generates)
Typical MVC ORMs offer eager-loading directives on the query, or worse, let templates trigger lazy loading (traversing a relation per row in a loop). AI frequently omits eager loading entirely because training examples show naive loops.

## Why Django differs
Django does no automatic eager loading; every attribute traversal across a relation in a template is a SQL query. Explicit select_related/prefetch_related in the View is the documented fix for N+1 and is the View's responsibility under MVT.

## Example
def get_queryset(self):
    return (Product.objects
            .select_related('category')       # FK: JOIN
            .prefetch_related('tags'))        # M2M: batched IN query

