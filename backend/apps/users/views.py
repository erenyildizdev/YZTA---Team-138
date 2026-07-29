from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.views.decorators.debug import sensitive_variables
from rest_framework import permissions, status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    ChangePasswordSerializer,
    EmailRequestSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    ProfileSerializer,
    RegisterSerializer,
    VerifyEmailSerializer,
)
from .services import issue_auth_code, reset_password_with_code, verify_email_code
from .models import AuthCode
from .throttles import ScopedIPRateThrottle

User = get_user_model()

REGISTER_SUCCESS_RESPONSE = {
    "detail": (
        "Hesabınız oluşturuldu. E-posta adresinize gönderilen doğrulama "
        "kodunu girin."
    ),
    "requires_email_verification": True,
}
REGISTER_FAILURE_RESPONSE = {
    "detail": "Kayıt şu anda tamamlanamadı. Lütfen daha sonra tekrar deneyin."
}
VERIFY_SUCCESS_RESPONSE = {
    "detail": "E-posta adresiniz doğrulandı. Giriş yapabilirsiniz."
}
VERIFY_FAILURE_RESPONSE = {
    "detail": "Doğrulama kodu geçersiz veya süresi dolmuş."
}
RESEND_RESPONSE = {
    "detail": "E-posta adresi uygunsa yeni doğrulama kodu gönderildi."
}
PASSWORD_RESET_REQUEST_RESPONSE = {
    "detail": "E-posta adresi uygunsa parola sıfırlama kodu gönderildi."
}
PASSWORD_RESET_SUCCESS_RESPONSE = {
    "detail": (
        "Parolanız başarıyla yenilendi. Yeni parolanızla giriş yapabilirsiniz."
    )
}
PASSWORD_RESET_FAILURE_RESPONSE = {
    "detail": "Parola sıfırlama kodu geçersiz veya süresi dolmuş."
}


def _find_user_by_canonical_email(email):
    return User.objects.filter(username=email).first()


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]
    throttle_classes = [ScopedIPRateThrottle]
    throttle_scope = "auth_code_send"

    @sensitive_variables()
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                user = serializer.save()
                issue_auth_code(user, AuthCode.Purpose.EMAIL_VERIFICATION)
        except IntegrityError:
            return Response(
                {
                    "email": [
                        "Bu e-posta adresiyle bir hesap zaten mevcut."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                REGISTER_FAILURE_RESPONSE,
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                **REGISTER_SUCCESS_RESPONSE,
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]

    @sensitive_variables()
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        if not user.is_email_verified:
            return Response(
                {
                    "detail": "E-posta adresinizi doğrulamanız gerekiyor.",
                    "code": "email_not_verified",
                    "email": serializer.validated_data["email"],
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            },
            status=status.HTTP_200_OK,
        )


class VerifyEmailView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]
    throttle_classes = [ScopedIPRateThrottle]
    throttle_scope = "auth_code_verify"

    @sensitive_variables()
    def post(self, request, *args, **kwargs):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = _find_user_by_canonical_email(
            serializer.validated_data["email"]
        )

        if user and verify_email_code(
            user,
            serializer.validated_data["code"],
        ):
            return Response(
                VERIFY_SUCCESS_RESPONSE,
                status=status.HTTP_200_OK,
            )

        return Response(
            VERIFY_FAILURE_RESPONSE,
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResendVerificationView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]
    throttle_classes = [ScopedIPRateThrottle]
    throttle_scope = "auth_code_send"

    def post(self, request, *args, **kwargs):
        serializer = EmailRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = _find_user_by_canonical_email(
            serializer.validated_data["email"]
        )

        if user and user.is_active and not user.is_email_verified:
            try:
                issue_auth_code(
                    user,
                    AuthCode.Purpose.EMAIL_VERIFICATION,
                )
            except Exception:
                pass

        return Response(RESEND_RESPONSE, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]
    throttle_classes = [ScopedIPRateThrottle]
    throttle_scope = "auth_code_send"

    def post(self, request, *args, **kwargs):
        serializer = EmailRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = _find_user_by_canonical_email(
            serializer.validated_data["email"]
        )

        if user and user.is_active and user.is_email_verified:
            try:
                issue_auth_code(user, AuthCode.Purpose.PASSWORD_RESET)
            except Exception:
                pass

        return Response(
            PASSWORD_RESET_REQUEST_RESPONSE,
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]
    throttle_classes = [ScopedIPRateThrottle]
    throttle_scope = "auth_code_verify"

    @sensitive_variables()
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = _find_user_by_canonical_email(
            serializer.validated_data["email"]
        )

        if not user or not user.is_active or not user.is_email_verified:
            return Response(
                PASSWORD_RESET_FAILURE_RESPONSE,
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reset_succeeded = reset_password_with_code(
                user,
                serializer.validated_data["code"],
                serializer.validated_data["new_password"],
            )
        except DjangoValidationError as error:
            return Response(
                {"new_password": list(error.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not reset_succeeded:
            return Response(
                PASSWORD_RESET_FAILURE_RESPONSE,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            PASSWORD_RESET_SUCCESS_RESPONSE,
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        serializer = ProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    @sensitive_variables()
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response(
            {
                "detail": "Parolanız başarıyla güncellendi.",
                "requires_reauthentication": True,
            },
            status=status.HTTP_200_OK,
        )
