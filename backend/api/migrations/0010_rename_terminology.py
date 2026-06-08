from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0009_logo_as_base64_text"),
    ]

    operations = [
        # 1. Rename DutySlip model → Invoice (frees up the name "DutySlip")
        migrations.RenameModel(
            old_name="DutySlip",
            new_name="Invoice",
        ),
        # 2. Rename DutySlipEntry model → DutySlip
        migrations.RenameModel(
            old_name="DutySlipEntry",
            new_name="DutySlip",
        ),
        # 3. Rename Invoice.slip_type → invoice_type
        migrations.RenameField(
            model_name="invoice",
            old_name="slip_type",
            new_name="invoice_type",
        ),
        # 4. Rename DutySlip.entry_type → trip_type
        migrations.RenameField(
            model_name="dutyslip",
            old_name="entry_type",
            new_name="trip_type",
        ),
        # 5. Rename DutySlip.duty_slip (FK to Invoice) → invoice
        migrations.RenameField(
            model_name="dutyslip",
            old_name="duty_slip",
            new_name="invoice",
        ),
        # Note: related_name changes (entries→trips, duty_slips→invoices) are
        # Python-level only and do not require a database migration.
    ]
