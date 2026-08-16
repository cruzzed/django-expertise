# path(), re_path(), include(), reverse(), resolve()

- **ID:** `core-url-routing`
- **Category:** django-core
- **Source:** §3.1 Core Framework
- **Tags:** `urls`, `routing`, `reverse`

## Canonical pattern (Django / HTMX / Hyperscript way)
Define URLs with path() (typed converters like <int:pk>, Django 2.0+), re_path() for regex edge cases, and include() with app_name for namespacing. reverse() builds URLs from names in Python; {% url %} does it in templates; resolve() maps a path back to its view.

## Typical MVC default (what AI typically generates)
Typical MVC frameworks declare routes in a central routes file with closure logic and named-route URL helpers, or resource-style route declarations. AI often hardcodes URL strings like '/products/5/' in views and templates instead of reversing by name.

## Why Django differs
Django's named-URL + reverse() system makes URLs single-source-of-truth: changing a path breaks nothing that references it by name. Hardcoded paths (common in AI output) silently rot when routes change and defeat HTMX patterns that embed {% url %} in attributes.

## Example
# urls.py
app_name = 'products'
urlpatterns = [
    path('', ProductListView.as_view(), name='list'),
    path('<int:pk>/', product_detail, name='detail'),
]

# view
from django.urls import reverse
url = reverse('products:detail', args=[product.pk])
# template: {% url 'products:detail' product.pk %}
