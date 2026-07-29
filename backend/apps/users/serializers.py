from collections.abc import Mapping

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

User = get_user_model()
FIRST_NAME_MAX_LENGTH = User._meta.get_field("first_name").max_length
LAST_NAME_MAX_LENGTH = User._meta.get_field("last_name").max_length
AUTH_EMAIL_MAX_LENGTH = User._meta.get_field("username").max_length


def normalize_auth_email(value):
    return value.strip().lower()


class StrictSixDigitCodeField(serializers.CharField):
    default_error_messages = {
        "invalid": "Kod tam olarak altı rakamdan oluşmalıdır.",
    }

    def __init__(self, **kwargs):
        kwargs.setdefault("trim_whitespace", False)
        kwargs.setdefault("write_only", True)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if not isinstance(data, str):
            self.fail("invalid")

        value = super().to_internal_value(data)
        if len(value) != 6 or not value.isascii() or not value.isdigit():
            self.fail("invalid")
        return value


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        max_length=AUTH_EMAIL_MAX_LENGTH,
    )
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name")

    def validate_email(self, value):
        email = normalize_auth_email(value)
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError(
                "Bu e-posta adresiyle bir hesap zaten mevcut."
            )
        return email

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            is_email_verified=False,
        )
        return user


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(
        allow_blank=False,
        max_length=FIRST_NAME_MAX_LENGTH,
        required=False,
        trim_whitespace=True,
    )
    last_name = serializers.CharField(
        allow_blank=False,
        max_length=LAST_NAME_MAX_LENGTH,
        required=False,
        trim_whitespace=True,
    )

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name")
        read_only_fields = ("id", "email")

    def to_internal_value(self, data):
        allowed_fields = {"first_name", "last_name"}
        disallowed_fields = (
            set(data) - allowed_fields
            if isinstance(data, Mapping)
            else set()
        )

        if disallowed_fields:
            errors = {}
            for field in sorted(disallowed_fields):
                if field == "email":
                    message = "E-posta adresi bu ekrandan değiştirilemez."
                else:
                    message = "Bu alan profil ekranından güncellenemez."
                errors[field] = [message]
            raise serializers.ValidationError(errors)

        return super().to_internal_value(data)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        trim_whitespace=False,
        write_only=True,
    )
    new_password = serializers.CharField(
        trim_whitespace=False,
        write_only=True,
    )
    new_password_confirm = serializers.CharField(
        trim_whitespace=False,
        write_only=True,
    )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            "current_password=<write-only>, "
            "new_password=<write-only>, "
            "new_password_confirm=<write-only>)"
        )

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mevcut parola yanlış.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        new_password = attrs["new_password"]

        if new_password != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": ["Yeni parola ve onayı eşleşmiyor."]}
            )

        if user.check_password(new_password):
            raise serializers.ValidationError(
                {"new_password": ["Yeni parola mevcut paroladan farklı olmalıdır."]}
            )

        try:
            password_validation.validate_password(new_password, user=user)
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {"new_password": list(error.messages)}
            ) from error

        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=AUTH_EMAIL_MAX_LENGTH)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = normalize_auth_email(attrs.get("email", ""))
        password = attrs.get("password", "")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError({"detail": "Invalid email or password."})

        attrs["email"] = email
        attrs["user"] = user
        return attrs


class EmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=AUTH_EMAIL_MAX_LENGTH)

    def validate_email(self, value):
        return normalize_auth_email(value)


class VerifyEmailSerializer(EmailRequestSerializer):
    code = StrictSixDigitCodeField()


class PasswordResetConfirmSerializer(VerifyEmailSerializer):
    new_password = serializers.CharField(
        trim_whitespace=False,
        write_only=True,
    )
    new_password_confirm = serializers.CharField(
        trim_whitespace=False,
        write_only=True,
    )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            "email=<normalized>, code=<write-only>, "
            "new_password=<write-only>, "
            "new_password_confirm=<write-only>)"
        )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": ["Yeni parola ve onayı eşleşmiyor."]}
            )
        return attrs
