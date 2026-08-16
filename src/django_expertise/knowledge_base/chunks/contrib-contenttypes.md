# django.contrib.contenttypes (GenericForeignKey)

- **ID:** `contrib-contenttypes`
- **Category:** contrib
- **Source:** §3.2 Contrib Modules, A-015
- **Tags:** `contenttypes`, `generic-relations`

## Canonical pattern (Django / HTMX / Hyperscript way)
contenttypes enables generic relations via GenericForeignKey (content_type + object_id) for models that must attach to any other model (comments, tags, audit logs). Use sparingly: the spec lists GenericForeignKey as anti-pattern A-015 for routine modeling.

## Typical MVC default (what AI typically generates)
Typical MVC ORMs offer polymorphic relations (type/id column pairs) declared eagerly on models. AI reaches for polymorphic relations as the default for any flexible association.

## Why Django differs
Django warns that generic relations lose referential integrity at the DB level and cost extra queries. For ordinary modeling, concrete inheritance or a JSONField (spec A-015) is faster and simpler; reserve contenttypes for genuinely framework-level reuse (e.g. a comments app).

## Example
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class TaggedItem(models.Model):
    tag = models.SlugField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
