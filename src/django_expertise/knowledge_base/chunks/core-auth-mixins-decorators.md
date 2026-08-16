# login_required and CBV access mixins

- **ID:** `core-auth-mixins-decorators`
- **Category:** django-core
- **Source:** §3.1 Core Framework
- **Tags:** `auth`, `mixins`, `login_required`, `cbv`

## Canonical pattern (Django / HTMX / Hyperscript way)
Use @login_required for FBVs and LoginRequiredMixin / PermissionRequiredMixin / UserPassesTestMixin for CBVs. LoginRequiredMixin MUST be the first class in the MRO: class MyView(LoginRequiredMixin, ListView).

## Typical MVC default (what AI typically generates)
Typical MVC frameworks attach auth middleware to routes or call authorize hooks inside controller methods. AI often writes middleware-style route config or forgets mixin ordering, producing a view that ignores the check.

## Why Django differs
Django enforces access at the view class level via cooperative multiple inheritance. Mixin order matters because dispatch() resolution follows the MRO - putting LoginRequiredMixin after ListView silently skips authentication.

## Example
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

@login_required
def dashboard(request): ...

class ProductListView(LoginRequiredMixin, ListView):  # mixin FIRST
    model = Product

class EditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'shop.change_product'
    model = Product
