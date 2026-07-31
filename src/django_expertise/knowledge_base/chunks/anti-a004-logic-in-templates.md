# A-004: Business logic in templates

- **ID:** `anti-a004-logic-in-templates`
- **Category:** anti-pattern
- **Source:** §7 A-004
- **Tags:** `templates`, `anti-pattern`, `mvt`

## Canonical pattern (Django / HTMX / Hyperscript way)
Templates are presentation-only: compute in model methods/properties (can_cancel, display_total), Manager methods, or View context; templates just render {{ }} and simple {% if %} on precomputed values.

## Laravel / MVC default (what AI typically generates)
Complex {% if %} chains and custom template tags doing database work - the equivalent of fat Blade templates with @php blocks and Eloquent queries inside views, which AI produces from Laravel training data.

## Why Django differs
Django's template language is deliberately limited (no arbitrary Python) to enforce the MVT boundary: logic in templates is untestable, un-cacheable, and hides queries. Model methods make the logic reusable across views, admin, and APIs.

## Example
# model
@property
def display_total(self):
    return f"${self.total:.2f}"
def can_cancel(self):
    return self.status in ('pending', 'processing')

# template
<p class="price">{{ product.display_total }}</p>
{% if product.can_cancel %}<button>Cancel</button>{% endif %}
