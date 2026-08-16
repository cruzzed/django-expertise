# django.contrib.auth (full authentication stack)

- **ID:** `contrib-auth`
- **Category:** contrib
- **Source:** §3.2 Contrib Modules, §2.1 Decision Tree
- **Tags:** `auth`, `login`, `batteries`

## Canonical pattern (Django / HTMX / Hyperscript way)
django.contrib.auth ships User, Group, Permission, session-based login/logout views (django.contrib.auth.views.LoginView), password validators and password-reset flows. Enable it plus its URLs instead of building or buying auth.

## Typical MVC default (what AI typically generates)
Typical MVC frameworks ship scaffolded auth starter kits, or - very commonly - AI installs a JWT token-auth package even for a server-rendered app. AI defaults to JWT libraries or hand-rolled OAuth2 per the spec's decision tree.

## Why Django differs
Django's session auth is production-grade out of the box (hashing, validators, reset emails, throttling hooks). JWT is unnecessary for HTMX apps where the browser already carries the session cookie - the decision tree says check the batteries first.

## Example
# urls.py
urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),  # login/logout/reset
]
# settings.py
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]
LOGIN_REDIRECT_URL = 'dashboard' 
