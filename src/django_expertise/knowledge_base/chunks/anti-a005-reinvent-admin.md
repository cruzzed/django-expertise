# A-005: Reinventing the admin

- **ID:** `anti-a005-reinvent-admin`
- **Category:** anti-pattern
- **Source:** §7 A-005
- **Tags:** `admin`, `anti-pattern`, `batteries`

## Canonical pattern (Django / HTMX / Hyperscript way)
Customize ModelAdmin (list_display, inlines, actions) and reskin with django-jazzmin or django-admin-interface before writing any custom dashboard.

## Laravel / MVC default (what AI typically generates)
Building a React admin panel or hand-rolled CRUD controllers (Laravel: Nova/Filament or custom controllers) because 'the admin looks bad' - weeks of work duplicating built-in CRUD.

## Why Django differs
django.contrib.admin already provides permission-aware CRUD, search, filters, and bulk actions. Custom dashboards reinvent them poorly; theming solves the aesthetics complaint at 1% of the cost.

## Example
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name',)
# + pip install django-jazzmin for a modern skin
