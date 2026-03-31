from django.db import models

class BusinessSettings(models.Model):
    name = models.CharField(max_length=255)
    abn = models.CharField(max_length=50)
    address = models.TextField()
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    currency = models.CharField(
        max_length=5,
        choices=[('USD', 'Dollar ($)'), ('INR', 'Rupee (₹)')],
        default='USD'
    )

    class Meta:
        verbose_name = 'Business Settings'
        verbose_name_plural = 'Business Settings'

    def __str__(self):
        return self.name

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

    def __str__(self):
        return self.name


class DutySlip(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('finalised', 'Unpaid / Finalised'),
        ('paid', 'Paid'),
    ]

    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='duty_slips')
    party_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return f"{self.party_name} - {self.company.name}"


class DutySlipEntry(models.Model):
    duty_slip = models.ForeignKey(
        DutySlip,
        on_delete=models.SET_NULL,
        related_name='entries',
        null=True,
        blank=True
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='entries'
    )
    party_name = models.CharField(max_length=255)
    date = models.DateField()
    car = models.ForeignKey(
        Car,
        on_delete=models.PROTECT
    )

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
        Company,
        on_delete=models.CASCADE,
        related_name='car_rates'
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='company_rates'
    )
    base_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    extra_km_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    extra_hr_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('company', 'car')  # one override per company+car combo

    def __str__(self):
        return f"{self.company.name} — {self.car.name}"