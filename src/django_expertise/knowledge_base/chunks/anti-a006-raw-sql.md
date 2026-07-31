# A-006: Raw SQL without ORM fallback

- **ID:** `anti-a006-raw-sql`
- **Category:** anti-pattern
- **Source:** §7 A-006
- **Tags:** `sql`, `anti-pattern`, `orm`, `security`

## Canonical pattern (Django / HTMX / Hyperscript way)
Use the ORM (including Subquery, Window, F, Q) for everything it can express; reserve Model.objects.raw() / cursor.execute() for genuinely complex reports the ORM cannot model, always parameterized.

## Laravel / MVC default (what AI typically generates)
Laravel DB::select(DB::raw(...)) with string interpolation, or Arel/raw SQL in Rails - AI defaults to raw SQL for anything beyond trivial filters because generic SQL dominates training data.

## Why Django differs
Raw SQL loses Django's parameterization (injection risk), query composition, portability, and optimization; the ORM's expression API covers correlated subqueries and windows, so raw SQL is rarely justified.

## Example
# WRONG
cursor.execute(f"SELECT * FROM products WHERE name LIKE '%{q}%'")

# RIGHT
Product.objects.filter(name__icontains=q)
# Complex case stays in ORM:
Product.objects.annotate(current_price=Subquery(latest.values('amount')[:1]))
