from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from credits.services import ledger_balance

User = get_user_model()


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_login_me_and_signup_bonus(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "email": "guest@example.com",
                "password": "StrongPass123",
                "display_name": "Guest One",
                "phone": "9999999999",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email="guest@example.com")
        self.assertEqual(user.profile.display_name, "Guest One")
        self.assertEqual(ledger_balance(user), 2)

        login = self.client.post(
            "/api/v1/auth/login/",
            {"email": "guest@example.com", "password": "StrongPass123"},
            format="json",
        )
        self.assertEqual(login.status_code, 200)
        token = login.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        me = self.client.get("/api/v1/auth/me/")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data["email"], "guest@example.com")

        profile = self.client.get("/api/v1/profiles/me/")
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.data["display_name"], "Guest One")

        updated = self.client.patch(
            "/api/v1/profiles/me/",
            {"bio": "Loves Goa", "city": "Goa", "languages": ["English", "Hindi"]},
            format="json",
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["city"], "Goa")

    def test_public_profile_requires_auth(self):
        user = User.objects.create_user(email="host@example.com", password="StrongPass123")
        response = self.client.get(f"/api/v1/profiles/{user.id}/")
        self.assertEqual(response.status_code, 401)
