"""Minimal Django configuration for observer tests."""

import os

import django
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

settings.configure(
    DEBUG=True,
    ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"],
    DATABASES={
        "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
    },
    INSTALLED_APPS=[
        "django.contrib.contenttypes",
        "django.contrib.auth",
    ],
    MIDDLEWARE=[
        "django_expertise.debug.observer.AgentObservationMiddleware",
        "django.middleware.common.CommonMiddleware",
    ],
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [os.path.join(BASE_DIR, "tests", "templates")],
            "APP_DIRS": True,
            "OPTIONS": {"context_processors": []},
        }
    ],
    ROOT_URLCONF="tests.test_debug_observer",
    SECRET_KEY="test-secret-key-for-prototype",
    USE_TZ=True,
)

django.setup()
