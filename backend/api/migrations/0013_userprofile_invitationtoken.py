import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0012_dutyslip_party_fk"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[("admin", "Admin"), ("client", "Client")],
                        default="client",
                        max_length=10,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "companies",
                    models.ManyToManyField(
                        blank=True, related_name="client_profiles", to="api.company"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="InvitationToken",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=254)),
                ("token", models.CharField(max_length=64, unique=True)),
                ("role", models.CharField(default="client", max_length=10)),
                (
                    "purpose",
                    models.CharField(
                        choices=[
                            ("invite", "Invite"),
                            ("password_reset", "Password Reset"),
                        ],
                        max_length=20,
                    ),
                ),
                ("used", models.BooleanField(default=False)),
                ("expires_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="invitations_sent",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
