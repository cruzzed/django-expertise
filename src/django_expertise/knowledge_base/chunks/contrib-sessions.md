# django.contrib.sessions (server-side sessions)

- **ID:** `contrib-sessions`
- **Category:** contrib
- **Source:** §3.2 Contrib Modules, A-011
- **Tags:** `sessions`, `state`, `cart`

## Canonical pattern (Django / HTMX / Hyperscript way)
django.contrib.sessions stores per-visitor state server-side, accessed as request.session (dict-like: request.session['cart_id'] = id). Use it for carts, wizard state, and flash-like data instead of stuffing state into hx-vals or hidden DOM attributes (spec A-011).

## Typical MVC default (what AI typically generates)
Typical MVC frameworks use a session helper, or - for SPA-minded AI - client-side state in localStorage / a JS store / JSON hidden inputs. AI trained on SPA frameworks keeps cart state in the browser and posts it back.

## Why Django differs
Django sessions keep authoritative state on the server (DB/cache backend), which is secure and survives DOM swaps. HTMX re-renders server HTML, so client-side state is fragile and a tampering risk - the server session is the single source of truth.

## Example
def add_to_cart(request, product_id):
    cart = request.session.setdefault('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session.modified = True
    return render(request, 'cart/_sidebar.html', {'cart': cart})
