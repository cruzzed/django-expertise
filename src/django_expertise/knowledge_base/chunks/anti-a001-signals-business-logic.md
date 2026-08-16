# A-001: Signals for business logic

- **ID:** `anti-a001-signals-business-logic`
- **Category:** anti-pattern
- **Source:** §7 A-001
- **Tags:** `signals`, `anti-pattern`, `service-layer`

## Canonical pattern (Django / HTMX / Hyperscript way)
Explicit service-layer calls in views/forms: order = form.save(); send_order_confirmation(order). Signals only for framework-level hooks like audit logging.

## Typical MVC default (what AI typically generates)
Using post_save (or typical MVC model observers / after-save callbacks) to send emails, update caches, or trigger side effects - the AI default because mainstream MVC training data embraces model callbacks.

## Why Django differs
Hidden side effects make save() do surprising things, break in bulk operations and tests, and scatter business flow across receivers. Explicit calls keep control flow visible, debuggable, and testable.

## Example
# WRONG
@receiver(post_save, sender=Order)
def notify(sender, instance, created, **kwargs):
    send_email(instance)  # hidden side effect

# RIGHT
def place_order(request):
    if form.is_valid():
        order = form.save()
        send_order_confirmation(order)   # explicit
        return redirect('order-detail', pk=order.pk)
