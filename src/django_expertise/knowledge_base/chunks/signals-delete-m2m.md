# pre_delete / post_delete and m2m_changed

- **ID:** `signals-delete-m2m`
- **Category:** signals
- **Source:** §3.3 Signals
- **Tags:** `signals`, `post_delete`, `m2m_changed`

## Canonical pattern (Django / HTMX / Hyperscript way)
pre_delete/post_delete suit cascade cleanup like deleting files from storage after the row goes away. m2m_changed (with action in pre_add/post_add/pre_remove/post_remove/pre_clear/post_clear) tracks many-to-many membership changes.

## Typical MVC default (what AI typically generates)
Typical MVC ORMs fire deleting/deleted model events and pivot sync observers; AI often uses these events to trigger business logic (notifications on tag changes) rather than purely mechanical cleanup.

## Why Django differs
Django sanctions these signals for resource hygiene (removing an uploaded file whose row was deleted) where there is no natural explicit call site. Business rules triggered by membership changes belong in the service layer, not the receiver.

## Example
from django.db.models.signals import post_delete, m2m_changed
from django.dispatch import receiver

@receiver(post_delete, sender=Document)
def delete_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)

@receiver(m2m_changed, sender=Product.tags.through)
def tags_changed(sender, instance, action, **kwargs):
    if action == 'post_add':
        instance.search_dirty = True
        instance.save(update_fields=['search_dirty'])
