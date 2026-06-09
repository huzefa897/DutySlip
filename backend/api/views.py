from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from weasyprint import HTML
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as XLImage
from openpyxl.worksheet.page import PageMargins
from io import BytesIO
import datetime
import json
import base64
import requests as http_requests

from django.contrib.auth.models import User
from django.utils.text import slugify

from .models import (
    Company,
    Car,
    Invoice,
    DutySlip,
    BusinessSettings,
    CompanyCarRate,
    Party,
    UserProfile,
)
from .serializers import (
    CompanySerializer,
    CarSerializer,
    InvoiceSerializer,
    DutySlipSerializer,
    BusinessSettingsSerializer,
    CompanyCarRateSerializer,
)
from .services import compute_trip, compute_invoice_total
from .permissions import admin_only, admin_or_client_readonly, get_scoped_company_ids
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
@admin_or_client_readonly
def business_settings(request):
    settings_obj = BusinessSettings.objects.first()
    if not settings_obj:
        return Response({"error": "Business settings not configured"}, status=404)

    if request.method == "GET":
        return Response(BusinessSettingsSerializer(settings_obj).data)

    logo_file = request.FILES.get("logo")
    data = request.data.dict() if hasattr(request.data, "dict") else dict(request.data)
    data.pop("logo", None)

    serializer = BusinessSettingsSerializer(settings_obj, data=data, partial=True)
    if serializer.is_valid():
        obj = serializer.save()
        if logo_file:
            mime = logo_file.content_type or "image/png"
            encoded = base64.b64encode(logo_file.read()).decode("utf-8")
            obj.logo = f"data:{mime};base64,{encoded}"
            obj.save(update_fields=["logo"])
        return Response(BusinessSettingsSerializer(obj).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Companies ─────────────────────────────────────────────────
def make_company_client_email(company_name):
    local_part = slugify(company_name).replace("-", "")
    if not local_part:
        local_part = "company"
    return f"{local_part}@client.com"


def ensure_company_client_account(company):
    email = make_company_client_email(company.name)
    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        user = User.objects.create(
            username=email,
            email=email,
            first_name=company.name,
            is_staff=False,
            is_superuser=False,
            is_active=True,
        )
    else:
        user.username = email
        user.email = email
        user.first_name = company.name
        user.is_staff = False
        user.is_superuser = False
        user.is_active = True

    user.set_password("client@123")
    user.save()

    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={"role": "client", "is_active": True},
    )
    changed = False
    if profile.role != "client":
        profile.role = "client"
        changed = True
    if not profile.is_active:
        profile.is_active = True
        changed = True
    if changed:
        profile.save(update_fields=["role", "is_active"])
    profile.companies.add(company)
    return user


@api_view(["GET", "POST"])
@admin_or_client_readonly
def company_list(request):
    if request.method == "GET":
        company_ids = get_scoped_company_ids(request)
        companies = Company.objects.all()
        if company_ids is not None:
            companies = companies.filter(id__in=company_ids)
        return Response(CompanySerializer(companies, many=True).data)

    serializer = CompanySerializer(data=request.data)
    if serializer.is_valid():
        company = serializer.save()
        ensure_company_client_account(company)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@admin_or_client_readonly
def company_detail(request, pk):
    try:
        company = Company.objects.get(pk=pk)
    except Company.DoesNotExist:
        return Response(
            {"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND
        )

    company_ids = get_scoped_company_ids(request)
    if company_ids is not None and company.id not in company_ids:
        return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)

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


@api_view(["GET", "POST"])
@admin_or_client_readonly
def company_parties(request, company_id):
    company_ids = get_scoped_company_ids(request)
    if company_ids is not None and company_id not in company_ids:
        return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    company = get_object_or_404(Company, pk=company_id)
    if request.method == "GET":
        parties = Party.objects.filter(company=company)
        return Response([{"id": p.id, "name": p.name} for p in parties])
    name = request.data.get("name", "").strip()
    if not name:
        return Response({"name": ["This field is required."]}, status=400)
    party, created = Party.objects.get_or_create(company=company, name=name)
    return Response(
        {"id": party.id, "name": party.name}, status=201 if created else 200
    )


@api_view(["GET", "POST"])
@admin_or_client_readonly
def company_invoice_parties(request, company_id):
    company_ids = get_scoped_company_ids(request)
    if company_ids is not None and company_id not in company_ids:
        return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    company = get_object_or_404(Company, pk=company_id)
    if request.method == "GET":
        parties = Party.objects.filter(company=company)
        return Response([{"id": p.id, "name": p.name} for p in parties])
    name = request.data.get("name", "").strip()
    if not name:
        return Response({"name": ["This field is required."]}, status=400)
    party, created = Party.objects.get_or_create(company=company, name=name)
    return Response(
        {"id": party.id, "name": party.name}, status=201 if created else 200
    )


