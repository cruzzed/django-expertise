import sys
from pathlib import Path

import pytest
from django.apps import apps
from django.conf import settings

from django_expertise._django import ensure_django_setup


def _configure_minimal_django():
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY="test-secret-key",
            ROOT_URLCONF="tests.test_debug_request_urls",
            ALLOWED_HOSTS=["testserver", "localhost"],
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
            ],
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
        )


def test_ensure_django_setup_adds_cwd_and_initializes_django():
    """When invoked as an installed console script, cwd may not be on sys.path.

    ``manage.py`` adds the project directory to ``sys.path`` and then calls
    ``django.setup()``; our CLI tools must do both before using Django.
    """
    _configure_minimal_django()

    # Simulate a partially-initialized state: settings configured but apps not ready.
    # In normal operation this happens when DJANGO_SETTINGS_MODULE is set but
    # django.setup() has not been called.
    if apps.ready:
        pytest.skip("Django apps are already ready in this process")

    cwd = str(Path.cwd())
    # Ensure a clean starting state.
    if cwd in sys.path:
        sys.path.remove(cwd)

    ensure_django_setup()

    assert sys.path[0] == cwd
    assert apps.ready is True
