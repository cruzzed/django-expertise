# A-011: State in hx-vals or data attributes

- **ID:** `anti-a011-client-state`
- **Category:** anti-pattern
- **Source:** §7 A-011
- **Tags:** `state`, `sessions`, `security`, `anti-pattern`

## Canonical pattern (Django / HTMX / Hyperscript way)
Keep authoritative state server-side: database rows or django.contrib.sessions (request.session). hx-vals only carries user inputs (sort choice, page number), never application state like cart contents or permissions.

## Typical MVC default (what AI typically generates)
Storing cart items / user role / draft state in data-* attributes, hidden inputs, or hx-vals JSON blobs posted back and forth - the SPA habit of client-side stores translated into HTML.

## Why Django differs
Client-held state is tamperable (users can edit attributes), desyncs from the database across tabs, and makes every request re-serialize the world. Server state in the DB/session is the single source of truth HTMX re-renders from.

## Example
# WRONG: cart smuggled through the client
<button hx-post="/cart/add/" hx-vals='js:{cart: JSON.stringify(cartState)}'>

# RIGHT: session-backed cart
def add_to_cart(request, product_id):
    cart = request.session.setdefault('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session.modified = True
    return render(request, 'cart/_sidebar.html', {'cart': cart})
