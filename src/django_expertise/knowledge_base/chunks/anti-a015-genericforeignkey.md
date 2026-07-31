# A-015: Using GenericForeignKey for routine modeling

- **ID:** `anti-a015-genericforeignkey`
- **Category:** anti-pattern
- **Source:** §7 A-015
- **Tags:** `contenttypes`, `anti-pattern`, `modeling`

## Canonical pattern (Django / HTMX / Hyperscript way)
Prefer concrete model inheritance (multi-table or abstract base classes) or a JSONField for flexible payloads; reserve contenttypes/GenericForeignKey for framework-level reuse like a generic comments app.

## Laravel / MVC default (what AI typically generates)
Laravel morphTo polymorphic relations (commentable_type/commentable_id) as the default for any flexible association - AI mirrors this with GenericForeignKey.

## Why Django differs
GenericForeignKey has no database-level FK constraint, can't be select_related'd generically, and adds a ContentType join per lookup - performance and integrity costs the spec deems unjustified for ordinary modeling.

## Example
# RIGHT: concrete relation
class Comment(models.Model):
    article = models.ForeignKey('Article', on_delete=models.CASCADE,
                                related_name='comments')

# RIGHT: flexible payload without relations
class Event(models.Model):
    payload = models.JSONField(default=dict)

# GFK only when building a reusable app across unknown models
