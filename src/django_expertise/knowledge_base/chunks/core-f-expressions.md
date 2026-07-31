# F() expressions for database-level operations

- **ID:** `core-f-expressions`
- **Category:** django-core
- **Source:** §3.1 Core Framework
- **Tags:** `F`, `atomic`, `concurrency`, `orm`

## Canonical pattern (Django / HTMX / Hyperscript way)
F() references a model field at the SQL level, enabling atomic updates (Model.objects.filter(pk=pk).update(count=F('count')+1)) and field-to-field comparisons/annotations without reading values into Python.

## Laravel / MVC default (what AI typically generates)
Laravel: DB::raw('count + 1') raw expressions, or read-modify-write in PHP ($m->count++; $m->save();). Rails: update_counters or raw SQL strings. AI usually generates a Python-side read-modify-write, which races under concurrency.

## Why Django differs
F() pushes the arithmetic into a single UPDATE statement, making it atomic and avoiding race conditions inherent to fetch-then-save. It is Django's canonical answer to concurrent counter updates.

## Example
from django.db.models import F
Product.objects.filter(pk=pk).update(stock=F('stock') - 1)
qs = Order.objects.annotate(tax=F('item_total') * 0.08)
expiring = Job.objects.filter(deadline__lt=F('created_at') + timedelta(days=30))
