# A-007: Putting all logic in views

- **ID:** `anti-a007-fat-views`
- **Category:** anti-pattern
- **Source:** §7 A-007
- **Tags:** `views`, `anti-pattern`, `service-layer`, `mvt`

## Canonical pattern (Django / HTMX / Hyperscript way)
Push business rules into model methods (order.cancel()), query logic into Managers, and cross-model orchestration into a service layer; views orchestrate request/response and template selection only.

## Laravel / MVC default (what AI typically generates)
Fat controllers: a 100-line Laravel controller method doing validation, business rules, emails, and redirects - or an MVC 'thin model, fat controller' style that AI generates by default.

## Why Django differs
Django MVT gives every concern a home: models own integrity/rules, views own orchestration, templates own presentation. Bloated views are untestable and duplicate logic across endpoints; model methods are reusable from admin, shell, and other views.

## Example
# WRONG: rules in the view
def cancel_order_view(request, pk):
    order = Order.objects.get(pk=pk)
    if order.status in ('pending', 'processing'):
        order.status = 'cancelled'; order.save()

# RIGHT
class Order(models.Model):
    def cancel(self):
        if not self.can_cancel():
            raise ValidationError("Cannot cancel this order")
        self.status = 'cancelled'; self.save()

def cancel_order_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.cancel()
    return redirect('order-list')
