import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0011_add_party_model"),
    ]

    operations = [
        migrations.AddField(
            model_name="dutyslip",
            name="party",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="trips",
                to="api.party",
            ),
        ),
    ]
