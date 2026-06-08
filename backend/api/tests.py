from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Company, Car, DutySlip, Invoice, UserProfile


class RBACTests(APITestCase):
    def setUp(self):
        # ── Setup Companies ──────────────────────────────────────────
        self.company_a = Company.objects.create(name="Company A", abn="ABN-A")
        self.company_b = Company.objects.create(name="Company B", abn="ABN-B")

        # ── Setup Admin ───────────────────────────────────────────────
        self.admin_user = User.objects.create_user(
            username="admin@test.com", email="admin@test.com", password="password"
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user, role="admin", is_active=True
        )

        # ── Setup Client (Company A only) ─────────────────────────────
        self.client_user = User.objects.create_user(
            username="client@test.com", email="client@test.com", password="password"
        )
        self.client_profile = UserProfile.objects.create(
            user=self.client_user, role="client", is_active=True
        )
        self.client_profile.companies.add(self.company_a)

        # ── Setup Data ────────────────────────────────────────────────
        self.car = Car.objects.create(
            name="Test Car", base_rate=100, extra_km_rate=10, extra_hr_rate=5
        )

        self.trip_a = DutySlip.objects.create(
            company=self.company_a,
            party_name="Guest A",
            date="2024-01-01",
            car=self.car,
            start_kms=0,
            end_kms=10,
        )
        self.trip_b = DutySlip.objects.create(
            company=self.company_b,
            party_name="Guest B",
            date="2024-01-01",
            car=self.car,
            start_kms=0,
            end_kms=10,
        )

        self.invoice_a = Invoice.objects.create(
            company=self.company_a, party_name="Guest A"
        )
        self.invoice_b = Invoice.objects.create(
            company=self.company_b, party_name="Guest B"
        )

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def set_auth(self, user):
        token = self.get_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # ── Test Admin Access ───────────────────────────────────────────
    def test_admin_can_see_everything(self):
        self.set_auth(self.admin_user)

        # Can see all companies
        res = self.client.get(reverse("company_list"))
        self.assertEqual(len(res.data), 2)

        # Can see all trips
        res = self.client.get(reverse("trip_list"))
        self.assertEqual(len(res.data), 2)

        # Can see all invoices
        res = self.client.get(reverse("invoice_list"))
        self.assertEqual(len(res.data), 2)

    def test_admin_can_write(self):
        self.set_auth(self.admin_user)
        res = self.client.post(
            reverse("car_list"),
            {
                "name": "Admin Car",
                "base_rate": 50,
                "extra_km_rate": 5,
                "extra_hr_rate": 2,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    # ── Test Client Access ──────────────────────────────────────────
    def test_client_scoped_to_company(self):
        self.set_auth(self.client_user)

        # Only sees Company A
        res = self.client.get(reverse("company_list"))
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], self.company_a.id)

        # Only sees Trip A
        res = self.client.get(reverse("trip_list"))
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], self.trip_a.id)

        # Only sees Invoice A
        res = self.client.get(reverse("invoice_list"))
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], self.invoice_a.id)

    def test_client_cannot_see_unauthorized_detail(self):
        self.set_auth(self.client_user)

        # Unauthorized company
        res = self.client.get(reverse("company_detail", args=[self.company_b.id]))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        # Unauthorized trip
        res = self.client.get(reverse("trip_detail", args=[self.trip_b.id]))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_client_cannot_write(self):
        self.set_auth(self.client_user)

        # Cannot create car
        res = self.client.post(reverse("car_list"), {"name": "Hacker Car"})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Cannot edit trip
        res = self.client.put(
            reverse("trip_detail", args=[self.trip_a.id]), {"party_name": "Edited"}
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Cannot delete invoice
        res = self.client.delete(reverse("invoice_detail", args=[self.invoice_a.id]))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # ── Test Deactivation ───────────────────────────────────────────
    def test_deactivated_user_blocked(self):
        self.client_profile.is_active = False
        self.client_profile.save()

        self.set_auth(self.client_user)
        res = self.client.get(reverse("company_list"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
