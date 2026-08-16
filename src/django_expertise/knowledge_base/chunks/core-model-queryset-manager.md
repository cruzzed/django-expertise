# models.Model, QuerySet, and custom Managers

- **ID:** `core-model-queryset-manager`
- **Category:** django-core
- **Source:** §3.1 Core Framework
- **Tags:** `model`, `queryset`, `manager`, `orm`

## Canonical pattern (Django / HTMX / Hyperscript way)
Models subclass django.db.models.Model and declare fields as class attributes. Queries are built with lazy QuerySets via Model.objects; reusable query logic is encapsulated in a custom Manager (e.g. Order.objects.pending()) rather than repeated in views.

## Typical MVC default (what AI typically generates)
Typical MVC ORMs use query scopes on the model or repository classes per entity. AI often generates a fat controller that filters inline, or a repository/service class per model as in typical MVC layering.

## Why Django differs
Django's QuerySet is lazy and composable, so Manager methods can chain and stay testable. Data integrity and business rules live on the model, keeping views thin - the Django MVT contract puts query encapsulation in Manager/Model, not a separate repository layer.

## Example
class OrderManager(models.Manager):
    def pending(self):
        return self.filter(status='pending').select_related('customer')

class Order(models.Model):
    status = models.CharField(max_length=20)
    objects = OrderManager()

# usage
orders = Order.objects.pending()
