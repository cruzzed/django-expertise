# django.contrib.humanize (natural-language template filters)

- **ID:** `contrib-humanize`
- **Category:** contrib
- **Source:** §3.2 Contrib Modules
- **Tags:** `humanize`, `template-filters`, `formatting`

## Canonical pattern (Django / HTMX / Hyperscript way)
Add 'django.contrib.humanize' to INSTALLED_APPS and {% load humanize %} to get filters like naturaltime, intcomma, ordinal, apnumber - formatting values the way humans read them without custom template tags.

## Laravel / MVC default (what AI typically generates)
Laravel: Carbon's diffForHumans() calls sprinkled in Blade, or custom helper functions. AI writes custom template filters or JS date libraries (moment.js/Day.js) for '3 days ago' formatting that humanize already provides.

## Why Django differs
Django ships display formatting as a battery because pushing presentation formatting into JS libraries contradicts server-rendered HTML. humanize keeps formatting in the template layer where MVT says presentation lives.

## Example
{% load humanize %}
<p>Created {{ task.created_at|naturaltime }}</p>
<p>{{ product.price|intcomma }} USD</p>
<p>You finished {{ place|ordinal }}.</p>
