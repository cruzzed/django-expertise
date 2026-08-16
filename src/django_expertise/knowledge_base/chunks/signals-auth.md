# user_logged_in / user_logged_out

- **ID:** `signals-auth`
- **Category:** signals
- **Source:** §3.3 Signals
- **Tags:** `signals`, `auth`, `analytics`

## Canonical pattern (Django / HTMX / Hyperscript way)
user_logged_in/user_logged_out (django.contrib.auth.signals, also user_login_failed) are the canonical hooks for session tracking and analytics: record last-IP, login counts, audit trails after authentication events.

## Typical MVC default (what AI typically generates)
Typical MVC frameworks use event listeners on auth login events, or override the login controller; AI often writes custom session-tracking middleware or stores analytics inline in the login view.

## Why Django differs
Django exposes auth lifecycle signals precisely so apps can observe authentication without subclassing the auth views. They are observer-friendly because authentication is a framework concern with no single explicit call site in your code.

## Example
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

@receiver(user_logged_in)
def track_login(sender, request, user, **kwargs):
    LoginEvent.objects.create(user=user, ip=request.META.get('REMOTE_ADDR'))
