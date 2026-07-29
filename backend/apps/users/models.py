from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_email_verified = models.BooleanField(default=True)


class AuthCode(models.Model):
    class Purpose(models.TextChoices):
        EMAIL_VERIFICATION = "email_verification", "E-posta doğrulama"
        PASSWORD_RESET = "password_reset", "Parola sıfırlama"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="auth_codes",
    )
    purpose = models.CharField(max_length=32, choices=Purpose.choices)
    code_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    failed_attempts = models.PositiveIntegerField(default=0)
    resend_available_at = models.DateTimeField()
    consumed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "purpose"),
                condition=models.Q(consumed_at__isnull=True),
                name="users_authcode_one_unconsumed_per_purpose",
            ),
            models.CheckConstraint(
                condition=models.Q(failed_attempts__gte=0),
                name="users_authcode_failed_attempts_nonnegative",
            ),
        ]
