# django.contrib.admin and ModelAdmin

- **ID:** `contrib-admin`
- **Category:** contrib
- **Source:** §3.2 Contrib Modules, A-005
- **Tags:** `admin`, `modeladmin`, `batteries`

## Canonical pattern (Django / HTMX / Hyperscript way)
Enable django.contrib.admin, register models with ModelAdmin subclasses configured via list_display, list_filter, search_fields, inlines, actions. Customize look with django-jazzmin/django-admin-interface before ever building a custom dashboard.

## Laravel / MVC default (what AI typically generates)
Laravel: install Nova/Filament or hand-roll a React/Vue admin panel with a JSON API. Rails: ActiveAdmin gem or custom scaffold controllers. AI frequently scaffolds an entire SPA CRUD admin because the Django admin 'looks bad'.

## Why Django differs
The admin is a flagship Django battery: permissions-aware CRUD with zero views written. Anti-pattern A-005 (reinventing the admin) exists precisely because AI defaults to building dashboards that ModelAdmin + theming already provides.

## Example
from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name',)
    actions = ['mark_discontinued']

    @admin.action(description="Mark discontinued")
    def mark_discontinued(self, request, queryset):
        queryset.update(discontinued=True)
