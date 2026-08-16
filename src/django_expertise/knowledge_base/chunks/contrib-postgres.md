# django.contrib.postgres (PostgreSQL-specific fields/search)

- **ID:** `contrib-postgres`
- **Category:** contrib
- **Source:** §3.2 Contrib Modules
- **Tags:** `postgres`, `full-text-search`, `arrayfield`

## Canonical pattern (Django / HTMX / Hyperscript way)
django.contrib.postgres adds ArrayField, HStoreField, enhanced JSONField lookups, full-text search (SearchVector, SearchQuery, SearchRank), and trigram similarity - only usable with a PostgreSQL backend.

## Typical MVC default (what AI typically generates)
Typical MVC ORMs have no typed array/hstore fields; AI writes raw JSON-path WHERE queries or installs an external full-text search service before checking database-native search.

## Why Django differs
Django exposes Postgres power features as first-class ORM fields and expressions. Built-in full-text search covers most app search needs without an external search service, and ArrayField/JSONField keep schemas typed and queryable.

## Example
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
qs = (Product.objects
      .annotate(rank=SearchRank(SearchVector('name', 'description'),
                                SearchQuery(query)))
      .filter(rank__gt=0.1).order_by('-rank'))

# model field
from django.contrib.postgres.fields import ArrayField
tags = ArrayField(models.CharField(max_length=50), default=list)