# ── Company Car Rates ─────────────────────────────────────────
@api_view(["GET", "POST"])
@admin_or_client_readonly
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
@admin_only
def delete_company_car_rate(request, company_id, car_id):
    try:
        rate = CompanyCarRate.objects.get(company_id=company_id, car_id=car_id)
        rate.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except CompanyCarRate.DoesNotExist:
        return Response({"error": "Rate not found"}, status=status.HTTP_404_NOT_FOUND)


# ── Cars ──────────────────────────────────────────────────────
@api_view(["GET", "POST"])
@admin_or_client_readonly
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
@admin_or_client_readonly
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
                {"error": "Cannot delete — car is used in existing trips."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ── DutySlip (Trip) ───────────────────────────────────────────
@api_view(["GET", "POST"])
@admin_or_client_readonly
def trip_list(request):
    if request.method == "GET":
        company_ids = get_scoped_company_ids(request)
        trips = DutySlip.objects.all().order_by("-date")

        # Filter by specific company if provided
        target_company = request.query_params.get("company")
        if target_company:
            trips = trips.filter(company_id=target_company)

        if company_ids is not None:
            trips = trips.filter(company_id__in=company_ids)
        return Response(DutySlipSerializer(trips, many=True).data)

    serializer = DutySlipSerializer(data=request.data)
    if serializer.is_valid():
        trip = serializer.save()
        if trip.party:
            trip.party_name = trip.party.name
        trip = compute_trip(trip)
        trip.save()
        return Response(DutySlipSerializer(trip).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@admin_or_client_readonly
def trip_detail(request, pk):
    try:
        trip = DutySlip.objects.get(pk=pk)
    except DutySlip.DoesNotExist:
        return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)

    company_ids = get_scoped_company_ids(request)
    if company_ids is not None and trip.company_id not in company_ids:
        return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(DutySlipSerializer(trip).data)

    if request.method == "PUT":
        serializer = DutySlipSerializer(trip, data=request.data)
        if serializer.is_valid():
            trip = serializer.save()
            if trip.party:
                trip.party_name = trip.party.name
            trip = compute_trip(trip)
            trip.save()
            if trip.invoice:
                compute_invoice_total(trip.invoice)
            return Response(DutySlipSerializer(trip).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        invoice = trip.invoice
        trip.delete()
        if invoice:
            compute_invoice_total(invoice)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@admin_only
def duplicate_trip(request, pk):
    try:
        trip = DutySlip.objects.get(pk=pk)
    except DutySlip.DoesNotExist:
        return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)

    new_trip = DutySlip.objects.create(
        invoice=None,
        company=trip.company,
        party=trip.party,
        party_name=trip.party_name,
        trip_type=trip.trip_type,
        date=trip.date,
        car=trip.car,
        start_kms=trip.start_kms,
        end_kms=trip.end_kms,
        start_time=trip.start_time,
        end_time=trip.end_time,
        driver_bhatta=trip.driver_bhatta,
        parking=trip.parking,
        notes=trip.notes,
    )
    new_trip = compute_trip(new_trip)
    new_trip.save()
    return Response(DutySlipSerializer(new_trip).data, status=status.HTTP_201_CREATED)


# ── Invoice ───────────────────────────────────────────────────
@api_view(["GET", "POST"])
@admin_or_client_readonly
def invoice_list(request):
    if request.method == "GET":
        company_ids = get_scoped_company_ids(request)
        invoices = Invoice.objects.all().order_by("-created_at")

        # Filter by specific company if provided
        target_company = request.query_params.get("company")
        if target_company:
            invoices = invoices.filter(company_id=target_company)

        if company_ids is not None:
            invoices = invoices.filter(company_id__in=company_ids)
        return Response(InvoiceSerializer(invoices, many=True).data)

    serializer = InvoiceSerializer(data=request.data)
    if serializer.is_valid():
        invoice = serializer.save()
        if invoice.party:
            invoice.party_name = invoice.party.name
            invoice.save(update_fields=["party_name"])
        return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "DELETE"])
