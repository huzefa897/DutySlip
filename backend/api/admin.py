from django.contrib import admin
from .models import Company, Car, Invoice, DutySlip, BusinessSettings, CompanyCarRate

admin.site.register(Company)
admin.site.register(Car)
admin.site.register(Invoice)
admin.site.register(DutySlip)
admin.site.register(BusinessSettings)
admin.site.register(CompanyCarRate)
