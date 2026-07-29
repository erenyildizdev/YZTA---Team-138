import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.debug import sensitive_variables

from .models import AuthCode


EMAIL_CONTENT_BY_PURPOSE = {
    AuthCode.Purpose.EMAIL_VERIFICATION: (
        "E-posta adresinizi doğrulayın",
        "users/emails/email_verification.txt",
    ),
    AuthCode.Purpose.PASSWORD_RESET: (
        "Parola sıfırlama kodunuz",
        "users/emails/password_reset.txt",
    ),
}


class AuthCodeEmailDeliveryError(RuntimeError):
    pass


def generate_auth_code():
    return f"{secrets.randbelow(1_000_000):06d}"


def _validate_purpose(purpose):
    if purpose not in AuthCode.Purpose.values:
        raise ValueError("Unsupported authentication code purpose.")


def _lock_user(user):
    user_model = get_user_model()
    return user_model._default_manager.select_for_update().get(pk=user.pk)


def _get_unconsumed_code(user, purpose):
    return (
        AuthCode.objects.select_for_update()
        .filter(
            user=user,
            purpose=purpose,
            consumed_at__isnull=True,
        )
        .order_by("-created_at", "-pk")
        .first()
    )


def _get_latest_code(user, purpose):
    return (
        AuthCode.objects.select_for_update()
        .filter(user=user, purpose=purpose)
        .order_by("-created_at", "-pk")
        .first()
    )


def _user_is_eligible_for_code(user, purpose):
    if purpose == AuthCode.Purpose.EMAIL_VERIFICATION:
        return user.is_active and not user.is_email_verified
    return user.is_active and user.is_email_verified


@sensitive_variables()
def send_auth_code_email(user, purpose, raw_code):
    _validate_purpose(purpose)
    if not user.email:
        raise AuthCodeEmailDeliveryError(
            "Authentication code email recipient is unavailable."
        )

    subject, template_name = EMAIL_CONTENT_BY_PURPOSE[purpose]
    message = render_to_string(
        template_name,
        {
            "code": raw_code,
            "ttl_minutes": settings.AUTH_CODE_TTL_MINUTES,
        },
    ).strip()
    sent_count = send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    if sent_count != 1:
        raise AuthCodeEmailDeliveryError(
            "Authentication code email could not be delivered."
        )


@sensitive_variables()
def issue_auth_code(user, purpose):
    _validate_purpose(purpose)

    with transaction.atomic():
        locked_user = _lock_user(user)
        if not _user_is_eligible_for_code(locked_user, purpose):
            return False

        latest_code = _get_latest_code(locked_user, purpose)
        current_code = _get_unconsumed_code(locked_user, purpose)
        now = timezone.now()

        if latest_code is not None and now < latest_code.resend_available_at:
            return False

        raw_code = generate_auth_code()
        if current_code is not None:
            current_code.consumed_at = now
            current_code.save(update_fields=["consumed_at", "updated_at"])

        AuthCode.objects.create(
            user=locked_user,
            purpose=purpose,
            code_hash=make_password(raw_code),
            expires_at=now
            + timedelta(minutes=settings.AUTH_CODE_TTL_MINUTES),
            resend_available_at=now
            + timedelta(
                seconds=settings.AUTH_CODE_RESEND_COOLDOWN_SECONDS
            ),
        )
        send_auth_code_email(locked_user, purpose, raw_code)

    return True


@sensitive_variables()
def _check_locked_code(auth_code, raw_code, now):
    if auth_code is None:
        return False
    if auth_code.expires_at <= now:
        return False
    if auth_code.failed_attempts >= settings.AUTH_CODE_MAX_ATTEMPTS:
        return False
    if not isinstance(raw_code, str) or not check_password(
        raw_code,
        auth_code.code_hash,
    ):
        auth_code.failed_attempts += 1
        auth_code.save(update_fields=["failed_attempts", "updated_at"])
        return False
    return True


@sensitive_variables()
def verify_email_code(user, raw_code):
    with transaction.atomic():
        locked_user = _lock_user(user)
        if locked_user.is_email_verified:
            return False

        auth_code = _get_unconsumed_code(
            locked_user,
            AuthCode.Purpose.EMAIL_VERIFICATION,
        )
        now = timezone.now()
        if not _check_locked_code(auth_code, raw_code, now):
            return False

        locked_user.is_email_verified = True
        locked_user.save(update_fields=["is_email_verified"])
        auth_code.consumed_at = now
        auth_code.save(update_fields=["consumed_at", "updated_at"])

    return True


@sensitive_variables()
def reset_password_with_code(user, raw_code, new_password):
    with transaction.atomic():
        locked_user = _lock_user(user)
        if not (
            locked_user.is_active and locked_user.is_email_verified
        ):
            return False

        auth_code = _get_unconsumed_code(
            locked_user,
            AuthCode.Purpose.PASSWORD_RESET,
        )
        now = timezone.now()
        if not _check_locked_code(auth_code, raw_code, now):
            return False

        password_validation.validate_password(
            new_password,
            user=locked_user,
        )
        locked_user.set_password(new_password)
        locked_user.save(update_fields=["password"])
        auth_code.consumed_at = now
        auth_code.save(update_fields=["consumed_at", "updated_at"])

    return True
