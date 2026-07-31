# django.contrib.redirects and django.contrib.flatpages

- **ID:** `contrib-redirects-flatpages`
- **Category:** contrib
- **Source:** §3.2 Contrib Modules
- **Tags:** `redirects`, `flatpages`, `batteries`

## Canonical pattern (Django / HTMX / Hyperscript way)
redirects stores old-path -> new-path pairs in the database, applied by RedirectFallbackMiddleware when no URL matches (legacy URL migration). flatpages serves simple database-editable static pages (About, Terms) via FlatpageFallbackMiddleware with a tiny template.

## Laravel / MVC default (what AI typically generates)
Laravel: hardcoded Route::redirect() entries piling up in routes/web.php, or a CMS package for three static pages. AI builds a whole pages CRUD or installs a CMS for an About page.

## Why Django differs
Django ships both as lightweight batteries: editors manage redirects and simple pages in the admin with zero code. Writing custom controllers/migrations for legacy redirects or static content is reinvention.

## Example
# settings.py
INSTALLED_APPS += ['django.contrib.redirects', 'django.contrib.flatpages',
                   'django.contrib.sites']
MIDDLEWARE += ['django.contrib.redirects.middleware.RedirectFallbackMiddleware',
               'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware']
SITE_ID = 1
# Then manage Redirect and FlatPage rows in the admin.
