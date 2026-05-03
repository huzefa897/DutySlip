from django.db import models


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


class DutySlip(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("finalised", "Finalised"),
        ("paid", "Paid"),
    ]
    SLIP_TYPE_CHOICES = [
        ("regular", "Regular"),
        ("outstation", "Outstation"),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.PROTECT, related_name="duty_slips"
    )
    party_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    slip_type = models.CharField(
        max_length=20, choices=SLIP_TYPE_CHOICES, default="regular"
    )

    def __str__(self):
        return f"{self.party_name} - {self.company.name}"


class DutySlipEntry(models.Model):
    ENTRY_TYPE_CHOICES = [
        ("regular", "Regular"),
        ("outstation", "Outstation"),
    ]

    duty_slip = models.ForeignKey(
        DutySlip,
        on_delete=models.SET_NULL,
        related_name="entries",
        null=True,
        blank=True,
    )
    company = models.ForeignKey(
        Company, on_delete=models.PROTECT, related_name="entries"
    )
    party_name = models.CharField(max_length=255)
    entry_type = models.CharField(
        max_length=20, choices=ENTRY_TYPE_CHOICES, default="regular"
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
        return f"{self.date} - {self.car.name} - {self.party_name} ({self.entry_type})"


class DutySlipEntryOutStation(models.Model):
    duty_slip = models.ForeignKey(
        DutySlip,
        on_delete=models.SET_NULL,
        related_name="out_station_entries",
        null=True,
        blank=True,
    )
    company = models.ForeignKey(
        Company, on_delete=models.PROTECT, related_name="out_station_entries"
    )
    party_name = models.CharField(max_length=255)
    date = models.DateField()
    car = models.ForeignKey(Car, on_delete=models.PROTECT)

    # KMs
    start_kms = models.DecimalField(max_digits=10, decimal_places=2)
    end_kms = models.DecimalField(max_digits=10, decimal_places=2)
    total_kms = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    extra_kms = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    extra_kms_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Time
    start_time = models.TimeField()
    end_time = models.TimeField()
    extra_hrs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    extra_hrs_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Charges
    driver_bhatta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    parking = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Row total
    row_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.car.name} - {self.party_name}"


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
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)
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
