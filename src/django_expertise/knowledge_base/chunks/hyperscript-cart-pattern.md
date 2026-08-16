# Full pattern: add-to-cart with visual feedback (§5.4)

- **ID:** `hyperscript-cart-pattern`
- **Category:** hyperscript
- **Source:** §5.4 Hyperscript + HTMX Event Integration
- **Tags:** `hyperscript`, `cart`, `htmx-events`, `feedback`

## Canonical pattern (Django / HTMX / Hyperscript way)
Button hx-posts to cart-add targeting #cart-sidebar (outerHTML). Hyperscript: on click store original label in :original, show 'Adding...'; on htmx:afterRequest restore, then on success flash .btn-success + 'Added ✓' for 2s and bounce #cart-icon, on error flash .btn-error. Variables (:original) keep per-element state without JS closures.

## Typical MVC default (what AI typically generates)
SPA-trained AI: an isAdding/isAdded state machine per product card with state hooks, setTimeout cleanup in an effect hook, and a cart context provider re-rendering the icon. Server-component default: wire-style loading attributes.

## Why Django differs
Per-element hyperscript variables (:original) scope state to the DOM node - no global store. The cart sidebar re-renders server-side via the hx-swap, so client and server never disagree about cart contents (contrast A-011 client-side state).

## Example
<button id="add-to-cart-{{ product.id }}" class="btn btn-primary"
  hx-post="{% url 'cart-add' product.id %}" hx-target="#cart-sidebar" hx-swap="outerHTML"
  _="on click
       add .loading to me
       set :original to my innerText
       put 'Adding...' into me
     end
     on htmx:afterRequest
       remove .loading from me
       put :original into me
       if event.detail.successful
         add .btn-success to me
         put 'Added ✓' into me
         wait 2s
         remove .btn-success from me
         put :original into me
         add .bounce to #cart-icon
         wait 300ms
         remove .bounce from #cart-icon
       else
         add .btn-error to me
         put 'Failed' into me
         wait 2s
         remove .btn-error from me
         put :original into me
       end
     end">
  Add to Cart
</button>
