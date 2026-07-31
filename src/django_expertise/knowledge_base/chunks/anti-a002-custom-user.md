# A-002: Custom User model without need

- **ID:** `anti-a002-custom-user`
- **Category:** anti-pattern
- **Source:** §7 A-002
- **Tags:** `auth`, `anti-pattern`, `user-model`

## Canonical pattern (Django / HTMX / Hyperscript way)
Extend AbstractUser for simple extra fields, add a OneToOne Profile model, or use a JSONField. If customizing, do it at project start and reference via get_user_model().

## Laravel / MVC default (what AI typically generates)
Extending AbstractBaseUser with a full custom user (custom password hashing, USERNAME_FIELD, user manager) just to add a phone number - or bolting on a JWT auth package.

## Why Django differs
AbstractBaseUser forces reimplementing authentication machinery and complicates migrations for zero benefit on simple profile fields. Profile models keep auth stock and profile data freely evolvable.

## Example
# RIGHT: simple extension
class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)

# or even simpler - profile model
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
