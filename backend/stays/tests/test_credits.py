from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from credits.services import available_credits, ledger_balance
from listings.models import Availability, Listing
from stays.models import StayRequest

User = get_user_model()


class CreditStayTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.host = User.objects.create_user(email="host@example.com", password="StrongPass123")
        self.guest = User.objects.create_user(email="guest@example.com", password="StrongPass123")
        self.other = User.objects.create_user(email="other@example.com", password="StrongPass123")
        self.listing = Listing.objects.create(
            host=self.host,
            title="Anjuna home",
            description="Quiet lane",
            city="Goa",
            address_area="Anjuna",
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
        return login.data["access"]

    def request_stay(self, check_in="2026-11-10", check_out="2026-11-12", guests_count=1):
        return self.client.post(
            "/api/v1/stay-requests/",
            {
                "listing": self.listing.id,
                "check_in": check_in,
                "check_out": check_out,
                "guests_count": guests_count,
                "message": "Hello",
            },
            format="json",
        )

    def test_insufficient_credits_rejected(self):
        self.auth(self.guest)
        # 4 nights * 1 guest = 4 credits, guest only has 2
        response = self.request_stay("2026-11-10", "2026-11-14", 1)
        self.assertEqual(response.status_code, 400)

    def test_cannot_request_own_listing(self):
        self.auth(self.host)
        response = self.request_stay()
        self.assertEqual(response.status_code, 400)

    def test_accept_reserves_and_double_accept_fails(self):
        self.auth(self.guest)
        created = self.request_stay()
        self.assertEqual(created.status_code, 201)
        stay_id = created.data["id"]
        self.assertEqual(available_credits(self.guest), 2)

        self.auth(self.host)
        accepted = self.client.post(f"/api/v1/stay-requests/{stay_id}/accept/")
        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(available_credits(self.guest), 0)

        again = self.client.post(f"/api/v1/stay-requests/{stay_id}/accept/")
        self.assertEqual(again.status_code, 400)

    def test_cancel_releases_credits(self):
        self.auth(self.guest)
        stay_id = self.request_stay().data["id"]
        self.auth(self.host)
        self.client.post(f"/api/v1/stay-requests/{stay_id}/accept/")
        self.assertEqual(available_credits(self.guest), 0)

        self.auth(self.guest)
        cancelled = self.client.post(f"/api/v1/stay-requests/{stay_id}/cancel/")
        self.assertEqual(cancelled.status_code, 200)
        self.assertEqual(available_credits(self.guest), 2)

    def test_overlap_rejected_on_accept(self):
        self.auth(self.guest)
        first = self.request_stay("2026-11-10", "2026-11-12").data["id"]
        self.auth(self.other)
        second = self.request_stay("2026-11-11", "2026-11-13").data["id"]

        self.auth(self.host)
        self.assertEqual(self.client.post(f"/api/v1/stay-requests/{first}/accept/").status_code, 200)
        overlap = self.client.post(f"/api/v1/stay-requests/{second}/accept/")
        self.assertEqual(overlap.status_code, 400)

    def test_complete_debits_guest_and_credits_host(self):
        self.auth(self.guest)
        stay_id = self.request_stay().data["id"]
        self.auth(self.host)
        self.client.post(f"/api/v1/stay-requests/{stay_id}/accept/")
        completed = self.client.post(f"/api/v1/stay-requests/{stay_id}/complete/")
        self.assertEqual(completed.status_code, 200)
        self.guest.refresh_from_db()
        self.host.refresh_from_db()
        self.assertEqual(ledger_balance(self.guest), 0)
        self.assertEqual(ledger_balance(self.host), 4)
        self.assertEqual(StayRequest.objects.get(pk=stay_id).status, StayRequest.Status.COMPLETED)

    def test_stranger_cannot_accept(self):
        self.auth(self.guest)
        stay_id = self.request_stay().data["id"]
        self.auth(self.other)
        denied = self.client.post(f"/api/v1/stay-requests/{stay_id}/accept/")
        self.assertEqual(denied.status_code, 403)
