from django.urls import path

from .views import ChangePasswordView, LoginView, ProfileView, RegisterView

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", ProfileView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]
