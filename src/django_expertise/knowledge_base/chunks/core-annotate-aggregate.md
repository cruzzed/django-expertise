# annotate() vs aggregate()

- **ID:** `core-annotate-aggregate`
- **Category:** django-core
- **Source:** §3.1 Core Framework
- **Tags:** `aggregation`, `annotate`, `aggregate`, `sql`

## Canonical pattern (Django / HTMX / Hyperscript way)
annotate() adds a computed column to each row of a QuerySet (per-object Sum/Count); aggregate() reduces the whole QuerySet to a single dict of values. Use them to push computation into SQL instead of Python loops.

## Laravel / MVC default (what AI typically generates)
Laravel: DB::table('orders')->selectRaw('SUM(...)') raw selects, or computing totals in a collection map() after fetching all rows. Rails: pluck + Ruby sum. AI often fetches rows then computes totals in Python/PHP.

## Why Django differs
Django's ORM exposes SQL aggregation declaratively so the database does the work in one query; computing in Python after Model.objects.all() is both an N+1-style waste and a memory blowup.

## Example
from django.db.models import Sum, Count, F
qs = Order.objects.annotate(item_total=Sum('items__price'))
grand = Order.objects.aggregate(total=Sum('total'))  # {'total': Decimal(...)}
# Manager method from spec:
def with_totals(self):
    return self.annotate(item_total=Sum('items__price'),
                         tax_total=F('item_total') * 0.08)
