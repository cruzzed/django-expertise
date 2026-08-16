# settings access and AppConfig.ready()

- **ID:** `core-settings-appconfig`
- **Category:** django-core
- **Source:** §3.1 Core Framework
- **Tags:** `settings`, `appconfig`, `signals`

## Canonical pattern (Django / HTMX / Hyperscript way)
Read configuration via django.conf.settings (never import the project settings module directly). AppConfig.ready() in apps.py is the one-time initialization hook - the canonical (and only sanctioned) place to import signal receivers or warm registries.

## Typical MVC default (what AI typically generates)
Typical MVC frameworks use config helper functions plus service-provider boot methods; AI often hardcodes env reads (os.environ / env()) inline in views, or puts import-time side effects in models.py.

## Why Django differs
Importing the concrete settings module couples code to one project and breaks test overrides; django.conf.settings respects override_settings. AppConfig.ready() runs after all apps are loaded, avoiding the circular-import hazards of doing setup in models.py import time.

## Example
from django.conf import settings
page_size = getattr(settings, 'PAGE_SIZE', 20)

# apps.py
from django.apps import AppConfig
class MyAppConfig(AppConfig):
    name = 'myapp'
    def ready(self):
        import myapp.signals  # register receivers
