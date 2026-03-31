from django.contrib import admin
from .models import Company, Car, DutySlip, DutySlipEntry

admin.site.register(Company)
admin.site.register(Car)
admin.site.register(DutySlip)
admin.site.register(DutySlipEntry)