from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from weasyprint import HTML
import datetime
import json
import base64
import requests as http_requests

from .models import (
    Company,
    Car,
    DutySlip,
    DutySlipEntry,
    BusinessSettings,
    CompanyCarRate,
)
from .serializers import (
    CompanySerializer,
    CarSerializer,
    DutySlipSerializer,
    DutySlipEntrySerializer,
    BusinessSettingsSerializer,
    CompanyCarRateSerializer,
)
from .services import compute_entry, compute_duty_slip_total
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        return super().default(obj)


# ── Business Settings ─────────────────────────────────────────
@api_view(["GET", "PATCH"])
def business_settings(request):
    settings_obj = BusinessSettings.objects.first()
    if not settings_obj:
        return Response({"error": "Business settings not configured"}, status=404)

    if request.method == "GET":
        return Response(BusinessSettingsSerializer(settings_obj).data)

    serializer = BusinessSettingsSerializer(
        settings_obj, data=request.data, partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Companies ─────────────────────────────────────────────────
@api_view(["GET", "POST"])
def company_list(request):
    if request.method == "GET":
        companies = Company.objects.all()
        return Response(CompanySerializer(companies, many=True).data)

    serializer = CompanySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def company_detail(request, pk):
    try:
        company = Company.objects.get(pk=pk)
    except Company.DoesNotExist:
        return Response(
            {"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        return Response(CompanySerializer(company).data)

    if request.method == "PUT":
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        try:
            company.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {"error": "Cannot delete — company is used in existing records."},
                status=status.HTTP_400_BAD_REQUEST,
            )


@api_view(["GET"])
def company_parties(request, company_id):
    names = (
        DutySlipEntry.objects.filter(company_id=company_id)
        .values_list("party_name", flat=True)
        .distinct()
        .order_by("party_name")
    )
    return Response(list(names))


# ── Company Car Rates ─────────────────────────────────────────
@api_view(["GET", "POST"])
def company_car_rates(request, company_id):
    try:
        company = Company.objects.get(pk=company_id)
    except Company.DoesNotExist:
        return Response(
            {"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        rates = CompanyCarRate.objects.filter(company=company)
        return Response(CompanyCarRateSerializer(rates, many=True).data)

    car_id = request.data.get("car")

    def clean(val):
        return val if val not in [None, "", "null"] else None

    defaults = {
        "base_rate": clean(request.data.get("base_rate")),
        "extra_km_rate": clean(request.data.get("extra_km_rate")),
        "extra_hr_rate": clean(request.data.get("extra_hr_rate")),
    }

    rate, created = CompanyCarRate.objects.get_or_create(
        company=company, car_id=car_id, defaults=defaults
    )

    if not created:
        for field, value in defaults.items():
            setattr(rate, field, value)
        rate.save()

    return Response(
        CompanyCarRateSerializer(rate).data,
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


@api_view(["DELETE"])
def delete_company_car_rate(request, company_id, car_id):
    try:
        rate = CompanyCarRate.objects.get(company_id=company_id, car_id=car_id)
        rate.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except CompanyCarRate.DoesNotExist:
        return Response({"error": "Rate not found"}, status=status.HTTP_404_NOT_FOUND)


# ── Cars ──────────────────────────────────────────────────────
@api_view(["GET", "POST"])
def car_list(request):
    if request.method == "GET":
        cars = Car.objects.all()
        return Response(CarSerializer(cars, many=True).data)

    serializer = CarSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def car_detail(request, pk):
    try:
        car = Car.objects.get(pk=pk)
    except Car.DoesNotExist:
        return Response({"error": "Car not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(CarSerializer(car).data)

    if request.method == "PUT":
        serializer = CarSerializer(car, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        try:
            car.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {"error": "Cannot delete — car is used in existing entries."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ── DutySlipEntry ─────────────────────────────────────────────
@api_view(["GET", "POST"])
def entry_list(request):
    if request.method == "GET":
        entries = DutySlipEntry.objects.all().order_by("-date")
        return Response(DutySlipEntrySerializer(entries, many=True).data)

    serializer = DutySlipEntrySerializer(data=request.data)
    if serializer.is_valid():
        entry = serializer.save()
        entry = compute_entry(entry)
        entry.save()
        return Response(
            DutySlipEntrySerializer(entry).data, status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def entry_detail(request, pk):
    try:
        entry = DutySlipEntry.objects.get(pk=pk)
    except DutySlipEntry.DoesNotExist:
        return Response({"error": "Entry not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(DutySlipEntrySerializer(entry).data)

    if request.method == "PUT":
        serializer = DutySlipEntrySerializer(entry, data=request.data)
        if serializer.is_valid():
            entry = serializer.save()
            entry = compute_entry(entry)
            entry.save()
            if entry.duty_slip:
                compute_duty_slip_total(entry.duty_slip)
            return Response(DutySlipEntrySerializer(entry).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        duty_slip = entry.duty_slip
        entry.delete()
        if duty_slip:
            compute_duty_slip_total(duty_slip)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def duplicate_entry(request, pk):
    try:
        entry = DutySlipEntry.objects.get(pk=pk)
    except DutySlipEntry.DoesNotExist:
        return Response({"error": "Entry not found"}, status=status.HTTP_404_NOT_FOUND)

    new_entry = DutySlipEntry.objects.create(
        duty_slip=None,
        company=entry.company,
        party_name=entry.party_name,
        date=entry.date,
        car=entry.car,
        start_kms=entry.start_kms,
        end_kms=entry.end_kms,
        start_time=entry.start_time,
        end_time=entry.end_time,
        driver_bhatta=entry.driver_bhatta,
        parking=entry.parking,
        notes=entry.notes,
    )
    new_entry = compute_entry(new_entry)
    new_entry.save()
    return Response(
        DutySlipEntrySerializer(new_entry).data, status=status.HTTP_201_CREATED
    )


# ── DutySlip ──────────────────────────────────────────────────
@api_view(["GET", "POST"])
def dutyslip_list(request):
    if request.method == "GET":
        slips = DutySlip.objects.all().order_by("-created_at")
        return Response(DutySlipSerializer(slips, many=True).data)

    serializer = DutySlipSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "DELETE"])
def dutyslip_detail(request, pk):
    try:
        slip = DutySlip.objects.get(pk=pk)
    except DutySlip.DoesNotExist:
        return Response(
            {"error": "DutySlip not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        return Response(DutySlipSerializer(slip).data)

    if request.method == "DELETE":
        slip.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def assign_entries_to_dutyslip(request, pk):
    try:
        slip = DutySlip.objects.get(pk=pk)
    except DutySlip.DoesNotExist:
        return Response(
            {"error": "DutySlip not found"}, status=status.HTTP_404_NOT_FOUND
        )

    entry_ids = request.data.get("entry_ids", [])
    entries = DutySlipEntry.objects.filter(id__in=entry_ids)
    entries.update(duty_slip=slip)
    compute_duty_slip_total(slip)
    return Response(DutySlipSerializer(slip).data)


@api_view(["POST"])
def remove_entry_from_dutyslip(request, pk, entry_id):
    try:
        slip = DutySlip.objects.get(pk=pk)
        entry = DutySlipEntry.objects.get(pk=entry_id, duty_slip=slip)
    except (DutySlip.DoesNotExist, DutySlipEntry.DoesNotExist):
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    entry.duty_slip = None
    entry.save()
    compute_duty_slip_total(slip)
    return Response(DutySlipSerializer(slip).data)


@api_view(["PATCH"])
def update_dutyslip_status(request, pk):
    try:
        slip = DutySlip.objects.get(pk=pk)
    except DutySlip.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get("status")
    if new_status not in ["draft", "finalised", "paid"]:
        return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

    slip.status = new_status
    slip.save()
    return Response(DutySlipSerializer(slip).data)


# ── DutySlip ──────────────────────────────────────────────────────────────────


# ── Invoice PDF ───────────────────────────────────────────────
@api_view(["GET"])
def download_invoice_pdf(request, pk):
    try:
        slip = DutySlip.objects.select_related("company").get(pk=pk)
    except DutySlip.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    entries = (
        DutySlipEntry.objects.filter(duty_slip=slip)
        .select_related("car")
        .order_by("date")
    )

    biz = BusinessSettings.objects.first()
    currency = "₹" if biz and biz.currency == "INR" else "$"
    year = datetime.date.today().year
    invoice_ref = f"786/110/{year}{str(slip.id).zfill(3)}"
    logo_url = ""
    if biz and biz.logo:
        logo_url = request.build_absolute_uri(biz.logo.url)
    today = datetime.date.today().strftime("%d %B %Y")

    html_string = render_to_string(
        "invoice.html",
        {
            "slip": slip,
            "entries": entries,
            "settings": biz,
            "currency": currency,
            "invoice_ref": invoice_ref,
            "logo_url": logo_url,
            "today": today,
        },
    )

    pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="invoice-{invoice_ref}.pdf"'
    )
    return response


# ── Backup & Restore ──────────────────────────────────────────
def get_backup_data():
    data = {
        "version": "1.0",
        "exported_at": datetime.datetime.now().isoformat(),
        "companies": list(Company.objects.values()),
        "cars": list(Car.objects.values()),
        "company_car_rates": list(CompanyCarRate.objects.values()),
        "duty_slips": list(DutySlip.objects.values()),
        "entries": list(DutySlipEntry.objects.values()),
        "business_settings": list(BusinessSettings.objects.values()),
    }
    # serialize and deserialize to convert all Decimals and dates to JSON-safe types
    return json.loads(json.dumps(data, cls=DecimalEncoder))


def push_to_github(biz, data):
    token = biz.github_token
    username = biz.github_username
    repo = biz.github_repo
    filename = f"backups/{datetime.date.today()}-{datetime.datetime.now().strftime('%H%M%S')}.json"
    api_url = f"https://api.github.com/repos/{username}/{repo}/contents/{filename}"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    content = base64.b64encode(json.dumps(data, indent=2).encode("utf-8")).decode(
        "utf-8"
    )
    payload = {
        "message": f"backup: {datetime.date.today()} {datetime.datetime.now().strftime('%H:%M:%S')}",
        "content": content,
    }
    res = http_requests.put(api_url, headers=headers, json=payload)
    return res.status_code in [200, 201]


@api_view(["GET"])
def backup_database(request):
    data = get_backup_data()
    biz = BusinessSettings.objects.first()
    if biz and biz.github_token and biz.github_username and biz.github_repo:
        push_to_github(biz, data)
    response = JsonResponse(data, json_dumps_params={"indent": 2})
    response["Content-Disposition"] = (
        f'attachment; filename="dutyslip-backup-{datetime.date.today()}.json"'
    )
    return response


@api_view(["POST"])
def restore_database(request):
    try:
        backup = json.loads(request.body)
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON file."}, status=400)

    if backup.get("version") != "1.0":
        return Response({"error": "Incompatible backup version."}, status=400)

    try:
        DutySlipEntry.objects.all().delete()
        DutySlip.objects.all().delete()
        CompanyCarRate.objects.all().delete()
        Company.objects.all().delete()
        Car.objects.all().delete()
        BusinessSettings.objects.all().delete()

        for row in backup.get("companies", []):
            Company.objects.create(**row)
        for row in backup.get("cars", []):
            Car.objects.create(**row)
        for row in backup.get("company_car_rates", []):
            CompanyCarRate.objects.create(**row)
        for row in backup.get("duty_slips", []):
            DutySlip.objects.create(**row)
        for row in backup.get("entries", []):
            DutySlipEntry.objects.create(**row)
        for row in backup.get("business_settings", []):
            row.pop("logo", None)
            BusinessSettings.objects.create(**row)

        return Response(
            {
                "message": "Restore successful.",
                "summary": {
                    "companies": len(backup.get("companies", [])),
                    "cars": len(backup.get("cars", [])),
                    "duty_slips": len(backup.get("duty_slips", [])),
                    "entries": len(backup.get("entries", [])),
                },
            }
        )
    except Exception as e:
        return Response({"error": f"Restore failed: {str(e)}"}, status=500)


@api_view(["POST"])
def push_backup_github(request):
    biz = BusinessSettings.objects.first()
    if not biz or not biz.github_token:
        return Response({"error": "GitHub not configured in settings."}, status=400)

    data = get_backup_data()
    success = push_to_github(biz, data)

    if success:
        return Response({"message": "Backup pushed to GitHub successfully."})
    return Response(
        {"error": "Failed to push to GitHub. Check your token and repo name."},
        status=500,
    )


@api_view(["GET"])
def list_github_backups(request):
    biz = BusinessSettings.objects.first()
    if not biz or not biz.github_token:
        return Response({"error": "GitHub not configured."}, status=400)

    api_url = f"https://api.github.com/repos/{biz.github_username}/{biz.github_repo}/contents/backups"
    headers = {
        "Authorization": f"token {biz.github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    res = http_requests.get(api_url, headers=headers)
    if res.status_code != 200:
        return Response({"error": "Could not fetch backups from GitHub."}, status=500)

    files = [
        {
            "name": f["name"],
            "path": f["path"],
            "download_url": f["download_url"],
            "size": f["size"],
        }
        for f in sorted(res.json(), key=lambda x: x["name"], reverse=True)
    ]
    return Response(files)


@api_view(["POST"])
def restore_from_github(request):
    biz = BusinessSettings.objects.first()
    if not biz or not biz.github_token:
        return Response({"error": "GitHub not configured."}, status=400)

    download_url = request.data.get("download_url")
    if not download_url:
        return Response({"error": "No download_url provided."}, status=400)

    headers = {
        "Authorization": f"token {biz.github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    res = http_requests.get(download_url, headers=headers)
    if res.status_code != 200:
        return Response({"error": "Could not download backup from GitHub."}, status=500)

    try:
        backup = res.json()
    except Exception:
        return Response({"error": "Invalid backup file."}, status=400)

    # ── call restore logic directly (no fake request) ──────────
    return _do_restore(backup)


def _do_restore(backup):
    """Core restore logic — accepts a backup dict directly."""
    if backup.get("version") != "1.0":
        return Response({"error": "Incompatible backup version."}, status=400)

    try:
        DutySlipEntry.objects.all().delete()
        DutySlip.objects.all().delete()
        CompanyCarRate.objects.all().delete()
        Company.objects.all().delete()
        Car.objects.all().delete()
        BusinessSettings.objects.all().delete()

        for row in backup.get("companies", []):
            Company.objects.create(**row)
        for row in backup.get("cars", []):
            Car.objects.create(**row)
        for row in backup.get("company_car_rates", []):
            CompanyCarRate.objects.create(**row)
        for row in backup.get("duty_slips", []):
            DutySlip.objects.create(**row)
        for row in backup.get("entries", []):
            DutySlipEntry.objects.create(**row)

        settings_rows = backup.get("business_settings", [])
        if settings_rows:
            for row in settings_rows:
                row.pop("logo", None)
                BusinessSettings.objects.create(**row)
        else:
            BusinessSettings.objects.create(
                name="", abn="", address="", phone="", email=""
            )

        # ── Reset PostgreSQL sequences after restore ──────────────
        from django.db import connection

        with connection.cursor() as cursor:
            tables = [
                "api_company",
                "api_car",
                "api_dutyslip",
                "api_dutyslipentry",
                "api_companycarrate",
                "api_businesssettings",
            ]
            for table in tables:
                cursor.execute(
                    f"SELECT setval('{table}_id_seq', COALESCE((SELECT MAX(id) FROM {table}), 1))"
                )

        return Response(
            {
                "message": "Restore successful.",
                "summary": {
                    "companies": len(backup.get("companies", [])),
                    "cars": len(backup.get("cars", [])),
                    "duty_slips": len(backup.get("duty_slips", [])),
                    "entries": len(backup.get("entries", [])),
                },
            }
        )
    except Exception as e:
        return Response({"error": f"Restore failed: {str(e)}"}, status=500)
