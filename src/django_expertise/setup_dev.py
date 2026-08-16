"""Development environment setup helpers for agent-driven Django projects.

These tools are intentionally small wrappers around Django management commands
and models so agents can bootstrap a working local environment without
interactive prompts.
"""

from __future__ import annotations

import getpass
import re
from pathlib import Path


def setup_devuser(
    username: str,
    email: str,
    password: str,
    *,
    dev_mode: bool = False,
    is_staff: bool = True,
    is_superuser: bool = True,
) -> dict:
    """Create a local dev user non-interactively.

    Insecure passwords are only allowed when `dev_mode=True`.
    """
    if not dev_mode and _is_insecure_password(password):
        raise RuntimeError(
            "Password is too weak for non-dev-mode use. "
            "Pass --dev-mode to allow insecure local passwords, or choose a stronger password."
        )

    from django_expertise._django import ensure_django_setup

    ensure_django_setup()

    try:
        from django.contrib.auth import get_user_model
    except ImportError as exc:
        raise RuntimeError("Django must be installed to create a dev user") from exc

    User = get_user_model()
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email, "is_staff": is_staff, "is_superuser": is_superuser},
    )
    if not created:
        user.email = email
        user.is_staff = is_staff
        user.is_superuser = is_superuser
    user.set_password(password)
    user.save()

    return {
        "username": username,
        "email": email,
        "created": created,
        "is_superuser": is_superuser,
    }


def _is_insecure_password(password: str) -> bool:
    # Minimal check: length and variety.
    if len(password) < 10:
        return True
    if not re.search(r"[A-Z]", password):
        return True
    if not re.search(r"[a-z]", password):
        return True
    if not re.search(r"[0-9]", password):
        return True
    return False


def seed_fixtures(app_label: str | None = None, fixture_path: str | None = None) -> dict:
    """Load fixture data into the Django database.

    If `fixture_path` is provided, it is passed to `loaddata`. Otherwise,
    the function looks for fixtures named `<app_label>/fixtures/sample.json`
    or `<app_label>/fixtures/seed.json`.
    """
    from django_expertise._django import ensure_django_setup

    ensure_django_setup()

    try:
        from django.core.management import call_command
    except ImportError as exc:
        raise RuntimeError("Django must be installed to load fixtures") from exc

    if fixture_path:
        call_command("loaddata", fixture_path)
        return {"loaded": [fixture_path]}

    if app_label is None:
        raise ValueError("Either app_label or fixture_path is required")

    candidates = [
        f"{app_label}/fixtures/seed.json",
        f"{app_label}/fixtures/sample.json",
        f"{app_label}/fixtures/demo.json",
    ]
    loaded = []
    for candidate in candidates:
        if (Path.cwd() / candidate).exists():
            call_command("loaddata", candidate)
            loaded.append(candidate)

    if not loaded:
        raise RuntimeError(
            f"No seed fixture found for app '{app_label}'. "
            f"Searched: {', '.join(candidates)}"
        )

    return {"loaded": loaded}


def generate_fixture_template(app_label: str) -> str:
    """Generate an empty fixture template file for an app."""
    fixture_dir = Path.cwd() / app_label / "fixtures"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    fixture_path = fixture_dir / "seed.json"
    fixture_path.write_text("[\n]\n")
    return str(fixture_path)
