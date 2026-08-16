import django
import pytest
from django.conf import settings

from django_expertise.debug import request


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
        django.setup()


def test_analyze_request_calls_django_setup():
    """analyze_request should call django.setup() when settings are not yet configured."""
    # Ensure a fresh state for this test.
    if settings.configured:
        pytest.skip("Django is already configured in this process")

    _configure_minimal_django()
    analysis = request.analyze_request("/")
    assert analysis.status_code == 200
    assert analysis.content_type == "text/html; charset=utf-8"


def test_analyze_request_returns_200_for_root():
    _configure_minimal_django()
    analysis = request.analyze_request("/")
    assert analysis.url == "/"
    assert analysis.status_code == 200
    assert analysis.is_htmx is False
