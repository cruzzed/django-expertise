# A-008: Signals for cache invalidation

- **ID:** `anti-a008-signals-cache`
- **Category:** anti-pattern
- **Source:** §7 A-008
- **Tags:** `signals`, `cache`, `anti-pattern`

## Canonical pattern (Django / HTMX / Hyperscript way)
Invalidate caches explicitly in the model's save()/delete() overrides or in a service-layer function, right next to the mutation that requires it.

## Typical MVC default (what AI typically generates)
A post_save receiver calling cache.delete(...) (or a typical MVC model 'saved' event flushing cache tags) - chosen because it 'just works' without touching call sites.

## Why Django differs
Signal-driven invalidation races (receiver runs before transaction commit), fires on fixtures/bulk ops unexpectedly, and hides the cache dependency from anyone reading the mutation code. Explicit calls are atomic-adjacent and grep-able.

## Example
# RIGHT
class Product(models.Model):
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'product:{self.pk}')

# or in a service function
def update_product(product, data):
    product.price = data['price']; product.save()
    cache.delete(f'product:{product.pk}')
