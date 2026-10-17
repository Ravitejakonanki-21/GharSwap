from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from listings.models import Availability, Listing
from stays.models import StayRequest

User = get_user_model()


class ReviewAndSafetyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.host = User.objects.create_user(email="host@example.com", password="StrongPass123")
        self.guest = User.objects.create_user(email="guest@example.com", password="StrongPass123")
        self.stranger = User.objects.create_user(email="stranger@example.com", password="StrongPass123")
        self.listing = Listing.objects.create(
            host=self.host,
            title="White Town studio",
            description="Near the promenade",
            city="Pondicherry",
            address_area="White Town",
            max_guests=2,
        )
        Availability.objects.create(
            listing=self.listing, start_date=date(2026, 11, 1), end_date=date(2026, 11, 30)
        )

    def auth(self, user):
        login = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "StrongPass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def complete_stay(self):
        self.auth(self.guest)
        stay_id = self.client.post(
            "/api/v1/stay-requests/",
            {
                "listing": self.listing.id,
                "check_in": "2026-11-10",
                "check_out": "2026-11-12",
                "guests_count": 1,
            },
            format="json",
        ).data["id"]
        self.auth(self.host)
        self.client.post(f"/api/v1/stay-requests/{stay_id}/accept/")
        self.client.post(f"/api/v1/stay-requests/{stay_id}/complete/")
        return stay_id

    def test_only_participants_can_review_completed_stay(self):
        stay_id = self.complete_stay()
        self.auth(self.stranger)
        denied = self.client.post(
            "/api/v1/reviews/",
            {"stay_request": stay_id, "rating": 5, "comment": "Nice"},
            format="json",
        )
        self.assertEqual(denied.status_code, 400)

        self.auth(self.guest)
        ok = self.client.post(
            "/api/v1/reviews/",
            {"stay_request": stay_id, "rating": 5, "comment": "Wonderful host"},
            format="json",
        )
        self.assertEqual(ok.status_code, 201)
        duplicate = self.client.post(
            "/api/v1/reviews/",
            {"stay_request": stay_id, "rating": 4, "comment": "again"},
            format="json",
        )
        self.assertEqual(duplicate.status_code, 400)

        reviews = self.client.get(f"/api/v1/users/{self.host.id}/reviews/")
        self.assertEqual(reviews.data["count"], 1)

    def test_block_hides_profile_and_prevents_request(self):
        self.auth(self.host)
        blocked = self.client.post("/api/v1/blocks/", {"blocked_user": self.guest.id}, format="json")
        self.assertEqual(blocked.status_code, 201)

        self.auth(self.guest)
        hidden = self.client.get(f"/api/v1/profiles/{self.host.id}/")
        self.assertEqual(hidden.status_code, 404)
        request_stay = self.client.post(
            "/api/v1/stay-requests/",
            {
                "listing": self.listing.id,
                "check_in": "2026-11-10",
                "check_out": "2026-11-12",
                "guests_count": 1,
            },
            format="json",
        )
        self.assertEqual(request_stay.status_code, 400)

    def test_report_user(self):
        self.auth(self.guest)
        response = self.client.post(
            "/api/v1/reports/",
            {"reported_user": self.host.id, "reason": "spam", "details": "Suspicious listing"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
