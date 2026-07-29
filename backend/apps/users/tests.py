import sys
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django.views.debug import ExceptionReporter
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .serializers import ChangePasswordSerializer
from .views import ChangePasswordView


PROFILE_RESPONSE_KEYS = {"id", "email", "first_name", "last_name"}


class AuthEndpointsTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("users:register")
        self.login_url = reverse("users:login")
        self.user_model = get_user_model()

    def test_register_creates_user_and_returns_user_data(self):
        payload = {
            "email": "founder@example.com",
            "password": "StrongPass123!",
            "first_name": "Ada",
            "last_name": "Lovelace",
        }

        response = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data), {"message", "user"})
        self.assertEqual(response.data["message"], "User registered successfully.")
        self.assertEqual(set(response.data["user"]), PROFILE_RESPONSE_KEYS)

        email = payload["email"].lower()
        self.assertEqual(response.data["user"]["email"], email)
        user = self.user_model.objects.get(username=email)
        self.assertEqual(response.data["user"]["id"], user.id)
        self.assertEqual(response.data["user"]["first_name"], payload["first_name"])
        self.assertEqual(response.data["user"]["last_name"], payload["last_name"])
        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, payload["first_name"])
        self.assertEqual(user.last_name, payload["last_name"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", response.data["user"])

    def test_login_returns_tokens_for_valid_credentials(self):
        user = self.user_model.objects.create_user(
            username="tester@example.com",
            email="tester@example.com",
            password="StrongPass123!",
            first_name="Test",
            last_name="User",
        )

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
