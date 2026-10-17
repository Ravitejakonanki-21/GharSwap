from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from listings.models import Availability, Listing

User = get_user_model()


class ListingSearchTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.host = User.objects.create_user(email="host@example.com", password="StrongPass123")
        self.guest = User.objects.create_user(email="guest@example.com", password="StrongPass123")
        self.listing = Listing.objects.create(
            host=self.host,
            title="Calangute cottage",
            description="Near the beach",
            city="Goa",
            address_area="Calangute",
            max_guests=2,
            house_rules="No parties",
        )
        Availability.objects.create(
            listing=self.listing,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 30),
        )

    def auth(self, user):
        login = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "StrongPass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_public_search_filters_city_and_dates(self):
        response = self.client.get(
            "/api/v1/listings/",
            {"city": "Goa", "check_in": "2026-11-10", "check_out": "2026-11-12", "guests": 2},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

        miss = self.client.get(
            "/api/v1/listings/",
            {"city": "Goa", "check_in": "2026-12-10", "check_out": "2026-12-12"},
        )
        self.assertEqual(miss.data["count"], 0)

    def test_owner_can_create_and_others_cannot_edit(self):
        self.auth(self.host)
        created = self.client.post(
            "/api/v1/listings/",
            {
                "title": "Pondy loft",
                "description": "Heritage street",
                "city": "Pondicherry",
                "address_area": "White Town",
                "max_guests": 3,
                "house_rules": "Quiet hours",
            },
            format="json",
        )
        self.assertEqual(created.status_code, 201)
        listing_id = created.data["id"]

        self.auth(self.guest)
        denied = self.client.patch(
            f"/api/v1/listings/{listing_id}/",
            {"title": "Hacked"},
            format="json",
        )
        self.assertEqual(denied.status_code, 403)
