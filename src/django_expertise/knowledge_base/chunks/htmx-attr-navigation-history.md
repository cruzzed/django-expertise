# Navigation and history: hx-boost, hx-push-url, hx-history-elt, hx-preserve, hx-disable, hx-encoding, hx-ext, hx-on:*

- **ID:** `htmx-attr-navigation-history`
- **Category:** htmx-attribute
- **Source:** §4.1 Core Attribute Reference, A-009
- **Tags:** `hx-boost`, `hx-push-url`, `history`, `progressive-enhancement`

## Canonical pattern (Django / HTMX / Hyperscript way)
hx-boost='true' turns ordinary links/forms into AJAX navigations for SPA-like feel while keeping Django's server-side routing (anti-pattern A-009 forbids client-side routers). hx-push-url updates the browser URL; hx-history-elt picks the element snapshotted for history restores; hx-preserve keeps an element across swaps; hx-encoding='multipart/form-data' for file uploads; hx-ext loads extensions; hx-on:* binds inline event handlers (Phase 1).

## Laravel / MVC default (what AI typically generates)
React SPA default: react-router with client-side routes plus a JSON API, history managed by the router library, forms handled with controlled components and preventDefault.

## Why Django differs
Django already has a URL resolver, back-button semantics via the browser, and form handling - hx-boost composes with them instead of replacing them. The app works without JS (links still navigate), which is the graceful-degradation gate; a client router breaks that contract.

## Example
<body hx-boost="true" hx-history-elt="#main">
  <main id="main">{% block content %}{% endblock %}</main>
</body>

<form hx-post="{% url 'document-upload' %}" hx-encoding="multipart/form-data" hx-target="#result">
  <input type="file" name="document">
  <button>Upload</button>
</form>
<div hx-preserve id="video-player">...</div>
