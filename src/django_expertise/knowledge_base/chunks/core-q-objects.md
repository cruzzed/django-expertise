# Q() objects for complex lookups

- **ID:** `core-q-objects`
- **Category:** django-core
- **Source:** §3.1 Core Framework
- **Tags:** `Q`, `complex-queries`, `orm`

## Canonical pattern (Django / HTMX / Hyperscript way)
Q() objects compose OR/NOT conditions that keyword arguments (which AND together) cannot express: Model.objects.filter(Q(a=1) | Q(b=2), ~Q(c=3)). Combine freely with &= and |=.

## Laravel / MVC default (what AI typically generates)
Laravel: nested where closures ($q->where(...)->orWhere(...)) in the query builder. Rails: Arel or raw SQL string fragments. AI often emits raw SQL WHERE strings or chained orWhere calls that mishandle operator precedence.

## Why Django differs
Django keeps query construction fully in Python with correct parenthesization and parameterization. Q objects are composable, testable units - no SQL string concatenation, no injection risk.

## Example
from django.db.models import Q
products = Product.objects.filter(
    Q(name__icontains=query) | Q(description__icontains=query)
).exclude(Q(discontinued=True) | Q(stock=0))[:20]
