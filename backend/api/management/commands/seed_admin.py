"""
Seed a single admin account for local development.

Usage:
    python manage.py seed_admin --email saleemtourist@admin --password admin@123

This command is idempotent:
- creates the user if missing
- updates the password if provided
- ensures the Django user is a staff/superuser account
- ensures the linked UserProfile exists with role='admin'
"""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from api.models import UserProfile


class Command(BaseCommand):
    help = "Seed a single admin user for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            default="saleemtourist@admin",
            help="Email address for the admin account",
        )
        parser.add_argument(
            "--password",
            default="admin@123",
            help="Password for the admin account",
        )
        parser.add_argument(
            "--first-name",
            default="Saleem",
            help="First name for the admin account",
        )
        parser.add_argument(
            "--last-name",
            default="Tourist",
            help="Last name for the admin account",
        )

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        password = options["password"]
        first_name = options["first_name"].strip()
        last_name = options["last_name"].strip()

        if not email:
            raise CommandError("--email is required.")
        if not password:
            raise CommandError("--password is required.")

        user = User.objects.filter(email__iexact=email).first()
        created = user is None
        if created:
            user = User.objects.create(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_staff=True,
                is_superuser=True,
                is_active=True,
            )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created admin user: {email}"))
        else:
            updated_fields = []
            if user.email != email:
                user.email = email
                updated_fields.append("email")
            if user.username != email:
                user.username = email
                updated_fields.append("username")
            if user.first_name != first_name:
                user.first_name = first_name
                updated_fields.append("first_name")
            if user.last_name != last_name:
                user.last_name = last_name
                updated_fields.append("last_name")
            if not user.is_staff:
                user.is_staff = True
                updated_fields.append("is_staff")
            if not user.is_superuser:
                user.is_superuser = True
                updated_fields.append("is_superuser")
            if not user.is_active:
                user.is_active = True
                updated_fields.append("is_active")

            user.set_password(password)
            user.save()
            if updated_fields:
                self.stdout.write(self.style.SUCCESS(f"Updated existing user: {email}"))
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"User already existed; password refreshed: {email}"
                    )
                )

        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={"role": "admin", "is_active": True},
        )
        profile_changed = False
        if profile.role != "admin":
            profile.role = "admin"
            profile_changed = True
        if not profile.is_active:
            profile.is_active = True
            profile_changed = True
        if profile_changed:
            profile.save(update_fields=["role", "is_active"])

        if profile_created:
            self.stdout.write(self.style.SUCCESS("Created matching admin profile."))
        elif profile_changed:
            self.stdout.write(self.style.SUCCESS("Updated profile to admin."))

        self.stdout.write(self.style.SUCCESS(f"✓ Seeded admin account: {email}"))
