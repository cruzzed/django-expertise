# Permission and Group (RBAC primitives)

- **ID:** `core-auth-permissions-groups`
- **Category:** django-core
- **Source:** §3.1 Core Framework
- **Tags:** `auth`, `permissions`, `rbac`, `groups`

## Canonical pattern (Django / HTMX / Hyperscript way)
django.contrib.auth.models.Permission and Group provide row-level-ready RBAC: permissions are auto-created per model (add/change/delete/view) and can be checked with request.user.has_perm('app.action_model'); groups bundle permissions.

## Typical MVC default (what AI typically generates)
Typical MVC frameworks rely on third-party RBAC packages or hand-written gate/policy classes. AI reaches for a third-party RBAC package before checking whether the built-in Permission/Group machinery suffices.

## Why Django differs
Django ships RBAC as a battery: permissions integrate with the admin, mixins (PermissionRequiredMixin) and templates ({% perms %}). Rolling your own or adding a package duplicates a mature built-in.

## Example
from django.contrib.auth.models import Group, Permission
editors = Group.objects.create(name='editors')
editors.permissions.add(Permission.objects.get(codename='change_article'))

# in a view
if request.user.has_perm('blog.change_article'):
    ...
