from django.urls import path

from .views import (
    LoginView,
    MeView,
    MyProfileView,
    PublicProfileView,
    RefreshView,
    RegisterView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
]

profile_urlpatterns = [
    path("profiles/me/", MyProfileView.as_view(), name="profile-me"),
    path("profiles/<int:user_id>/", PublicProfileView.as_view(), name="profile-public"),
]
