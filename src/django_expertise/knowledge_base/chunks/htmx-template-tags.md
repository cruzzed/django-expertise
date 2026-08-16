# Custom template tags for HTMX (htmx_partial, hx_attrs)

- **ID:** `htmx-template-tags`
- **Category:** htmx-pattern
- **Source:** §4.4 HTMX Template Tags
- **Tags:** `htmx`, `template-tags`, `reverse`

## Canonical pattern (Django / HTMX / Hyperscript way)
Two custom tags (spec §4.4): an inclusion tag htmx_partial wrapping partial rendering with shared context, and a simple_tag hx_attrs that generates hx-get/hx-post/... attributes with URL resolution via reverse() - {% hx_attrs get=('task-update' task.id) target='#row' %}.

## Typical MVC default (what AI typically generates)
AI hardcodes hx-post='/tasks/5/update/' strings in every template (brittle when URLs change), or generates attribute markup in JS, or builds a mini frontend-routing table.

## Why Django differs
Generating hx-* attributes through reverse() keeps HTMX attributes as single-source-of-truth as {% url %} does. Central tags also enforce consistent attribute spelling across the project instead of copy-paste drift.

## Example
from django import template
from django.urls import reverse
register = template.Library()

@register.inclusion_tag('htmx/_partial_wrapper.html')
def htmx_partial(template_name, **kwargs):
    return {'template_name': template_name, 'context': kwargs}

@register.simple_tag(takes_context=True)
def hx_attrs(context, **kwargs):
    attrs = []
    for key, value in kwargs.items():
        if key in ('get', 'post', 'put', 'delete', 'patch'):
            url = reverse(value[0], args=value[1:]) if isinstance(value, tuple) else reverse(value)
            attrs.append(f'hx-{key}="{url}"')
        else:
            attrs.append(f'hx-{key}="{value}"')
    return ' '.join(attrs)