@admin_or_client_readonly
def invoice_detail(request, pk):
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        return Response(
            {"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND
        )

    company_ids = get_scoped_company_ids(request)
    if company_ids is not None and invoice.company_id not in company_ids:
        return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(InvoiceSerializer(invoice).data)

    if request.method == "DELETE":
        invoice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@admin_only
def assign_trips_to_invoice(request, pk):
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        return Response(
            {"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND
        )

    trip_ids = request.data.get("trip_ids", [])
    trips = DutySlip.objects.filter(id__in=trip_ids)

    mismatched = trips.exclude(trip_type=invoice.invoice_type)
    if mismatched.exists():
        return Response(
            {"error": "Selected trips must match the invoice type."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    trips.update(invoice=invoice)
    compute_invoice_total(invoice)
    return Response(InvoiceSerializer(invoice).data)


@api_view(["POST"])
@admin_only
def remove_trip_from_invoice(request, pk, trip_id):
    try:
        invoice = Invoice.objects.get(pk=pk)
        trip = DutySlip.objects.get(pk=trip_id, invoice=invoice)
    except (Invoice.DoesNotExist, DutySlip.DoesNotExist):
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    trip.invoice = None
    trip.save()
    compute_invoice_total(invoice)
    return Response(InvoiceSerializer(invoice).data)


@api_view(["PATCH"])
@admin_only
def update_invoice_status(request, pk):
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get("status")
    if new_status not in ["draft", "finalised"]:
        return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

    invoice.status = new_status
    invoice.save()
    return Response(InvoiceSerializer(invoice).data)


@api_view(["PATCH"])
@admin_only
def update_invoice_payment_status(request, pk):
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get("payment_status")
    if new_status not in ["unpaid", "paid"]:
        return Response(
            {"error": "Invalid payment status"}, status=status.HTTP_400_BAD_REQUEST
        )

    invoice.payment_status = new_status
    invoice.save()
    return Response(InvoiceSerializer(invoice).data)


# ── Excel helpers ─────────────────────────────────────────────


def _calc_total_hrs(trip):
    """Return total trip hours for regular trips; 0 for outstation."""
    if not trip.start_time or not trip.end_time:
        return Decimal("0")
    s = datetime.datetime.combine(trip.date, trip.start_time)
    e = datetime.datetime.combine(trip.date, trip.end_time)
    if e < s:
        e += datetime.timedelta(days=1)
    return Decimal(str(round((e - s).total_seconds() / 3600, 2)))


def _amount_to_words(amount):
    """Convert a numeric amount to Indian-English words (Rupees)."""
    ONES = [
        "",
        "One",
        "Two",
        "Three",
        "Four",
        "Five",
        "Six",
        "Seven",
        "Eight",
        "Nine",
        "Ten",
        "Eleven",
        "Twelve",
        "Thirteen",
        "Fourteen",
        "Fifteen",
        "Sixteen",
        "Seventeen",
        "Eighteen",
        "Nineteen",
    ]
    TENS = [
        "",
        "",
        "Twenty",
        "Thirty",
        "Forty",
        "Fifty",
        "Sixty",
        "Seventy",
        "Eighty",
        "Ninety",
    ]

    def below_1000(n):
        if n == 0:
            return ""
        if n < 20:
            return ONES[n]
        if n < 100:
            rest = ONES[n % 10]
            return TENS[n // 10] + (" " + rest if rest else "")
        rest = below_1000(n % 100)
        return ONES[n // 100] + " Hundred" + (" And " + rest if rest else "")

    def to_words(n):
        if n == 0:
            return "Zero"
        parts = []
        for label, divisor in [
            ("Crore", 10_000_000),
            ("Lakh", 100_000),
            ("Thousand", 1_000),
        ]:
            if n >= divisor:
                parts.append(below_1000(n // divisor) + " " + label)
                n %= divisor
        if n:
            parts.append(below_1000(n))
        return " ".join(parts)

    total = float(amount)
    rupees = int(total)
    paise = round((total - rupees) * 100)
    result = to_words(rupees) + " Rupees"
    if paise:
        result += " And " + to_words(paise) + " Paise"
    return result + " Only"


def _build_invoice_html(
    invoice, trips, biz, currency, invoice_ref, logo_url, today, request_base_url
):
    html_string = render_to_string(
        "invoice.html",
        {
            "invoice": invoice,
            "trips": trips,
            "settings": biz,
            "currency": currency,
            "invoice_ref": invoice_ref,
            "logo_url": logo_url,
            "today": today,
        },
    )
    return HTML(string=html_string, base_url=request_base_url).render()


# ── Invoice PDF ───────────────────────────────────────────────
@api_view(["GET"])
@admin_or_client_readonly
def download_invoice_pdf(request, pk):
    try:
        invoice = Invoice.objects.select_related("company").get(pk=pk)
    except Invoice.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    company_ids = get_scoped_company_ids(request)
    if company_ids is not None and invoice.company_id not in company_ids:
        return Response({"error": "Not found."}, status=404)

    trips = (
        DutySlip.objects.filter(invoice=invoice).select_related("car").order_by("date")
    )
    trips_with_totals = []
    for trip in trips:
        trip.total_hrs = _calc_total_hrs(trip)
        trips_with_totals.append(trip)

    biz = BusinessSettings.objects.first()
    currency = "₹" if biz and biz.currency == "INR" else "$"
    year = datetime.date.today().year
    invoice_ref = f"786/110/{year}{str(invoice.id).zfill(3)}"
    logo_url = biz.logo if biz and biz.logo else ""
    today = datetime.date.today().strftime("%d %B %Y")

    pdf = _build_invoice_html(
        invoice,
        trips_with_totals,
        biz,
        currency,
        invoice_ref,
        logo_url,
        today,
        request.build_absolute_uri(),
    ).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="invoice-{invoice_ref}.pdf"'
    )
    return response


# ── Invoice Excel helpers ──────────────────────────────────────


def _build_invoice_sheet(ws, invoice, trips, biz, currency, invoice_ref, company_rates):
    """Populate ws with the full invoice layout (header, table, totals, signature)."""
    LAST_COL = "M"
    N_COLS = 13
    DARK_FILL = PatternFill("solid", fgColor="1A1A2E")
    STRIPE_FILL = PatternFill("solid", fgColor="F5F5F5")
    WHITE_FILL = PatternFill("solid", fgColor="FFFFFF")
    CENTER = Alignment(horizontal="center", vertical="center")
    LEFT_AL = Alignment(horizontal="left", vertical="center")
    RIGHT_AL = Alignment(horizontal="right", vertical="center")
    GRAY_FONT = Font(size=10, color="555555")
    CURRENCY_FMT = "#,##0.00"
    NUM_FMT = "#,##0.00"

    def _thin_border():
        t = Side(style="thin")
        return Border(left=t, right=t, top=t, bottom=t)

    def _bottom_only():
        return Border(bottom=Side(style="thin"))

    def set_merged(
        cell_range, value, font=None, align=None, fill=None, border=None, fmt=None
    ):
        ws.merge_cells(cell_range)
        cell = ws[cell_range.split(":")[0]]
        cell.value = value
        if font:
            cell.font = font
        if align:
            cell.alignment = align
        if fill:
            cell.fill = fill
        if border:
            cell.border = border
        if fmt:
            cell.number_format = fmt

    def write_data_cell(row, col, value, fmt=None, row_fill=None):
        cell = ws.cell(row=row, column=col, value=value)
        cell.border = _thin_border()
        cell.alignment = LEFT_AL if col <= 2 else RIGHT_AL
        if fmt:
            cell.number_format = fmt
        if row_fill:
            cell.fill = row_fill

    # ── Section 1: Company Header ────────────────────────────────
    ws.row_dimensions[1].height = 4

    has_logo = False
    if biz and biz.logo and biz.logo.startswith("data:"):
        try:
            _, b64data = biz.logo.split(",", 1)
            img_bytes = base64.b64decode(b64data)
            img = XLImage(BytesIO(img_bytes))
            img.height = 110
            img.width = 110
            ws.add_image(img, "A2")
            ws.row_dimensions[2].height = 84
            has_logo = True
        except Exception:
            pass
    if not has_logo:
        ws.row_dimensions[2].height = 4

    set_merged(
        f"A3:{LAST_COL}3",
        biz.name if biz else "",
        font=Font(bold=True, size=18),
        align=CENTER,
    )
    ws.row_dimensions[3].height = 30

    set_merged(
        f"A4:{LAST_COL}4", biz.address if biz else "", font=GRAY_FONT, align=CENTER
    )
    ws.row_dimensions[4].height = 14

    set_merged(
        f"A5:{LAST_COL}5", biz.phone if biz else "", font=GRAY_FONT, align=CENTER
    )
    ws.row_dimensions[5].height = 14

    set_merged(
        f"A6:{LAST_COL}6",
        f"ABN: {biz.abn}" if biz and biz.abn else "",
        font=GRAY_FONT,
        align=CENTER,
    )
    ws.row_dimensions[6].height = 14

    for col in range(1, N_COLS + 1):
        ws.cell(row=7, column=col).border = _bottom_only()
    ws.row_dimensions[7].height = 4
    ws.row_dimensions[8].height = 10

    # ── Section 2: Customer + Invoice Meta (rows 9–11) ───────────
    set_merged("A9:F9", "To:", font=Font(bold=True, size=10), align=LEFT_AL)
    set_merged(
        "H9:M9",
        f"Invoice #: {invoice_ref}",
        font=Font(bold=True, size=10),
        align=RIGHT_AL,
    )

    set_merged(
        "A10:F10", invoice.company.name, font=Font(bold=True, size=11), align=LEFT_AL
    )
    set_merged(
        "H10:M10",
        f"Date: {invoice.created_at.strftime('%d/%m/%Y')}",
        font=Font(size=10),
        align=RIGHT_AL,
    )

    if invoice.company.abn:
        set_merged(
            "A11:F11", f"ABN: {invoice.company.abn}", font=GRAY_FONT, align=LEFT_AL
        )
    set_merged(
        "H11:M11",
        f"Payment: {invoice.payment_status.capitalize()}",
        font=Font(size=10),
        align=RIGHT_AL,
    )

    ws.row_dimensions[12].height = 8

    # ── Section 3: Guest Name Row (row 13) ───────────────────────
    set_merged(
        "A13:M13",
        f"Guest Name: {invoice.party_name}",
        font=Font(bold=True, size=10),
        align=LEFT_AL,
    )

    ws.row_dimensions[14].height = 8

    # ── Section 4: Trip Table ─────────────────────────────────────
    TABLE_ROW = 15
    HEADERS = [
        "Date",
        "Car Name",
        "Start KMs",
        "End KMs",
        "Total KMs",
        "Extra KMs",
        "Total Hrs",
        "Extra Hrs Amt",
        "Extra KMs Amt",
        "Driver Bhatta",
        "Basic Rate",
        "Parking",
        "Total Amount",
    ]
    for col, hdr in enumerate(HEADERS, start=1):
        cell = ws.cell(row=TABLE_ROW, column=col)
        cell.value = hdr
        cell.font = Font(bold=True, color="FFFFFF", size=9)
        cell.fill = DARK_FILL
        cell.alignment = CENTER
        cell.border = _thin_border()
    ws.row_dimensions[TABLE_ROW].height = 18

    data_row = TABLE_ROW + 1
    for idx, trip in enumerate(trips):
        cr = company_rates.get(trip.car_id)
        base_rate = (
            cr.base_rate if (cr and cr.base_rate is not None) else trip.car.base_rate
        )
        total_hrs = _calc_total_hrs(trip)
        row_fill = STRIPE_FILL if idx % 2 == 1 else None

        write_data_cell(data_row, 1, trip.date.strftime("%d/%m/%Y"), None, row_fill)
        write_data_cell(data_row, 2, trip.car.name, None, row_fill)
        write_data_cell(data_row, 3, float(trip.start_kms), NUM_FMT, row_fill)
        write_data_cell(data_row, 4, float(trip.end_kms), NUM_FMT, row_fill)
        write_data_cell(data_row, 5, float(trip.total_kms), NUM_FMT, row_fill)
        write_data_cell(data_row, 6, float(trip.extra_kms), NUM_FMT, row_fill)
        write_data_cell(data_row, 7, float(total_hrs), NUM_FMT, row_fill)
        write_data_cell(
            data_row, 8, float(trip.extra_hrs_amount), CURRENCY_FMT, row_fill
        )
        write_data_cell(
            data_row, 9, float(trip.extra_kms_amount), CURRENCY_FMT, row_fill
        )
        write_data_cell(data_row, 10, float(trip.driver_bhatta), CURRENCY_FMT, row_fill)
        write_data_cell(data_row, 11, float(base_rate), CURRENCY_FMT, row_fill)
        write_data_cell(data_row, 12, float(trip.parking), CURRENCY_FMT, row_fill)
        write_data_cell(data_row, 13, float(trip.row_total), CURRENCY_FMT, row_fill)
        ws.row_dimensions[data_row].height = 16
        data_row += 1

    last_data_row = data_row - 1

    # ── Section 5: Grand Total ────────────────────────────────────
    ws.row_dimensions[last_data_row + 1].height = 6
    total_row = last_data_row + 2

    set_merged(
        f"A{total_row}:F{total_row}",
        _amount_to_words(invoice.grand_total),
        font=Font(italic=True, size=10),
        align=LEFT_AL,
    )
    ws.row_dimensions[total_row].height = 22

    m_side = Side(style="medium")
    for c in range(8, N_COLS + 1):
        cell = ws.cell(row=total_row, column=c)
        cell.fill = WHITE_FILL
        cell.border = Border(
            left=m_side if c == 8 else None,
            right=m_side if c == N_COLS else None,
            top=m_side,
            bottom=m_side,
        )
    ws.merge_cells(f"H{total_row}:{LAST_COL}{total_row}")
    gt_cell = ws[f"H{total_row}"]
    gt_cell.value = f"Grand Total: {currency}{float(invoice.grand_total):,.2f}"
    gt_cell.font = Font(bold=True, size=13)
    gt_cell.alignment = RIGHT_AL

    # ── Section 6: Signature ──────────────────────────────────────
    ws.row_dimensions[total_row + 1].height = 8
    ws.row_dimensions[total_row + 2].height = 8
    sig_row = total_row + 3

    set_merged(
        f"H{sig_row}:{LAST_COL}{sig_row}",
        f"For {biz.name if biz else ''}",
        font=Font(bold=True, size=10),
        align=RIGHT_AL,
    )

    for gap in range(1, 4):
        ws.row_dimensions[sig_row + gap].height = 18

    prop_row = sig_row + 4
    set_merged(
        f"H{prop_row}:{LAST_COL}{prop_row}",
        "(Proprietor)",
        font=Font(size=10),
        align=RIGHT_AL,
    )

    last_row = prop_row

    # ── Column widths + hide unused area ─────────────────────────
    col_widths = [12, 18, 11, 11, 11, 10, 10, 13, 13, 13, 12, 10, 14]
    for i, w in enumerate(col_widths, start=1):
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w

    ws.sheet_view.showGridLines = False
    for i in range(N_COLS + 1, N_COLS + 50):
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].hidden = True
    for r in range(last_row + 1, last_row + 60):
        ws.row_dimensions[r].hidden = True

    # ── Print setup (A4 landscape) ────────────────────────────────
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = 9  # A4
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.print_area = f"A1:{LAST_COL}{last_row}"
    ws.page_margins = PageMargins(left=0.5, right=0.5, top=0.75, bottom=0.75)


def _build_trips_sheet(ws, trips, biz, currency, report_title, report_date):
    LAST_COL = "K"
    N_COLS = 11
    DARK_FILL = PatternFill("solid", fgColor="1A1A2E")
    STRIPE_FILL = PatternFill("solid", fgColor="F5F5F5")
    WHITE_FILL = PatternFill("solid", fgColor="FFFFFF")
    CENTER = Alignment(horizontal="center", vertical="center")
    LEFT_AL = Alignment(horizontal="left", vertical="center")
    RIGHT_AL = Alignment(horizontal="right", vertical="center")
    GRAY_FONT = Font(size=10, color="555555")
    CURRENCY_FMT = "#,##0.00"
    NUM_FMT = "#,##0.00"

    def _thin_border():
        t = Side(style="thin")
        return Border(left=t, right=t, top=t, bottom=t)

    def _bottom_only():
        return Border(bottom=Side(style="thin"))

    def set_merged(
        cell_range, value, font=None, align=None, fill=None, border=None, fmt=None
    ):
        ws.merge_cells(cell_range)
        cell = ws[cell_range.split(":")[0]]
        cell.value = value
        if font:
            cell.font = font
        if align:
            cell.alignment = align
        if fill:
            cell.fill = fill
        if border:
            cell.border = border
        if fmt:
            cell.number_format = fmt

    def write_data_cell(row, col, value, fmt=None, row_fill=None):
        cell = ws.cell(row=row, column=col, value=value)
        cell.border = _thin_border()
        cell.alignment = LEFT_AL if col <= 5 else RIGHT_AL
        if fmt:
            cell.number_format = fmt
        if row_fill:
            cell.fill = row_fill

    ws.row_dimensions[1].height = 4

    has_logo = False
    if biz and biz.logo and biz.logo.startswith("data:"):
        try:
            _, b64data = biz.logo.split(",", 1)
            img_bytes = base64.b64decode(b64data)
            img = XLImage(BytesIO(img_bytes))
            img.height = 90
            img.width = 90
            ws.add_image(img, "A2")
            ws.row_dimensions[2].height = 70
            has_logo = True
        except Exception:
            pass
    if not has_logo:
        ws.row_dimensions[2].height = 4

    set_merged(
        f"A3:{LAST_COL}3",
        biz.name if biz else "",
        font=Font(bold=True, size=18),
        align=CENTER,
    )
    ws.row_dimensions[3].height = 28
    set_merged(
        f"A4:{LAST_COL}4", biz.address if biz else "", font=GRAY_FONT, align=CENTER
    )
    ws.row_dimensions[4].height = 14
    set_merged(
        f"A5:{LAST_COL}5", biz.phone if biz else "", font=GRAY_FONT, align=CENTER
    )
    ws.row_dimensions[5].height = 14
    set_merged(
        f"A6:{LAST_COL}6",
        f"ABN: {biz.abn}" if biz and biz.abn else "",
        font=GRAY_FONT,
        align=CENTER,
    )
    ws.row_dimensions[6].height = 14

    for col in range(1, N_COLS + 1):
        ws.cell(row=7, column=col).border = _bottom_only()
    ws.row_dimensions[7].height = 4
    ws.row_dimensions[8].height = 10

    set_merged("A9:F9", report_title, font=Font(bold=True, size=11), align=LEFT_AL)
    set_merged("H9:K9", report_date, font=Font(size=10), align=RIGHT_AL)
    set_merged(
        "A10:K10",
        "Trips exported from the current database state",
        font=GRAY_FONT,
        align=LEFT_AL,
    )

    ws.row_dimensions[11].height = 8

    TABLE_ROW = 12
    HEADERS = [
        "Date",
        "Trip Type",
        "Party",
        "Company",
        "Car",
        "Total KMs",
        "Extra Hrs",
        "Bhatta",
        "Parking",
        "Invoice",
        "Row Total",
    ]
    for col, hdr in enumerate(HEADERS, start=1):
        cell = ws.cell(row=TABLE_ROW, column=col)
        cell.value = hdr
        cell.font = Font(bold=True, color="FFFFFF", size=9)
        cell.fill = DARK_FILL
        cell.alignment = CENTER
        cell.border = _thin_border()
    ws.row_dimensions[TABLE_ROW].height = 18

    data_row = TABLE_ROW + 1
    for idx, trip in enumerate(trips):
        row_fill = STRIPE_FILL if idx % 2 == 1 else None
        write_data_cell(data_row, 1, trip.date.strftime("%d/%m/%Y"), None, row_fill)
        write_data_cell(
            data_row,
            2,
            "Outstation Trip" if trip.trip_type == "outstation" else "Regular Trip",
            None,
            row_fill,
        )
        write_data_cell(data_row, 3, trip.party_name, None, row_fill)
        write_data_cell(data_row, 4, trip.company.name, None, row_fill)
        write_data_cell(data_row, 5, trip.car.name, None, row_fill)
        write_data_cell(data_row, 6, float(trip.total_kms), NUM_FMT, row_fill)
        write_data_cell(data_row, 7, float(trip.extra_hrs), NUM_FMT, row_fill)
        write_data_cell(data_row, 8, float(trip.driver_bhatta), CURRENCY_FMT, row_fill)
        write_data_cell(data_row, 9, float(trip.parking), CURRENCY_FMT, row_fill)
        write_data_cell(
            data_row,
            10,
            f"INV-{str(trip.invoice_id).zfill(3)}" if trip.invoice_id else "Unassigned",
            None,
            row_fill,
        )
        write_data_cell(data_row, 11, float(trip.row_total), CURRENCY_FMT, row_fill)
        ws.row_dimensions[data_row].height = 16
        data_row += 1

    last_data_row = data_row - 1
    ws.row_dimensions[last_data_row + 1].height = 6
    total_row = last_data_row + 2

    grand_total = sum((t.row_total for t in trips), Decimal("0"))

    set_merged(
        f"A{total_row}:J{total_row}",
        _amount_to_words(grand_total),
        font=Font(italic=True, size=10),
        align=LEFT_AL,
    )
    ws.row_dimensions[total_row].height = 22

    m_side = Side(style="medium")
    cell = ws.cell(row=total_row, column=11)
    cell.fill = WHITE_FILL
    cell.border = Border(left=m_side, right=m_side, top=m_side, bottom=m_side)
    cell.value = f"Grand Total: {currency}{float(grand_total):,.2f}"
    cell.font = Font(bold=True, size=13)
    cell.alignment = RIGHT_AL

    ws.row_dimensions[total_row + 1].height = 8
    ws.row_dimensions[total_row + 2].height = 8
    sig_row = total_row + 3

    set_merged(
        f"H{sig_row}:K{sig_row}",
        f"For {biz.name if biz else ''}",
        font=Font(bold=True, size=10),
        align=RIGHT_AL,
    )

    for gap in range(1, 4):
        ws.row_dimensions[sig_row + gap].height = 18

    prop_row = sig_row + 4
    set_merged(
        f"H{prop_row}:K{prop_row}", "(Proprietor)", font=Font(size=10), align=RIGHT_AL
    )

    last_row = prop_row

    col_widths = [12, 18, 18, 18, 16, 11, 11, 13, 13, 13, 14]
    for i, w in enumerate(col_widths, start=1):
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w

    ws.sheet_view.showGridLines = False
    for i in range(N_COLS + 1, N_COLS + 20):
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].hidden = True
    for r in range(last_row + 1, last_row + 30):
        ws.row_dimensions[r].hidden = True

    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = 9
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.print_area = f"A1:{LAST_COL}{last_row}"
    ws.page_margins = PageMargins(left=0.5, right=0.5, top=0.75, bottom=0.75)


@api_view(["GET"])
@admin_or_client_readonly
def download_invoice_excel(request, pk):
    invoice = get_object_or_404(Invoice.objects.select_related("company"), pk=pk)
    company_ids = get_scoped_company_ids(request)
    if company_ids is not None and invoice.company_id not in company_ids:
        return Response({"error": "Not found."}, status=404)
    trips = list(
        DutySlip.objects.filter(invoice=invoice).select_related("car").order_by("date")
    )
    biz = BusinessSettings.objects.first()
    currency = "₹" if biz and biz.currency == "INR" else "$"
    year = datetime.date.today().year
    invoice_ref = f"786/110/{year}{str(invoice.id).zfill(3)}"
    company_rates = {
        cr.car_id: cr for cr in CompanyCarRate.objects.filter(company=invoice.company)
    }

    wb = Workbook()
    ws = wb.active
    ws.title = "Invoice"
    _build_invoice_sheet(ws, invoice, trips, biz, currency, invoice_ref, company_rates)

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    response = HttpResponse(
        buf.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="invoice-{invoice_ref}.xlsx"'
    )
    return response


@api_view(["POST"])
@admin_or_client_readonly
def bulk_download_invoice_pdf(request):
    ids = request.data.get("ids", [])
    if not ids:
        return Response({"error": "No invoice IDs provided."}, status=400)

    company_ids = get_scoped_company_ids(request)
    invoices = (
        Invoice.objects.filter(id__in=ids).select_related("company").order_by("id")
    )
    if company_ids is not None:
        invoices = invoices.filter(company_id__in=company_ids)
    biz = BusinessSettings.objects.first()
    currency = "₹" if biz and biz.currency == "INR" else "$"
    year = datetime.date.today().year
    today = datetime.date.today().strftime("%d %B %Y")
    request_base_url = request.build_absolute_uri()

    documents = []
    valid_refs = []
    for invoice in invoices:
        trips = (
            DutySlip.objects.filter(invoice=invoice)
            .select_related("car")
            .order_by("date")
        )
        trips_with_totals = []
        for trip in trips:
            trip.total_hrs = _calc_total_hrs(trip)
            trips_with_totals.append(trip)

        invoice_ref = f"786/110/{year}{str(invoice.id).zfill(3)}"
        logo_url = biz.logo if biz and biz.logo else ""

        documents.append(
            _build_invoice_html(
                invoice,
                trips_with_totals,
                biz,
                currency,
                invoice_ref,
                logo_url,
                today,
                request_base_url,
            )
        )
        valid_refs.append(invoice_ref)

    if not documents:
        return Response({"error": "No valid invoices found."}, status=404)

    pages = []
    for document in documents:
        pages.extend(document.pages)

    combined_pdf = documents[0].copy(pages=pages).write_pdf()
    response = HttpResponse(combined_pdf, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="invoices-export-{datetime.date.today().strftime("%Y%m%d")}.pdf"'
    )
    return response


@api_view(["GET"])
@admin_or_client_readonly
def download_trips_excel(request):
    company_ids = get_scoped_company_ids(request)
    qs = DutySlip.objects.select_related("car", "company", "invoice")
    if company_ids is not None:
        qs = qs.filter(company_id__in=company_ids)
    ids = request.query_params.get("ids", "")
    if ids:
        id_list = [int(value) for value in ids.split(",") if value.strip().isdigit()]
        qs = qs.filter(id__in=id_list)
    else:
        party_name = request.query_params.get("party_name", "").strip()
        company = request.query_params.get("company", "").strip()
        car = request.query_params.get("car", "").strip()
        date_from = request.query_params.get("date_from", "").strip()
        date_to = request.query_params.get("date_to", "").strip()

        if party_name:
            qs = qs.filter(party_name__icontains=party_name)
        if company:
            qs = qs.filter(company_id=company)
        if car:
            qs = qs.filter(car_id=car)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)

    trips = list(qs.order_by("-date", "-id"))
    biz = BusinessSettings.objects.first()
    currency = "₹" if biz and biz.currency == "INR" else "$"
    report_date = datetime.date.today().strftime("%d/%m/%Y")

    wb = Workbook()
    ws = wb.active
    ws.title = "Trips"
    _build_trips_sheet(ws, trips, biz, currency, "Trips Report", report_date)

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    today = datetime.date.today().strftime("%Y%m%d")
    response = HttpResponse(
        buf.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="trips-export-{today}.xlsx"'
    )
    return response


@api_view(["POST"])
@admin_or_client_readonly
def bulk_export_excel(request):
    ids = request.data.get("ids", [])
    if not ids:
        return Response({"error": "No invoice IDs provided."}, status=400)

    company_ids = get_scoped_company_ids(request)
    invoices = (
        Invoice.objects.filter(id__in=ids).select_related("company").order_by("id")
    )
    if company_ids is not None:
        invoices = invoices.filter(company_id__in=company_ids)
    biz = BusinessSettings.objects.first()
    currency = "₹" if biz and biz.currency == "INR" else "$"
    year = datetime.date.today().year

    wb = Workbook()
    wb.remove(wb.active)  # remove default blank sheet

    for invoice in invoices:
        trips = list(
            DutySlip.objects.filter(invoice=invoice)
            .select_related("car")
            .order_by("date")
        )
        invoice_ref = f"786/110/{year}{str(invoice.id).zfill(3)}"
        company_rates = {
            cr.car_id: cr
            for cr in CompanyCarRate.objects.filter(company=invoice.company)
        }
        ws = wb.create_sheet(title=f"INV-{str(invoice.id).zfill(3)}")
        _build_invoice_sheet(
            ws, invoice, trips, biz, currency, invoice_ref, company_rates
        )

    if not wb.sheetnames:
        return Response({"error": "No valid invoices found."}, status=404)

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    today = datetime.date.today().strftime("%Y%m%d")
    response = HttpResponse(
        buf.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="invoices-export-{today}.xlsx"'
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
        "invoices": list(Invoice.objects.values()),
        "trips": list(DutySlip.objects.values()),
        "business_settings": list(BusinessSettings.objects.values()),
    }
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
@admin_only
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
@admin_only
def restore_database(request):
    try:
        backup = json.loads(request.body)
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON file."}, status=400)

    if backup.get("version") != "1.0":
        return Response({"error": "Incompatible backup version."}, status=400)

    try:
        DutySlip.objects.all().delete()
        Invoice.objects.all().delete()
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
        for row in backup.get("invoices", []):
            Invoice.objects.create(**row)
        for row in backup.get("trips", []):
            DutySlip.objects.create(**row)
        for row in backup.get("business_settings", []):
            row.pop("logo", None)
            BusinessSettings.objects.create(**row)

        return Response(
            {
                "message": "Restore successful.",
                "summary": {
                    "companies": len(backup.get("companies", [])),
                    "cars": len(backup.get("cars", [])),
                    "invoices": len(backup.get("invoices", [])),
                    "trips": len(backup.get("trips", [])),
                },
            }
        )
    except Exception as e:
        return Response({"error": f"Restore failed: {str(e)}"}, status=500)


@api_view(["POST"])
@admin_only
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
@admin_only
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
@admin_only
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

    return _do_restore(backup)


def _do_restore(backup):
    """Core restore logic — accepts a backup dict directly."""
    if backup.get("version") != "1.0":
        return Response({"error": "Incompatible backup version."}, status=400)

    try:
        DutySlip.objects.all().delete()
        Invoice.objects.all().delete()
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
        for row in backup.get("invoices", []):
            Invoice.objects.create(**row)
        for row in backup.get("trips", []):
            DutySlip.objects.create(**row)

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
                "api_invoice",
                "api_dutyslip",
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
                    "invoices": len(backup.get("invoices", [])),
                    "trips": len(backup.get("trips", [])),
                },
            }
        )
    except Exception as e:
        return Response({"error": f"Restore failed: {str(e)}"}, status=500)
