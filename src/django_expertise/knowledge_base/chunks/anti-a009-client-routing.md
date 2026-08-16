# A-009: Client-side routing for internal apps

- **ID:** `anti-a009-client-routing`
- **Category:** anti-pattern
- **Source:** §7 A-009
- **Tags:** `routing`, `hx-boost`, `anti-pattern`, `spa`

## Canonical pattern (Django / HTMX / Hyperscript way)
hx-boost='true' on links/forms for SPA-like navigation while Django's URL resolver, {% url %} tags, and server-rendered pages remain the routing system. hx-push-url keeps history honest.

## Typical MVC default (what AI typically generates)
A client-side router SPA with a JSON API backend (Django REST Framework) for an internal CRUD app - the AI default whenever 'dynamic UI' is requested.

## Why Django differs
A client router duplicates Django's routing, breaks the back button unless carefully managed, requires a whole JSON API, and fails without JS. hx-boost gets the perceived speed with server routing intact and graceful degradation free.

## Example
<!-- RIGHT -->
<body hx-boost="true" hx-history-elt="#main">
  <a href="{% url 'product-list' %}">Products</a>  <!-- boosted, still a real link -->
</body>

# WRONG: path('api/products/', ...) JSON + <Route path="/products"> ...
