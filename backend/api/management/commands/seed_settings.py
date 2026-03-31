from django.core.management.base import BaseCommand
from api.models import BusinessSettings


class Command(BaseCommand):
    help = 'Seed default business settings'

    def handle(self, *args, **kwargs):
        if BusinessSettings.objects.exists():
            self.stdout.write('Settings already exist.')
            return

        BusinessSettings.objects.create(
            name='SaleemTourist',
            abn='',
            address='19-4-370/A/13 ChiragAli Nagar, Bahadurpura, Hyderabad, Telangana 500064',
            phone='+91 9246365181',
            email='saleemtourist@gmail.com',
        )
        self.stdout.write(self.style.SUCCESS('Business settings created.'))