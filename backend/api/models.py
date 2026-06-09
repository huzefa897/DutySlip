import secrets
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Company(models.Model):
    name = models.CharField(max_length=255)
    abn = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.name} (ABN: {self.abn})"


class Car(models.Model):
    name = models.CharField(max_length=100)
    base_rate = models.DecimalField(max_digits=10, decimal_places=2)
    extra_km_rate = models.DecimalField(max_digits=10, decimal_places=2)
    extra_hr_rate = models.DecimalField(max_digits=10, decimal_places=2)
    outstation_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class Party(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="parties"
    )
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = [("company", "name")]
        ordering = ["name"]

    def __str__(self):
        return self.name


class Invoice(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("finalised", "Finalised"),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
    ]
    INVOICE_TYPE_CHOICES = [
        ("regular", "Regular"),
        ("outstation", "Outstation"),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.PROTECT, related_name="invoices"
    )
    party = models.ForeignKey(
        "Party",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )
    party_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="unpaid"
    )
    invoice_type = models.CharField(
        max_length=20, choices=INVOICE_TYPE_CHOICES, default="regular"
    )

    def __str__(self):
        return f"{self.party_name} - {self.company.name}"


class DutySlip(models.Model):
    TRIP_TYPE_CHOICES = [
        ("regular", "Regular"),
        ("outstation", "Outstation"),
    ]

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        related_name="trips",
        null=True,
        blank=True,
    )
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="trips")
    party = models.ForeignKey(
        "Party", on_delete=models.SET_NULL, null=True, blank=True, related_name="trips"
    )
    party_name = models.CharField(max_length=255)
    trip_type = models.CharField(
        max_length=20, choices=TRIP_TYPE_CHOICES, default="regular"
    )
    date = models.DateField()
    car = models.ForeignKey(Car, on_delete=models.PROTECT)

    # KMs
    start_kms = models.DecimalField(max_digits=10, decimal_places=2)
    end_kms = models.DecimalField(max_digits=10, decimal_places=2)
    total_kms = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    extra_kms = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    extra_kms_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Time — optional for outstation
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    extra_hrs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    extra_hrs_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Outstation
    outstation_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Charges
    driver_bhatta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    parking = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Row total
    row_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.car.name} - {self.party_name} ({self.trip_type})"


class CompanyCarRate(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="car_rates"
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="company_rates")
    base_rate = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    extra_km_rate = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    extra_hr_rate = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    outstation_rate = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    class Meta:
        unique_together = ("company", "car")

    def __str__(self):
        return f"{self.company.name} — {self.car.name}"


class BusinessSettings(models.Model):
    name = models.CharField(max_length=255)
    abn = models.CharField(max_length=50)
    address = models.TextField()
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    logo = models.TextField(blank=True, null=True)
    currency = models.CharField(
        max_length=5,
        choices=[("USD", "Dollar ($)"), ("INR", "Rupee (₹)")],
        default="USD",
    )
    # GitHub backup config
    github_token = models.CharField(max_length=255, blank=True, null=True)
    github_username = models.CharField(max_length=100, blank=True, null=True)
    github_repo = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Business Settings"
        verbose_name_plural = "Business Settings"

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    ROLE_CHOICES = [("admin", "Admin"), ("client", "Client")]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="client")
    companies = models.ManyToManyField(
        Company, blank=True, related_name="client_profiles"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} ({self.role})"


class InvitationToken(models.Model):
    PURPOSE_CHOICES = [("invite", "Invite"), ("password_reset", "Password Reset")]

    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True)
    role = models.CharField(max_length=10, default="client")
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="invitations_sent",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at

    @classmethod
    def make(cls, email, purpose, role="client", created_by=None, hours=48):
        return cls.objects.create(
            email=email,
            token=secrets.token_urlsafe(48),
            purpose=purpose,
            role=role,
            expires_at=timezone.now() + timedelta(hours=hours),
            created_by=created_by,
        )

    def __str__(self):
        return f"{self.purpose} for {self.email}"
