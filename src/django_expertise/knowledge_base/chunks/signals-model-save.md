# pre_save / post_save (audit and cache only)

- **ID:** `signals-model-save`
- **Category:** signals
- **Source:** §3.3 Signals, A-001, A-008
- **Tags:** `signals`, `post_save`, `audit`

## Canonical pattern (Django / HTMX / Hyperscript way)
pre_save/post_save receivers are for framework-level concerns like audit logging - NOT emails, cache updates, or business side effects (anti-patterns A-001/A-008). Connect with @receiver(post_save, sender=Order) in a signals.py imported from AppConfig.ready().

## Typical MVC default (what AI typically generates)
Typical MVC ORMs offer model events/observers used liberally for sending mail and updating totals; AI routinely puts business side effects in model observers because mainstream MVC training data encourages it.

## Why Django differs
Django culture treats signals as hidden control flow: a post_save that emails users makes save() do surprising things, breaks in bulk operations, and is hard to debug. Explicit service-layer calls in the view keep the flow visible and testable.

## Example
# WRONG: sending email in post_save
# RIGHT: explicit service call
def order_create(request):
    form = OrderForm(request.POST)
    if form.is_valid():
        order = form.save()
        send_order_confirmation(order)   # explicit, visible, testable
        return redirect('order-detail', pk=order.pk)

# Legitimate signal use: audit logging
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Order)
def audit_order_save(sender, instance, created, **kwargs):
    AuditLog.objects.create(model='Order', object_id=instance.pk,
                            action='created' if created else 'updated')
