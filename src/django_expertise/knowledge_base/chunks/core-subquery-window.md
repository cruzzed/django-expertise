# Subquery/OuterRef and Window functions

- **ID:** `core-subquery-window`
- **Category:** django-core
- **Source:** §3.1 Core Framework
- **Tags:** `subquery`, `outerref`, `window`, `advanced-orm`

## Canonical pattern (Django / HTMX / Hyperscript way)
Subquery with OuterRef builds correlated subqueries (e.g. latest price per product); django.db.models.functions.Window provides ROW_NUMBER, RANK etc. over partitions - both keep set-based logic in one SQL round-trip.

## Laravel / MVC default (what AI typically generates)
Laravel: DB::select with hand-written correlated SQL or lateral joins; Eloquent has no first-class window API, so AI reaches for addSelect(DB::raw(...)) or post-processing collections in PHP.

## Why Django differs
Django's expression API (Subquery, OuterRef, Window) models these SQL constructs as typed, composable ORM objects. You get correlated subqueries and window functions without dropping to raw SQL, preserving portability and parameterization.

## Example
from django.db.models import Subquery, OuterRef
from django.db.models.functions import RowNumber
from django.db.models import Window
latest = Price.objects.filter(product=OuterRef('pk')).order_by('-created_at')
products = Product.objects.annotate(current_price=Subquery(latest.values('amount')[:1]))
ranked = Sale.objects.annotate(rn=Window(expression=RowNumber(),
        partition_by='region', order_by='-amount'))
