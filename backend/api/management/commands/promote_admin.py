"""
Usage:
    python manage.py promote_admin <email>

Creates a UserProfile with role='admin' for the given user. If the user
doesn't exist, creates one (prompting for a password). Idempotent: running
it again on an existing admin profile is a no-op.
"""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from api.models import UserProfile


class Command(BaseCommand):
    help = "Promote a user to Admin role (creates UserProfile if needed)"

    def add_arguments(self, parser):
        parser.add_argument(
            "email", type=str, help="Email address of the user to promote"
        )

    def handle(self, *args, **options):
        email = options["email"].strip().lower()

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            self.stdout.write(f"No user found with email '{email}'. Creating one...")
            password = self._prompt_password()
            user = User.objects.create_superuser(
                username=email, email=email, password=password
            )
            self.stdout.write(self.style.SUCCESS(f"Created user: {email}"))

        profile, created = UserProfile.objects.get_or_create(
            user=user, defaults={"role": "admin", "is_active": True}
        )
        if not created:
            if profile.role == "admin":
                self.stdout.write(
                    self.style.WARNING(f"{email} is already an admin. No changes made.")
                )
                return
            profile.role = "admin"
            profile.is_active = True
            profile.save(update_fields=["role", "is_active"])

        self.stdout.write(self.style.SUCCESS(f"✓ {email} is now an Admin."))

    def _prompt_password(self):
        import getpass

        while True:
            pw1 = getpass.getpass("Password: ")
            pw2 = getpass.getpass("Password (again): ")
            if pw1 != pw2:
                self.stderr.write("Passwords do not match. Try again.")
                continue
            if len(pw1) < 8:
                self.stderr.write("Password must be at least 8 characters.")
                continue
            return pw1
