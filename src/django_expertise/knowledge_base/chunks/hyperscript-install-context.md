# Hyperscript installation and Django template context

- **ID:** `hyperscript-install-context`
- **Category:** hyperscript
- **Source:** §5.1 Installation, §5.2 Hyperscript + Django Context
- **Tags:** `hyperscript`, `installation`, `django-context`

## Canonical pattern (Django / HTMX / Hyperscript way)
Load hyperscript 0.9.12 via a CDN script tag in the base template after HTMX; interactivity lives in the _ attribute. Django template variables render inside hyperscript ({{ cart.item_count }}), and htmx events are listenable: on htmx:afterRequest from #add-to-cart.

## Laravel / MVC default (what AI typically generates)
AI defaults to a bundled npm dependency + a framework (Alpine.js x-data, Stimulus controllers, or React) and passes server data through data-* attributes or JSON <script> islands parsed in JS.

## Why Django differs
Hyperscript is a single script tag with zero build step - matching Django's no-Node philosophy. Because Django templates render server-side, values interpolate directly into the _ attribute at render time; no hydration or JSON bootstrapping needed.

## Example
<!-- base.html -->
<script src="https://unpkg.com/hyperscript.org@0.9.12"></script>

<div id="cart-count"
     _="on htmx:afterRequest from #add-to-cart
          put {{ cart.item_count }} into me
          add .pulse to me
          wait 500ms
          remove .pulse from me
        end">
  {{ cart.item_count }}
</div>
