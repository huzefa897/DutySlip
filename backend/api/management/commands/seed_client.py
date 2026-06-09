"""
Seed a single client account for local development.

Usage:
    python manage.py seed_client --email saleemtourist@client --password admin@123

This command is idempotent:
- creates the user if missing
- updates the password if provided
- ensures the Django user is not staff/superuser
- ensures the linked UserProfile exists with role='client'
- assigns the client to existing companies, or creates a default demo company
"""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from api.models import Company, UserProfile


class Command(BaseCommand):
    help = "Seed a single client user for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            default="saleemtourist@client",
            help="Email address for the client account",
        )
        parser.add_argument(
            "--password",
            default="admin@123",
            help="Password for the client account",
        )
        parser.add_argument(
            "--first-name",
            default="Saleem",
            help="First name for the client account",
        )
        parser.add_argument(
            "--last-name",
            default="Client",
            help="Last name for the client account",
        )
        parser.add_argument(
            "--company-name",
            default="Client Demo Company",
            help="Demo company to assign to the client",
        )
        parser.add_argument(
            "--company-abn",
            default="CLIENT-001",
            help="ABN/identifier for the demo company",
        )
        parser.add_argument(
            "--no-assign-existing-companies",
            action="store_false",
            dest="assign_existing_companies",
            help="Only assign the default demo company instead of every existing company",
        )
        parser.set_defaults(assign_existing_companies=True)

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        password = options["password"]
        first_name = options["first_name"].strip()
        last_name = options["last_name"].strip()
        company_name = options["company_name"].strip()
        company_abn = options["company_abn"].strip()
        assign_existing_companies = options["assign_existing_companies"]

        if not email:
            raise CommandError("--email is required.")
        if not password:
            raise CommandError("--password is required.")
        if not company_name:
            raise CommandError("--company-name is required.")
        if not company_abn:
            raise CommandError("--company-abn is required.")

        user = User.objects.filter(email__iexact=email).first()
        created = user is None
        if created:
            user = User.objects.create(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_staff=False,
                is_superuser=False,
                is_active=True,
            )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created client user: {email}"))
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
            if user.is_staff:
                user.is_staff = False
                updated_fields.append("is_staff")
            if user.is_superuser:
                user.is_superuser = False
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
            defaults={"role": "client", "is_active": True},
        )
        profile_changed = False
        if profile.role != "client":
            profile.role = "client"
            profile_changed = True
        if not profile.is_active:
            profile.is_active = True
            profile_changed = True
        if profile_changed:
            profile.save(update_fields=["role", "is_active"])

        if assign_existing_companies and Company.objects.exists():
            assigned_companies = list(Company.objects.all())
            profile.companies.add(*assigned_companies)
        else:
            company, company_created = Company.objects.get_or_create(
                abn=company_abn,
                defaults={"name": company_name},
            )
            if not company_created and company.name != company_name:
                company.name = company_name
                company.save(update_fields=["name"])
            assigned_companies = [company]
            profile.companies.add(company)

        if profile_created:
            self.stdout.write(self.style.SUCCESS("Created matching client profile."))
        elif profile_changed:
            self.stdout.write(self.style.SUCCESS("Updated profile to client."))

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Seeded client account: {email} -> "
                f"{', '.join(company.name for company in assigned_companies)}"
            )
        )
