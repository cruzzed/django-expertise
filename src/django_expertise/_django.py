"""Small Django lifecycle helper for CLI tools.

When django-expertise is invoked as an installed console script, the current
working directory is not automatically on ``sys.path`` the way it is when
running ``python manage.py``. This helper makes ``django.setup()`` behave the
same in both cases.
"""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_django_setup() -> None:
    """Add cwd to ``sys.path`` and initialize Django if it is not ready."""
    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    import django
    from django.apps import apps

    if not apps.ready:
        django.setup()
