# Caching: cache_page, cached_property, lru_cache

- **ID:** `core-caching-memoization`
- **Category:** django-core
- **Source:** §3.1 Core Framework
- **Tags:** `cache`, `performance`, `cached_property`

## Canonical pattern (Django / HTMX / Hyperscript way)
Per-view caching with @cache_page(60*15) from django.views.decorators.cache; per-instance method memoization with django.utils.functional.cached_property; pure-function memoization with functools.lru_cache. Reach for django.core.cache for explicit get/set.

## Laravel / MVC default (what AI typically generates)
Laravel: Cache::remember('key', 900, fn() => ...) everywhere or Redis facades; AI frequently installs a Redis wrapper package before considering the built-in cache framework, or memoizes nothing and recomputes per request.

## Why Django differs
Django ships a layered cache framework (per-view, template-fragment, low-level, per-method). cached_property avoids repeated expensive computation within a request without any cache backend; picking the right layer is the Django way.

## Example
from django.views.decorators.cache import cache_page
from django.utils.functional import cached_property

@cache_page(60 * 15)
def report(request): ...

class Order(models.Model):
    @cached_property
    def expensive_total(self):
        return self.items.aggregate(t=Sum('price'))['t']
