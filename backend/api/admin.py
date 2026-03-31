from django.contrib import admin
from .models import Company, Car, DutySlip, DutySlipEntry
from .models import BusinessSettings
from .models import Company, Car, DutySlip, DutySlipEntry, BusinessSettings, CompanyCarRate

admin.site.register(Company)
admin.site.register(Car)
admin.site.register(DutySlip)
admin.site.register(DutySlipEntry)
admin.site.register(BusinessSettings)
admin.site.register(CompanyCarRate)