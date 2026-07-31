# django.contrib.staticfiles

- **ID:** `contrib-staticfiles`
- **Category:** contrib
- **Source:** §3.2 Contrib Modules, §5.1
- **Tags:** `staticfiles`, `assets`

## Canonical pattern (Django / HTMX / Hyperscript way)
django.contrib.staticfiles collects and serves CSS/JS/images. Reference assets in templates with {% load static %} and {% static 'app/site.css' %}; run collectstatic for production. Serve htmx/hyperscript via CDN script tags or static files in the base template.

## Laravel / MVC default (what AI typically generates)
Laravel: Vite/Mix asset pipeline with npm build step and compiled bundles; AI often sets up a full npm/webpack toolchain even for two <script> tags, or hardcodes /static/ paths instead of using the static tag.

## Why Django differs
Django's staticfiles app handles the common case (a handful of server-side JS libraries) without any Node toolchain. The {% static %} tag abstracts the URL so cache-busting/storage backends (e.g. ManifestStaticFilesStorage) work transparently.

## Example
{% load static %}
<script src="{% static 'vendor/htmx.min.js' %}"></script>
<script src="https://unpkg.com/hyperscript.org@0.9.12"></script>
<link rel="stylesheet" href="{% static 'css/app.css' %}">
