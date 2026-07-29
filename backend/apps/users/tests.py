import re
import sys
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.core import mail
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import (
    SimpleTestCase,
    TransactionTestCase,
    override_settings,
)
from django.urls import reverse
from django.utils import timezone
from django.views.debug import ExceptionReporter
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .models import AuthCode
from .serializers import ChangePasswordSerializer
from .services import issue_auth_code
from .throttles import ScopedIPRateThrottle
from .views import ChangePasswordView


PROFILE_RESPONSE_KEYS = {"id", "email", "first_name", "last_name"}
LOC_MEM_EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
FAST_PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


def extract_auth_code(message):
    match = re.search(r"(?<![0-9])([0-9]{6})(?![0-9])", message.body)
    if not match:
        raise AssertionError("E-posta gövdesinde altı haneli kod bulunamadı.")
    return match.group(1)


class AuthEndpointsTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.register_url = reverse("users:register")
        self.login_url = reverse("users:login")
        self.user_model = get_user_model()

    @override_settings(
        EMAIL_BACKEND=LOC_MEM_EMAIL_BACKEND,
        PASSWORD_HASHERS=FAST_PASSWORD_HASHERS,
    )
    @patch("apps.users.services.generate_auth_code", return_value="004271")
    def test_register_creates_unverified_user_and_sends_hashed_code(
        self,
        generate_code,
    ):
        payload = {
            "email": "founder@example.com",
            "password": "StrongPass123!",
            "first_name": "Ada",
            "last_name": "Lovelace",
        }

        response = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            {
                "detail": (
                    "Hesabınız oluşturuldu. E-posta adresinize gönderilen "
                    "doğrulama kodunu girin."
                ),
                "email": "founder@example.com",
                "requires_email_verification": True,
            },
        )
        self.assertTrue(
            {
                "access_token",
                "refresh_token",
                "token",
                "user",
                "password",
                "code",
            }.isdisjoint(response.data)
        )

        user = self.user_model.objects.get(username="founder@example.com")
        self.assertEqual(user.email, "founder@example.com")
        self.assertEqual(user.first_name, payload["first_name"])
        self.assertEqual(user.last_name, payload["last_name"])
        self.assertFalse(user.is_email_verified)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["founder@example.com"])
        self.assertIn("doğrulayın", mail.outbox[0].subject)
        self.assertIn("10 dakika", mail.outbox[0].body)
        self.assertIn("dikkate almayın", mail.outbox[0].body)
        self.assertEqual(extract_auth_code(mail.outbox[0]), "004271")

        auth_code = AuthCode.objects.get(
            user=user,
            purpose=AuthCode.Purpose.EMAIL_VERIFICATION,
            consumed_at__isnull=True,
        )
        self.assertNotEqual(auth_code.code_hash, "004271")
        self.assertNotIn("004271", auth_code.code_hash)
        self.assertTrue(check_password("004271", auth_code.code_hash))
        self.assertEqual(auth_code.failed_attempts, 0)
        self.assertGreater(auth_code.expires_at, timezone.now())
        generate_code.assert_called_once_with()

        response_text = str(response.data)
        self.assertNotIn(payload["password"], response_text)
        self.assertNotIn("004271", response_text)

    @override_settings(
        EMAIL_BACKEND=LOC_MEM_EMAIL_BACKEND,
        PASSWORD_HASHERS=FAST_PASSWORD_HASHERS,
    )
    def test_duplicate_email_is_a_controlled_field_error(self):
        self.user_model.objects.create_user(
            username="founder@example.com",
            email="founder@example.com",
            password="ExistingStrongPass123!",
        )

        response = self.client.post(
            self.register_url,
            {
                "email": "FOUNDER@EXAMPLE.COM",
                "password": "StrongPass123!",
                "first_name": "Ada",
                "last_name": "Lovelace",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.data), {"email"})
        self.assertEqual(self.user_model.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(
        EMAIL_BACKEND=LOC_MEM_EMAIL_BACKEND,
        PASSWORD_HASHERS=FAST_PASSWORD_HASHERS,
    )
    @patch(
        "apps.users.services.send_mail",
        side_effect=RuntimeError("smtp-password=must-not-leak"),
    )
    def test_register_email_failure_rolls_back_and_returns_sanitized_503(
        self,
        send_mail,
    ):
        payload = {
            "email": "rollback@example.com",
            "password": "StrongPass123!",
            "first_name": "Rollback",
            "last_name": "User",
        }

        response = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        self.assertEqual(
            response.data,
            {
                "detail": (
                    "Kayıt şu anda tamamlanamadı. Lütfen daha sonra tekrar "
                    "deneyin."
                )
            },
        )
        self.assertFalse(
            self.user_model.objects.filter(
                username="rollback@example.com"
            ).exists()
        )
        self.assertEqual(AuthCode.objects.count(), 0)
        response_text = str(response.data)
        self.assertNotIn(payload["password"], response_text)
        self.assertNotIn("smtp-password", response_text)
        send_mail.assert_called_once()

    def test_register_requires_email_and_rejects_identifier_overflow(self):
        base_payload = {
            "password": "StrongPass123!",
            "first_name": "Ada",
            "last_name": "Lovelace",
        }

        missing_response = self.client.post(
            self.register_url,
            base_payload,
            format="json",
        )
        long_response = self.client.post(
            self.register_url,
            {
                **base_payload,
                "email": f"{'a' * 145}@x.com",
            },
            format="json",
        )

        self.assertEqual(
            missing_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            long_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("email", missing_response.data)
        self.assertIn("email", long_response.data)
        self.assertEqual(self.user_model.objects.count(), 0)

    def test_login_returns_tokens_for_valid_credentials(self):
        user = self.user_model.objects.create_user(
            username="tester@example.com",
            email="tester@example.com",
            password="StrongPass123!",
            first_name="Test",
            last_name="User",
        )
        self.assertTrue(user.is_email_verified)

        response = self.client.post(
            self.login_url,
            {"email": "tester@example.com", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data),
            {"access_token", "refresh_token", "user"},
        )
        self.assertEqual(set(response.data["user"]), PROFILE_RESPONSE_KEYS)
        self.assertEqual(response.data["user"]["id"], user.id)
        self.assertEqual(response.data["user"]["email"], user.email)
        self.assertEqual(response.data["user"]["first_name"], user.first_name)
        self.assertEqual(response.data["user"]["last_name"], user.last_name)
        self.assertNotIn("password", response.data["user"])
        access = AccessToken(response.data["access_token"])
        refresh = RefreshToken(response.data["refresh_token"])
        self.assertEqual(access["user_id"], str(user.id))
        self.assertEqual(refresh["user_id"], str(user.id))

    @override_settings(PASSWORD_HASHERS=FAST_PASSWORD_HASHERS)
    def test_unverified_user_with_valid_password_gets_stable_403_without_tokens(self):
        self.user_model.objects.create_user(
            username="pending@example.com",
            email="pending@example.com",
            password="StrongPass123!",
            is_email_verified=False,
        )

        response = self.client.post(
            self.login_url,
            {
                "email": "PENDING@EXAMPLE.COM",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data,
            {
                "detail": "E-posta adresinizi doğrulamanız gerekiyor.",
                "code": "email_not_verified",
                "email": "pending@example.com",
            },
        )
        self.assertTrue(
            {"access_token", "refresh_token", "token"}.isdisjoint(
                response.data
            )
        )

    @override_settings(PASSWORD_HASHERS=FAST_PASSWORD_HASHERS)
    def test_wrong_password_does_not_reveal_unverified_account_state(self):
        self.user_model.objects.create_user(
            username="pending@example.com",
            email="pending@example.com",
            password="StrongPass123!",
            is_email_verified=False,
        )

        pending_response = self.client.post(
            self.login_url,
            {
                "email": "pending@example.com",
                "password": "WrongStrongPass123!",
            },
            format="json",
        )
        missing_response = self.client.post(
            self.login_url,
            {
                "email": "missing@example.com",
                "password": "WrongStrongPass123!",
            },
            format="json",
        )

        self.assertEqual(
            pending_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            missing_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(pending_response.data, missing_response.data)
        self.assertEqual(
            pending_response.data,
            {"detail": ["Invalid email or password."]},
        )
        self.assertNotIn("email_not_verified", str(pending_response.data))


class AuthSettingsValidationTests(SimpleTestCase):
    @patch("config.settings.config", return_value=0)
    def test_positive_integer_settings_reject_zero(self, mocked_config):
        from config.settings import _positive_int_config

        with self.assertRaises(ImproperlyConfigured):
            _positive_int_config("AUTH_CODE_TTL_MINUTES", 10)
        mocked_config.assert_called_once()

    @patch("config.settings.config", return_value=1441)
    def test_policy_settings_reject_values_above_safe_maximum(
        self,
        mocked_config,
    ):
        from config.settings import _positive_int_config

        with self.assertRaises(ImproperlyConfigured):
            _positive_int_config(
                "AUTH_CODE_TTL_MINUTES",
                10,
                maximum=1440,
            )
        mocked_config.assert_called_once()

    @patch("config.settings.config", return_value="")
    def test_boolean_settings_reject_explicitly_empty_values(
        self,
        mocked_config,
    ):
        from config.settings import _boolean_config

        with self.assertRaises(ImproperlyConfigured):
            _boolean_config("EMAIL_USE_TLS", True)
        mocked_config.assert_called_once()


@override_settings(PASSWORD_HASHERS=FAST_PASSWORD_HASHERS)
class UserVerificationDefaultsTests(APITestCase):
    def test_generic_and_superuser_creation_are_verified_by_default(self):
        user_model = get_user_model()
        regular_user = user_model.objects.create_user(
            username="system@example.com",
            email="system@example.com",
            password="StrongPass123!",
        )
        superuser = user_model.objects.create_superuser(
            username="admin@example.com",
            email="admin@example.com",
            password="StrongPass123!",
        )

        self.assertTrue(regular_user.is_email_verified)
        self.assertTrue(superuser.is_email_verified)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)


class EmailVerificationMigrationTests(TransactionTestCase):
    migrate_from = [("users", "0001_initial")]
    migrate_to = [
        ("users", "0002_user_is_email_verified_authcode"),
    ]

    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps
        old_user_model = old_apps.get_model("users", "User")
        self.user_id = old_user_model.objects.create(
            username="existing@example.com",
            email="existing@example.com",
            password="historical-hash",
        ).pk

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        self.migrated_apps = executor.loader.project_state(
            self.migrate_to
        ).apps

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_existing_user_is_verified_when_additive_migration_runs(self):
        migrated_user_model = self.migrated_apps.get_model("users", "User")
        user = migrated_user_model.objects.get(pk=self.user_id)

        self.assertTrue(user.is_email_verified)


class AuthCodeEndpointMixin:
    def setUp(self):
        super().setUp()
        cache.clear()
        self.user_model = get_user_model()

    def create_user(
        self,
        email,
        *,
        verified=True,
        active=True,
        password="CurrentStrongPass123!",
        username=None,
    ):
        return self.user_model.objects.create_user(
            username=username or email.lower(),
            email=email.lower(),
            password=password,
            is_email_verified=verified,
            is_active=active,
        )

    def issue_code(self, user, purpose, raw_code):
        with patch(
            "apps.users.services.generate_auth_code",
            return_value=raw_code,
        ):
            sent = issue_auth_code(user, purpose)
        self.assertTrue(sent)
        return AuthCode.objects.get(
            user=user,
            purpose=purpose,
            consumed_at__isnull=True,
        )

    def elapse_cooldown(self, auth_code):
        auth_code.resend_available_at = timezone.now() - timedelta(seconds=1)
        auth_code.save(update_fields=["resend_available_at", "updated_at"])

    def expire_code(self, auth_code):
        auth_code.expires_at = timezone.now() - timedelta(seconds=1)
        auth_code.save(update_fields=["expires_at", "updated_at"])


@override_settings(
    EMAIL_BACKEND=LOC_MEM_EMAIL_BACKEND,
    PASSWORD_HASHERS=FAST_PASSWORD_HASHERS,
    AUTH_CODE_TTL_MINUTES=10,
    AUTH_CODE_RESEND_COOLDOWN_SECONDS=60,
    AUTH_CODE_MAX_ATTEMPTS=5,
)
class VerifyEmailEndpointTests(AuthCodeEndpointMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.verify_url = reverse("users:verify-email")

    def test_leading_zero_code_verifies_once_and_is_consumed(self):
        user = self.create_user("pending@example.com", verified=False)
        auth_code = self.issue_code(
            user,
            AuthCode.Purpose.EMAIL_VERIFICATION,
            "004271",
        )

        first_response = self.client.post(
            self.verify_url,
            {"email": "PENDING@EXAMPLE.COM", "code": "004271"},
            format="json",
        )
        replay_response = self.client.post(
            self.verify_url,
            {"email": "pending@example.com", "code": "004271"},
            format="json",
        )

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            first_response.data,
            {
                "detail": (
                    "E-posta adresiniz doğrulandı. Giriş yapabilirsiniz."
                )
            },
        )
        self.assertEqual(
            replay_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            replay_response.data,
            {
                "detail": (
                    "Doğrulama kodu geçersiz veya süresi dolmuş."
                )
            },
        )
        user.refresh_from_db()
        auth_code.refresh_from_db()
        self.assertTrue(user.is_email_verified)
        self.assertIsNotNone(auth_code.consumed_at)
        self.assertEqual(auth_code.failed_attempts, 0)

    def test_wrong_attempts_increment_and_lock_code_at_configured_maximum(self):
        user = self.create_user("pending@example.com", verified=False)
        auth_code = self.issue_code(
            user,
            AuthCode.Purpose.EMAIL_VERIFICATION,
            "123456",
        )

        for attempt in range(5):
            response = self.client.post(
                self.verify_url,
                {"email": user.email, "code": "999999"},
                format="json",
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
            )
            auth_code.refresh_from_db()
            self.assertEqual(auth_code.failed_attempts, attempt + 1)

        locked_response = self.client.post(
            self.verify_url,
            {"email": user.email, "code": "123456"},
            format="json",
        )
        self.assertEqual(
            locked_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        user.refresh_from_db()
        auth_code.refresh_from_db()
        self.assertFalse(user.is_email_verified)
        self.assertEqual(auth_code.failed_attempts, 5)
        self.assertIsNone(auth_code.consumed_at)

    def test_expired_code_is_rejected_without_verifying_user(self):
        user = self.create_user("expired@example.com", verified=False)
        auth_code = self.issue_code(
            user,
            AuthCode.Purpose.EMAIL_VERIFICATION,
            "123456",
        )
        self.expire_code(auth_code)

        response = self.client.post(
            self.verify_url,
            {"email": user.email, "code": "123456"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        auth_code.refresh_from_db()
        self.assertFalse(user.is_email_verified)
        self.assertEqual(auth_code.failed_attempts, 0)
        self.assertIsNone(auth_code.consumed_at)

    def test_code_from_another_purpose_is_rejected(self):
        user = self.create_user("purpose@example.com", verified=False)
        AuthCode.objects.create(
            user=user,
            purpose=AuthCode.Purpose.PASSWORD_RESET,
            code_hash=make_password("654321"),
            expires_at=timezone.now() + timedelta(minutes=10),
            resend_available_at=timezone.now() + timedelta(seconds=60),
        )

        response = self.client.post(
            self.verify_url,
            {"email": user.email, "code": "654321"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertFalse(user.is_email_verified)
        self.assertEqual(
            AuthCode.objects.get(
                user=user,
                purpose=AuthCode.Purpose.PASSWORD_RESET,
            ).failed_attempts,
            0,
        )

    def test_another_users_code_cannot_verify_target_user(self):
        target = self.create_user("target@example.com", verified=False)
        other = self.create_user("other@example.com", verified=False)
        target_code = self.issue_code(
            target,
            AuthCode.Purpose.EMAIL_VERIFICATION,
            "111111",
        )
        other_code = self.issue_code(
            other,
            AuthCode.Purpose.EMAIL_VERIFICATION,
            "222222",
        )

        response = self.client.post(
            self.verify_url,
            {"email": target.email, "code": "222222"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        target.refresh_from_db()
        other.refresh_from_db()
        target_code.refresh_from_db()
        other_code.refresh_from_db()
        self.assertFalse(target.is_email_verified)
        self.assertFalse(other.is_email_verified)
        self.assertEqual(target_code.failed_attempts, 1)
        self.assertEqual(other_code.failed_attempts, 0)

    def test_verified_or_missing_account_gets_generic_invalid_response(self):
        verified = self.create_user("verified@example.com")
        request_payloads = (
            {"email": verified.email, "code": "123456"},
            {"email": "missing@example.com", "code": "123456"},
        )

        responses = [
            self.client.post(self.verify_url, payload, format="json")
            for payload in request_payloads
        ]

        for response in responses:
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
            )
            self.assertEqual(
                response.data,
                {
                    "detail": (
                        "Doğrulama kodu geçersiz veya süresi dolmuş."
                    )
                },
            )
        verified.refresh_from_db()
        self.assertTrue(verified.is_email_verified)
        self.assertEqual(AuthCode.objects.count(), 0)

    def test_code_must_be_an_ascii_six_digit_json_string(self):
        user = self.create_user("strict@example.com", verified=False)
        auth_code = self.issue_code(
            user,
            AuthCode.Purpose.EMAIL_VERIFICATION,
            "123456",
        )

        invalid_codes = (123456, "12345", "１２３４５６", "12345a")
        for invalid_code in invalid_codes:
            with self.subTest(code=invalid_code):
                response = self.client.post(
                    self.verify_url,
                    {"email": user.email, "code": invalid_code},
                    format="json",
                )
                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertEqual(set(response.data), {"code"})

        auth_code.refresh_from_db()
        self.assertEqual(auth_code.failed_attempts, 0)
        self.assertIsNone(auth_code.consumed_at)


@override_settings(
    EMAIL_BACKEND=LOC_MEM_EMAIL_BACKEND,
    PASSWORD_HASHERS=FAST_PASSWORD_HASHERS,
    AUTH_CODE_TTL_MINUTES=10,
    AUTH_CODE_RESEND_COOLDOWN_SECONDS=60,
    AUTH_CODE_MAX_ATTEMPTS=5,
)
class ResendVerificationEndpointTests(AuthCodeEndpointMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.resend_url = reverse("users:resend-verification")
        self.verify_url = reverse("users:verify-email")
        self.generic_response = {
            "detail": (
                "E-posta adresi uygunsa yeni doğrulama kodu gönderildi."
            )
        }

    def test_cooldown_returns_generic_response_without_rotating_or_sending(self):
        user = self.create_user("pending@example.com", verified=False)
        auth_code = self.issue_code(
            user,
            AuthCode.Purpose.EMAIL_VERIFICATION,
            "111111",
        )
        original_hash = auth_code.code_hash

        response = self.client.post(
            self.resend_url,
            {"email": user.email},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.generic_response)
        auth_code.refresh_from_db()
        self.assertEqual(AuthCode.objects.count(), 1)
        self.assertEqual(auth_code.code_hash, original_hash)
        self.assertIsNone(auth_code.consumed_at)
        self.assertEqual(len(mail.outbox), 1)

    def test_resend_after_cooldown_rotates_code_and_invalidates_old_code(self):
        user = self.create_user("pending@example.com", verified=False)
        old_code = self.issue_code(
            user,
            AuthCode.Purpose.EMAIL_VERIFICATION,
            "111111",
        )
        self.elapse_cooldown(old_code)

        with patch(
            "apps.users.services.generate_auth_code",
            return_value="222222",
        ):
            response = self.client.post(
                self.resend_url,
                {"email": user.email},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.generic_response)
        old_code.refresh_from_db()
        new_code = AuthCode.objects.get(
            user=user,
            purpose=AuthCode.Purpose.EMAIL_VERIFICATION,
            consumed_at__isnull=True,
        )
        self.assertIsNotNone(old_code.consumed_at)
        self.assertNotEqual(old_code.pk, new_code.pk)
        self.assertTrue(check_password("222222", new_code.code_hash))
        self.assertFalse(check_password("111111", new_code.code_hash))
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(extract_auth_code(mail.outbox[-1]), "222222")

        old_response = self.client.post(
            self.verify_url,
            {"email": user.email, "code": "111111"},
            format="json",
        )
        new_response = self.client.post(
            self.verify_url,
            {"email": user.email, "code": "222222"},
            format="json",
        )
        self.assertEqual(
            old_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(new_response.status_code, status.HTTP_200_OK)

    def test_missing_and_verified_accounts_receive_same_generic_response(self):
        verified = self.create_user("verified@example.com")

        missing_response = self.client.post(
            self.resend_url,
            {"email": "missing@example.com"},
            format="json",
        )
        verified_response = self.client.post(
            self.resend_url,
            {"email": verified.email},
            format="json",
        )

        self.assertEqual(missing_response.status_code, status.HTTP_200_OK)
        self.assertEqual(verified_response.status_code, status.HTTP_200_OK)
        self.assertEqual(missing_response.data, self.generic_response)
        self.assertEqual(verified_response.data, self.generic_response)
        self.assertEqual(AuthCode.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_smtp_failure_preserves_previous_code_and_generic_response(self):
        user = self.create_user("pending@example.com", verified=False)
        old_code = self.issue_code(
            user,
            AuthCode.Purpose.EMAIL_VERIFICATION,
            "111111",
        )
        self.elapse_cooldown(old_code)
        original_hash = old_code.code_hash

        with (
            patch(
                "apps.users.services.generate_auth_code",
                return_value="222222",
            ),
            patch(
                "apps.users.services.send_mail",
                side_effect=RuntimeError("smtp-host-secret"),
            ),
        ):
            response = self.client.post(
                self.resend_url,
                {"email": user.email},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.generic_response)
        self.assertNotIn("smtp-host-secret", str(response.data))
        old_code.refresh_from_db()
        self.assertEqual(AuthCode.objects.count(), 1)
        self.assertEqual(old_code.code_hash, original_hash)
        self.assertIsNone(old_code.consumed_at)
        self.assertEqual(len(mail.outbox), 1)


@override_settings(
    EMAIL_BACKEND=LOC_MEM_EMAIL_BACKEND,
    PASSWORD_HASHERS=FAST_PASSWORD_HASHERS,
    AUTH_CODE_TTL_MINUTES=10,
    AUTH_CODE_RESEND_COOLDOWN_SECONDS=60,
    AUTH_CODE_MAX_ATTEMPTS=5,
)
class PasswordResetRequestEndpointTests(AuthCodeEndpointMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.request_url = reverse("users:password-reset-request")
        self.generic_response = {
            "detail": (
                "E-posta adresi uygunsa parola sıfırlama kodu gönderildi."
            )
        }

    @patch("apps.users.services.generate_auth_code", return_value="004271")
    def test_verified_active_user_receives_hashed_reset_code(self, generator):
        user = self.create_user("owner@example.com")

        response = self.client.post(
            self.request_url,
            {"email": "OWNER@EXAMPLE.COM"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.generic_response)
        self.assertNotIn("004271", str(response.data))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [user.email])
        self.assertIn("Parola sıfırlama", mail.outbox[0].subject)
        self.assertIn("10 dakika", mail.outbox[0].body)
        self.assertIn("dikkate almayın", mail.outbox[0].body)
        self.assertEqual(extract_auth_code(mail.outbox[0]), "004271")
        auth_code = AuthCode.objects.get(
            user=user,
            purpose=AuthCode.Purpose.PASSWORD_RESET,
            consumed_at__isnull=True,
        )
        self.assertNotEqual(auth_code.code_hash, "004271")
        self.assertTrue(check_password("004271", auth_code.code_hash))
        generator.assert_called_once_with()

    def test_missing_unverified_and_inactive_accounts_are_indistinguishable(self):
        unverified = self.create_user(
            "pending@example.com",
            verified=False,
        )
        inactive = self.create_user(
            "inactive@example.com",
            active=False,
        )
        emails = (
            "missing@example.com",
            unverified.email,
            inactive.email,
        )

        responses = [
            self.client.post(
                self.request_url,
                {"email": email},
                format="json",
            )
            for email in emails
        ]

        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, self.generic_response)
        self.assertEqual(AuthCode.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_lookup_uses_unique_canonical_username_not_nonunique_email(self):
        canonical = self.create_user("shared@example.com")
        distractor = self.create_user(
            "shared@example.com",
            username="different-identifier",
        )

        response = self.client.post(
            self.request_url,
            {"email": "SHARED@EXAMPLE.COM"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            AuthCode.objects.filter(
                user=canonical,
                purpose=AuthCode.Purpose.PASSWORD_RESET,
            ).exists()
        )
        self.assertFalse(
            AuthCode.objects.filter(user=distractor).exists()
        )

    def test_cooldown_suppresses_second_reset_email(self):
        user = self.create_user("owner@example.com")
        auth_code = self.issue_code(
            user,
            AuthCode.Purpose.PASSWORD_RESET,
            "111111",
        )
        original_hash = auth_code.code_hash

        response = self.client.post(
            self.request_url,
            {"email": user.email},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.generic_response)
        auth_code.refresh_from_db()
        self.assertEqual(AuthCode.objects.count(), 1)
        self.assertEqual(auth_code.code_hash, original_hash)
        self.assertEqual(len(mail.outbox), 1)

    def test_smtp_failure_is_generic_and_rolls_back_new_reset_code(self):
        user = self.create_user("owner@example.com")

        with patch(
            "apps.users.services.send_mail",
            side_effect=RuntimeError("smtp-user-and-password"),
        ):
            response = self.client.post(
                self.request_url,
                {"email": user.email},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.generic_response)
        self.assertNotIn("smtp-user-and-password", str(response.data))
        self.assertFalse(AuthCode.objects.filter(user=user).exists())
        self.assertEqual(len(mail.outbox), 0)


@override_settings(
    EMAIL_BACKEND=LOC_MEM_EMAIL_BACKEND,
    PASSWORD_HASHERS=FAST_PASSWORD_HASHERS,
    AUTH_CODE_TTL_MINUTES=10,
    AUTH_CODE_RESEND_COOLDOWN_SECONDS=60,
    AUTH_CODE_MAX_ATTEMPTS=5,
)
class PasswordResetConfirmEndpointTests(AuthCodeEndpointMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.confirm_url = reverse("users:password-reset-confirm")
        self.login_url = reverse("users:login")
        self.profile_url = reverse("users:me")
        self.current_password = "CurrentStrongPass123!"
        self.new_password = "DifferentStrongPass456!"

    def valid_payload(self, user, code):
        return {
            "email": user.email,
            "code": code,
            "new_password": self.new_password,
            "new_password_confirm": self.new_password,
        }

    def test_leading_zero_code_resets_password_once_without_returning_secrets(self):
        user = self.create_user(
            "owner@example.com",
            password=self.current_password,
        )
        auth_code = self.issue_code(
            user,
            AuthCode.Purpose.PASSWORD_RESET,
            "004271",
        )
        payload = self.valid_payload(user, "004271")

        response = self.client.post(
            self.confirm_url,
            payload,
            format="json",
        )
        replay_response = self.client.post(
            self.confirm_url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "detail": (
                    "Parolanız başarıyla yenilendi. Yeni parolanızla giriş "
                    "yapabilirsiniz."
                )
            },
        )
        self.assertEqual(
            replay_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        response_text = str(response.data)
        for secret in (
            "004271",
            self.current_password,
            self.new_password,
        ):
            self.assertNotIn(secret, response_text)
        self.assertTrue(
            {
                "access_token",
                "refresh_token",
                "token",
                "password",
                "code",
            }.isdisjoint(response.data)
        )
        user.refresh_from_db()
        auth_code.refresh_from_db()
        self.assertFalse(user.check_password(self.current_password))
        self.assertTrue(user.check_password(self.new_password))
        self.assertIsNotNone(auth_code.consumed_at)

        old_login = self.client.post(
            self.login_url,
            {"email": user.email, "password": self.current_password},
            format="json",
        )
        new_login = self.client.post(
            self.login_url,
            {"email": user.email, "password": self.new_password},
            format="json",
        )
        self.assertEqual(
            old_login.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(new_login.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(new_login.data),
            {"access_token", "refresh_token", "user"},
        )

    def test_confirmation_mismatch_and_django_validator_do_not_consume_code(self):
        user = self.create_user(
            "owner@example.com",
            password=self.current_password,
        )
        auth_code = self.issue_code(
            user,
            AuthCode.Purpose.PASSWORD_RESET,
            "123456",
        )
        mismatch_payload = self.valid_payload(user, "123456")
        mismatch_payload["new_password_confirm"] = "OtherStrongPass789!"

        mismatch_response = self.client.post(
            self.confirm_url,
            mismatch_payload,
            format="json",
        )
        weak_payload = self.valid_payload(user, "123456")
        weak_payload["new_password"] = "12345678"
        weak_payload["new_password_confirm"] = "12345678"
        weak_response = self.client.post(
            self.confirm_url,
            weak_payload,
            format="json",
        )

        self.assertEqual(
            mismatch_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            set(mismatch_response.data),
            {"new_password_confirm"},
        )
        self.assertEqual(
            weak_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(set(weak_response.data), {"new_password"})
        user.refresh_from_db()
        auth_code.refresh_from_db()
        self.assertTrue(user.check_password(self.current_password))
        self.assertIsNone(auth_code.consumed_at)
        self.assertEqual(auth_code.failed_attempts, 0)
        self.assertNotIn("12345678", str(weak_response.data))

    def test_wrong_attempts_lock_reset_code_without_changing_password(self):
        user = self.create_user(
            "owner@example.com",
            password=self.current_password,
        )
        auth_code = self.issue_code(
            user,
            AuthCode.Purpose.PASSWORD_RESET,
            "123456",
        )
        wrong_payload = self.valid_payload(user, "999999")

        for attempt in range(5):
            response = self.client.post(
                self.confirm_url,
                wrong_payload,
                format="json",
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
            )
            auth_code.refresh_from_db()
            self.assertEqual(auth_code.failed_attempts, attempt + 1)

        correct_response = self.client.post(
            self.confirm_url,
            self.valid_payload(user, "123456"),
            format="json",
        )
        self.assertEqual(
            correct_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        user.refresh_from_db()
        auth_code.refresh_from_db()
        self.assertTrue(user.check_password(self.current_password))
        self.assertEqual(auth_code.failed_attempts, 5)
        self.assertIsNone(auth_code.consumed_at)

    def test_expired_reset_code_is_rejected(self):
        user = self.create_user(
            "owner@example.com",
            password=self.current_password,
        )
        auth_code = self.issue_code(
            user,
            AuthCode.Purpose.PASSWORD_RESET,
            "123456",
        )
        self.expire_code(auth_code)

        response = self.client.post(
            self.confirm_url,
            self.valid_payload(user, "123456"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        auth_code.refresh_from_db()
        self.assertTrue(user.check_password(self.current_password))
        self.assertIsNone(auth_code.consumed_at)

    def test_email_verification_code_cannot_reset_password(self):
        user = self.create_user(
            "owner@example.com",
            password=self.current_password,
        )
        verification_code = AuthCode.objects.create(
            user=user,
            purpose=AuthCode.Purpose.EMAIL_VERIFICATION,
            code_hash=make_password("123456"),
            expires_at=timezone.now() + timedelta(minutes=10),
            resend_available_at=timezone.now() + timedelta(seconds=60),
        )

        response = self.client.post(
            self.confirm_url,
            self.valid_payload(user, "123456"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        verification_code.refresh_from_db()
        self.assertTrue(user.check_password(self.current_password))
        self.assertEqual(verification_code.failed_attempts, 0)
        self.assertIsNone(verification_code.consumed_at)

    def test_another_users_reset_code_does_not_change_either_user(self):
        target = self.create_user(
            "target@example.com",
            password=self.current_password,
        )
        other = self.create_user(
            "other@example.com",
            password="OtherStrongPass123!",
        )
        target_code = self.issue_code(
            target,
            AuthCode.Purpose.PASSWORD_RESET,
            "111111",
        )
        other_code = self.issue_code(
            other,
            AuthCode.Purpose.PASSWORD_RESET,
            "222222",
        )

        response = self.client.post(
            self.confirm_url,
            self.valid_payload(target, "222222"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        target.refresh_from_db()
        other.refresh_from_db()
        target_code.refresh_from_db()
        other_code.refresh_from_db()
        self.assertTrue(target.check_password(self.current_password))
        self.assertTrue(other.check_password("OtherStrongPass123!"))
        self.assertEqual(target_code.failed_attempts, 1)
        self.assertEqual(other_code.failed_attempts, 0)
        self.assertIsNone(target_code.consumed_at)
        self.assertIsNone(other_code.consumed_at)

    def test_all_fields_are_required_and_code_must_remain_a_string(self):
        user = self.create_user("owner@example.com")
        base_payload = self.valid_payload(user, "123456")

        for field in (
            "email",
            "code",
            "new_password",
            "new_password_confirm",
        ):
            with self.subTest(field=field):
                payload = dict(base_payload)
                payload.pop(field)
                response = self.client.post(
                    self.confirm_url,
                    payload,
                    format="json",
                )
                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertIn(field, response.data)

        integer_payload = dict(base_payload)
        integer_payload["code"] = 123456
        integer_response = self.client.post(
            self.confirm_url,
            integer_payload,
            format="json",
        )
        self.assertEqual(
            integer_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(set(integer_response.data), {"code"})

    def test_reset_does_not_revoke_preexisting_access_or_refresh_tokens(self):
        user = self.create_user(
            "owner@example.com",
            password=self.current_password,
        )
        login_response = self.client.post(
            self.login_url,
            {"email": user.email, "password": self.current_password},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        old_access = login_response.data["access_token"]
        old_refresh = login_response.data["refresh_token"]
        self.issue_code(
            user,
            AuthCode.Purpose.PASSWORD_RESET,
            "123456",
        )

        reset_response = self.client.post(
            self.confirm_url,
            self.valid_payload(user, "123456"),
            format="json",
        )
        self.assertEqual(reset_response.status_code, status.HTTP_200_OK)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {old_access}",
        )
        old_access_response = self.client.get(self.profile_url)
        self.assertEqual(old_access_response.status_code, status.HTTP_200_OK)
        self.assertEqual(old_access_response.data["id"], user.id)

        access_from_old_refresh = str(
            RefreshToken(old_refresh).access_token
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_from_old_refresh}",
        )
        old_refresh_response = self.client.get(self.profile_url)
        self.assertEqual(old_refresh_response.status_code, status.HTTP_200_OK)
        self.assertEqual(old_refresh_response.data["id"], user.id)


@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework_simplejwt.authentication.JWTAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.AllowAny",
        ],
        "DEFAULT_THROTTLE_RATES": {
            "auth_code_send": "2/min",
            "auth_code_verify": "2/min",
        },
        "NUM_PROXIES": 0,
    },
)
class PublicAuthThrottleTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.throttle_rates = patch.object(
            ScopedIPRateThrottle,
            "THROTTLE_RATES",
            {
                "auth_code_send": "2/min",
                "auth_code_verify": "2/min",
            },
        )
        self.throttle_rates.start()
        self.addCleanup(self.throttle_rates.stop)
        self.register_url = reverse("users:register")
        self.reset_request_url = reverse("users:password-reset-request")
        self.verify_url = reverse("users:verify-email")

    def tearDown(self):
        cache.clear()
        super().tearDown()

    def assert_throttled_without_account_data(self, response):
        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )
        self.assertEqual(set(response.data), {"detail"})
        response_text = str(response.data["detail"]).lower()
        self.assertNotIn("email", response_text)
        self.assertNotIn("password", response_text)
        self.assertIsNone(re.search(r"(?<![0-9])[0-9]{6}(?![0-9])", response_text))

    def test_send_scope_uses_remote_ip_and_ignores_spoofed_forwarded_for(self):
        responses = []
        for forwarded_ip in ("198.51.100.1", "198.51.100.2", "198.51.100.3"):
            responses.append(
                self.client.post(
                    self.reset_request_url,
                    {"email": "missing@example.com"},
                    format="json",
                    HTTP_X_FORWARDED_FOR=forwarded_ip,
                )
            )

        self.assertEqual(responses[0].status_code, status.HTTP_200_OK)
        self.assertEqual(responses[1].status_code, status.HTTP_200_OK)
        self.assert_throttled_without_account_data(responses[2])

    def test_verify_scope_returns_429_after_configured_ip_limit(self):
        responses = [
            self.client.post(
                self.verify_url,
                {"email": "missing@example.com", "code": "123456"},
                format="json",
            )
            for _ in range(3)
        ]

        self.assertEqual(
            responses[0].status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            responses[1].status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assert_throttled_without_account_data(responses[2])

    def test_register_is_protected_by_the_send_scope(self):
        responses = [
            self.client.post(
                self.register_url,
                {"password": "StrongPass123!"},
                format="json",
            )
            for _ in range(3)
        ]

        self.assertEqual(
            responses[0].status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            responses[1].status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assert_throttled_without_account_data(responses[2])


class ProfileEndpointsTests(APITestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.password = "CurrentStrongPass123!"
        self.user = self.user_model.objects.create_user(
            username="owner@example.com",
            email="owner@example.com",
            password=self.password,
            first_name="Current",
            last_name="Owner",
        )
        self.other_user = self.user_model.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password="OtherStrongPass123!",
            first_name="Other",
            last_name="Person",
        )
        self.profile_url = reverse("users:me")

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def assert_profile_response(self, response):
        self.assertEqual(set(response.data), PROFILE_RESPONSE_KEYS)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["first_name"], self.user.first_name)
        self.assertEqual(response.data["last_name"], self.user.last_name)

    def test_anonymous_user_cannot_get_profile(self):
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_gets_only_own_safe_profile(self):
        self.authenticate()

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_profile_response(response)
        self.assertNotEqual(response.data["id"], self.other_user.id)
        self.assertNotEqual(response.data["email"], self.other_user.email)
        self.assertTrue(
            {
                "password",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            }.isdisjoint(response.data)
        )

    def test_profile_get_supports_existing_blank_names(self):
        self.user.first_name = ""
        self.user.last_name = ""
        self.user.save(update_fields=["first_name", "last_name"])
        self.authenticate()

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "")
        self.assertEqual(response.data["last_name"], "")

    def test_user_can_update_only_first_name_without_erasing_last_name(self):
        self.authenticate()

        response = self.client.patch(
            self.profile_url,
            {"first_name": "  Updated  "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Owner")
        self.assert_profile_response(response)

    def test_user_can_update_only_last_name_without_erasing_first_name(self):
        self.authenticate()

        response = self.client.patch(
            self.profile_url,
            {"last_name": "  Surname  "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Current")
        self.assertEqual(self.user.last_name, "Surname")
        self.assert_profile_response(response)

    def test_user_can_update_both_names_without_affecting_other_user(self):
        other_values = (
            self.other_user.first_name,
            self.other_user.last_name,
            self.other_user.email,
        )
        self.authenticate()

        response = self.client.patch(
            self.profile_url,
            {"first_name": "  New  ", "last_name": "  Name  "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.other_user.refresh_from_db()
        self.assertEqual(self.user.first_name, "New")
        self.assertEqual(self.user.last_name, "Name")
        self.assert_profile_response(response)
        self.assertEqual(
            (
                self.other_user.first_name,
                self.other_user.last_name,
                self.other_user.email,
            ),
            other_values,
        )

    def test_whitespace_only_names_are_rejected_without_database_changes(self):
        self.authenticate()

        for field in ("first_name", "last_name"):
            with self.subTest(field=field):
                response = self.client.patch(
                    self.profile_url,
                    {field: "   "},
                    format="json",
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
                self.user.refresh_from_db()
                self.assertEqual(self.user.first_name, "Current")
                self.assertEqual(self.user.last_name, "Owner")

    def test_overlong_names_are_rejected_without_database_changes(self):
        self.authenticate()

        for field in ("first_name", "last_name"):
            max_length = self.user._meta.get_field(field).max_length
            with self.subTest(field=field):
                response = self.client.patch(
                    self.profile_url,
                    {field: "x" * (max_length + 1)},
                    format="json",
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
                self.user.refresh_from_db()
                self.assertEqual(self.user.first_name, "Current")
                self.assertEqual(self.user.last_name, "Owner")

    def test_email_update_is_explicitly_rejected(self):
        original_username = self.user.username
        original_email = self.user.email
        self.authenticate()

        payloads = (
            {"email": "changed@example.com"},
            {"email": "changed@example.com", "first_name": "   "},
        )
        for payload in payloads:
            with self.subTest(payload=payload):
                response = self.client.patch(
                    self.profile_url,
                    payload,
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )
                self.assertEqual(
                    response.data,
                    {"email": ["E-posta adresi bu ekrandan değiştirilemez."]},
                )
                self.user.refresh_from_db()
                self.assertEqual(self.user.username, original_username)
                self.assertEqual(self.user.email, original_email)
                self.assertEqual(self.user.first_name, "Current")

    def test_protected_and_unknown_fields_are_rejected_without_changes(self):
        original_values = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "password": self.user.password,
            "is_staff": self.user.is_staff,
            "is_superuser": self.user.is_superuser,
        }
        other_values = {
            "id": self.other_user.id,
            "email": self.other_user.email,
            "password": self.other_user.password,
            "is_staff": self.other_user.is_staff,
            "is_superuser": self.other_user.is_superuser,
        }
        attempts = {
            "id": self.other_user.id,
            "username": "changed@example.com",
            "password": "CompromisedPass123!",
            "is_staff": True,
            "is_superuser": True,
            "unknown": "value",
        }
        self.authenticate()

        for field, value in attempts.items():
            with self.subTest(field=field):
                response = self.client.patch(
                    self.profile_url,
                    {field: value},
                    format="json",
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
                self.user.refresh_from_db()
                self.assertEqual(self.user.id, original_values["id"])
                self.assertEqual(self.user.username, original_values["username"])
                self.assertEqual(self.user.email, original_values["email"])
                self.assertEqual(self.user.password, original_values["password"])
                self.assertEqual(self.user.is_staff, original_values["is_staff"])
                self.assertEqual(
                    self.user.is_superuser,
                    original_values["is_superuser"],
                )
                self.assertTrue(self.user.check_password(self.password))
                self.other_user.refresh_from_db()
                self.assertEqual(self.other_user.id, other_values["id"])
                self.assertEqual(self.other_user.email, other_values["email"])
                self.assertEqual(
                    self.other_user.password,
                    other_values["password"],
                )
                self.assertEqual(
                    self.other_user.is_staff,
                    other_values["is_staff"],
                )
                self.assertEqual(
                    self.other_user.is_superuser,
                    other_values["is_superuser"],
                )


class ChangePasswordEndpointTests(APITestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.current_password = "CurrentStrongPass123!"
        self.new_password = "DifferentStrongPass456!"
        self.user = self.user_model.objects.create_user(
            username="owner@example.com",
            email="owner@example.com",
            password=self.current_password,
            first_name="Current",
            last_name="Owner",
        )
        self.other_password = "OtherStrongPass123!"
        self.other_user = self.user_model.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password=self.other_password,
            first_name="Other",
            last_name="Person",
        )
        self.change_password_url = reverse("users:change-password")
        self.login_url = reverse("users:login")
        self.profile_url = reverse("users:me")

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def valid_payload(self):
        return {
            "current_password": self.current_password,
            "new_password": self.new_password,
            "new_password_confirm": self.new_password,
        }

    def assert_response_excludes_secrets(self, response, payload):
        response_text = str(response.data)
        for secret in payload.values():
            if isinstance(secret, str):
                self.assertNotIn(secret, response_text)

    def test_anonymous_user_cannot_change_password(self):
        payload = self.valid_payload()
        response = self.client.post(
            self.change_password_url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assert_response_excludes_secrets(response, payload)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.current_password))

    def test_wrong_current_password_is_rejected_without_secret_echo(self):
        original_hash = self.user.password
        payload = self.valid_payload()
        payload["current_password"] = "WrongCurrentPass123!"
        self.authenticate()

        response = self.client.post(
            self.change_password_url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.data), {"current_password"})
        self.assert_response_excludes_secrets(response, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.password, original_hash)
        self.assertTrue(self.user.check_password(self.current_password))

    def test_all_password_fields_are_required(self):
        self.authenticate()

        for field in (
            "current_password",
            "new_password",
            "new_password_confirm",
        ):
            payload = self.valid_payload()
            payload.pop(field)
            with self.subTest(field=field):
                response = self.client.post(
                    self.change_password_url,
                    payload,
                    format="json",
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
                self.assert_response_excludes_secrets(response, payload)
                self.user.refresh_from_db()
                self.assertTrue(self.user.check_password(self.current_password))

    def test_password_confirmation_must_match(self):
        payload = self.valid_payload()
        payload["new_password_confirm"] = "AnotherStrongPass789!"
        self.authenticate()

        response = self.client.post(
            self.change_password_url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.data), {"new_password_confirm"})
        self.assert_response_excludes_secrets(response, payload)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.current_password))

    def test_new_password_must_differ_from_current_password(self):
        payload = self.valid_payload()
        payload["new_password"] = self.current_password
        payload["new_password_confirm"] = self.current_password
        self.authenticate()

        response = self.client.post(
            self.change_password_url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.data), {"new_password"})
        self.assert_response_excludes_secrets(response, payload)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.current_password))

    def test_django_password_validators_reject_weak_password(self):
        payload = self.valid_payload()
        payload["new_password"] = "12345678"
        payload["new_password_confirm"] = "12345678"
        self.authenticate()

        response = self.client.post(
            self.change_password_url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.data), {"new_password"})
        self.assert_response_excludes_secrets(response, payload)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.current_password))

    def test_successful_password_change_hashes_password_and_returns_safe_response(self):
        original_hash = self.user.password
        other_hash = self.other_user.password
        payload = self.valid_payload()
        self.authenticate()

        response = self.client.post(
            self.change_password_url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "detail": "Parolanız başarıyla güncellendi.",
                "requires_reauthentication": True,
            },
        )
        self.assert_response_excludes_secrets(response, payload)

        self.user.refresh_from_db()
        self.other_user.refresh_from_db()
        self.assertNotEqual(self.user.password, original_hash)
        self.assertNotEqual(self.user.password, self.new_password)
        self.assertFalse(self.user.check_password(self.current_password))
        self.assertTrue(self.user.check_password(self.new_password))
        self.assertEqual(self.other_user.password, other_hash)
        self.assertTrue(self.other_user.check_password(self.other_password))

    def test_login_uses_only_new_password_after_successful_change(self):
        self.authenticate()
        change_response = self.client.post(
            self.change_password_url,
            self.valid_payload(),
            format="json",
        )
        self.assertEqual(change_response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=None)

        old_login_response = self.client.post(
            self.login_url,
            {"email": self.user.email, "password": self.current_password},
            format="json",
        )
        new_login_response = self.client.post(
            self.login_url,
            {"email": self.user.email, "password": self.new_password},
            format="json",
        )

        self.assertEqual(
            old_login_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(new_login_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(new_login_response.data),
            {"access_token", "refresh_token", "user"},
        )
        self.assertEqual(new_login_response.data["user"]["id"], self.user.id)

    def test_existing_access_and_refresh_tokens_survive_password_change(self):
        login_response = self.client.post(
            self.login_url,
            {"email": self.user.email, "password": self.current_password},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        refresh_token = login_response.data["refresh_token"]
        access_token = login_response.data["access_token"]
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )

        change_response = self.client.post(
            self.change_password_url,
            self.valid_payload(),
            format="json",
        )
        old_access_response = self.client.get(self.profile_url)

        self.assertEqual(change_response.status_code, status.HTTP_200_OK)
        self.assertEqual(old_access_response.status_code, status.HTTP_200_OK)
        self.assertEqual(old_access_response.data["id"], self.user.id)

        access_from_old_refresh = str(RefreshToken(refresh_token).access_token)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_from_old_refresh}",
        )
        refreshed_access_response = self.client.get(self.profile_url)

        self.assertEqual(
            refreshed_access_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(refreshed_access_response.data["id"], self.user.id)

    def test_password_fields_are_write_only_and_serializer_repr_is_safe(self):
        payload = self.valid_payload()
        serializer = ChangePasswordSerializer(
            data=payload,
            context={"request": SimpleNamespace(user=self.user)},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        for field in payload:
            self.assertTrue(serializer.fields[field].write_only)
        representation = repr(serializer)
        for secret in payload.values():
            self.assertNotIn(secret, representation)

    @override_settings(DEBUG=False)
    def test_unexpected_validation_error_redacts_passwords_from_error_report(self):
        payload = self.valid_payload()
        request = APIRequestFactory().post(
            self.change_password_url,
            payload,
            format="json",
        )
        force_authenticate(request, user=self.user)

        with patch(
            "apps.users.serializers.password_validation.validate_password",
            side_effect=RuntimeError("Synthetic validator failure"),
        ):
            try:
                ChangePasswordView.as_view()(request)
            except RuntimeError:
                exception_type, exception_value, traceback = sys.exc_info()
            else:
                self.fail("Synthetic validator failure was not raised.")

        while traceback and traceback.tb_frame.f_code.co_filename == __file__:
            traceback = traceback.tb_next

        report = ExceptionReporter(
            request,
            exception_type,
            exception_value,
            traceback,
        ).get_traceback_html()
        self.assertIn("Synthetic validator failure", report)
        for secret in payload.values():
            self.assertNotIn(secret, report)
