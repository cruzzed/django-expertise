# get_user_model(), AbstractUser, AbstractBaseUser

- **ID:** `core-custom-user-model`
- **Category:** django-core
- **Source:** §3.1 Core Framework
- **Tags:** `auth`, `user-model`, `customization`

## Canonical pattern (Django / HTMX / Hyperscript way)
Always reference the user model via django.contrib.auth.get_user_model() (or settings.AUTH_USER_MODEL in ForeignKeys). For simple extra fields extend AbstractUser once at project start, or add a OneToOne Profile; reserve AbstractBaseUser for a genuinely different authentication scheme.

## Typical MVC default (what AI typically generates)
Typical MVC frameworks ship scaffolded auth whose User model gets edited freely, or AI installs a JWT package. AI often jumps to AbstractBaseUser + full custom user for a couple of profile fields, or hardcodes from django.contrib.auth.models import User.

## Why Django differs
Django decouples the user model through the swappable AUTH_USER_MODEL setting; get_user_model() keeps code working when projects swap it. AbstractBaseUser forces you to reimplement authentication machinery - the spec's anti-pattern A-002.

## Example
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
User = get_user_model()

class CustomUser(AbstractUser):          # simple extra fields
    phone = models.CharField(max_length=20, blank=True)

class Profile(models.Model):             # or a profile
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
