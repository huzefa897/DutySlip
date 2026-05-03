from django.db import migrations, models


def sync_paid_status(apps, schema_editor):
    DutySlip = apps.get_model("api", "DutySlip")
    DutySlip.objects.filter(status="paid").update(
        status="finalised", payment_status="paid"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0007_car_outstation_rate_companycarrate_outstation_rate_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="dutyslip",
            name="payment_status",
            field=models.CharField(
                choices=[("unpaid", "Unpaid"), ("paid", "Paid")],
                default="unpaid",
                max_length=20,
            ),
        ),
        migrations.RunPython(sync_paid_status, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="dutyslip",
            name="status",
            field=models.CharField(
                choices=[("draft", "Draft"), ("finalised", "Finalised")],
                default="draft",
                max_length=20,
            ),
        ),
    ]
