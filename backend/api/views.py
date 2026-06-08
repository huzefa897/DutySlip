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

    mismatched = entries.exclude(entry_type=slip.slip_type)
    if mismatched.exists():
        return Response(
            {"error": "Selected entries must match the duty slip type."},
            status=status.HTTP_400_BAD_REQUEST,
        )

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
    if new_status not in ["draft", "finalised"]:
        return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

    slip.status = new_status
    slip.save()
    return Response(DutySlipSerializer(slip).data)


@api_view(["PATCH"])
def update_dutyslip_payment_status(request, pk):
    try:
        slip = DutySlip.objects.get(pk=pk)
    except DutySlip.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get("payment_status")
    if new_status not in ["unpaid", "paid"]:
        return Response(
            {"error": "Invalid payment status"}, status=status.HTTP_400_BAD_REQUEST
        )

    slip.payment_status = new_status
    slip.save()
    return Response(DutySlipSerializer(slip).data)


# ── DutySlip ──────────────────────────────────────────────────────────────────


# ── Excel helpers ─────────────────────────────────────────────


def _calc_total_hrs(entry):
    """Return total trip hours for regular entries; 0 for outstation."""
    if not entry.start_time or not entry.end_time:
        return Decimal("0")
    s = datetime.datetime.combine(entry.date, entry.start_time)
    e = datetime.datetime.combine(entry.date, entry.end_time)
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
    slip, entries, biz, currency, invoice_ref, logo_url, today, request_base_url
):
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
    return HTML(string=html_string, base_url=request_base_url).render()


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
    entries_with_totals = []
    for entry in entries:
        entry.total_hrs = _calc_total_hrs(entry)
        entries_with_totals.append(entry)

    biz = BusinessSettings.objects.first()
    currency = "₹" if biz and biz.currency == "INR" else "$"
    year = datetime.date.today().year
    invoice_ref = f"786/110/{year}{str(slip.id).zfill(3)}"
    logo_url = biz.logo if biz and biz.logo else ""
    today = datetime.date.today().strftime("%d %B %Y")

    pdf = _build_invoice_html(
        slip,
        entries_with_totals,
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


def _build_invoice_sheet(ws, slip, entries, biz, currency, invoice_ref, company_rates):
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
        "A10:F10", slip.company.name, font=Font(bold=True, size=11), align=LEFT_AL
    )
    set_merged(
        "H10:M10",
        f"Date: {slip.created_at.strftime('%d/%m/%Y')}",
        font=Font(size=10),
        align=RIGHT_AL,
    )

    if slip.company.abn:
        set_merged("A11:F11", f"ABN: {slip.company.abn}", font=GRAY_FONT, align=LEFT_AL)
    set_merged(
        "H11:M11",
        f"Payment: {slip.payment_status.capitalize()}",
        font=Font(size=10),
        align=RIGHT_AL,
    )

    ws.row_dimensions[12].height = 8

    # ── Section 3: Guest Name Row (row 13) ───────────────────────
    set_merged(
        "A13:M13",
        f"Guest Name: {slip.party_name}",
        font=Font(bold=True, size=10),
        align=LEFT_AL,
    )

    ws.row_dimensions[14].height = 8

    # ── Section 4: Duty Slip Table ───────────────────────────────
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
    for idx, entry in enumerate(entries):
        cr = company_rates.get(entry.car_id)
        base_rate = (
            cr.base_rate if (cr and cr.base_rate is not None) else entry.car.base_rate
        )
        total_hrs = _calc_total_hrs(entry)
        row_fill = STRIPE_FILL if idx % 2 == 1 else None

        write_data_cell(data_row, 1, entry.date.strftime("%d/%m/%Y"), None, row_fill)
        write_data_cell(data_row, 2, entry.car.name, None, row_fill)
        write_data_cell(data_row, 3, float(entry.start_kms), NUM_FMT, row_fill)
        write_data_cell(data_row, 4, float(entry.end_kms), NUM_FMT, row_fill)
        write_data_cell(data_row, 5, float(entry.total_kms), NUM_FMT, row_fill)
        write_data_cell(data_row, 6, float(entry.extra_kms), NUM_FMT, row_fill)
        write_data_cell(data_row, 7, float(total_hrs), NUM_FMT, row_fill)
        write_data_cell(
            data_row, 8, float(entry.extra_hrs_amount), CURRENCY_FMT, row_fill
        )
        write_data_cell(
            data_row, 9, float(entry.extra_kms_amount), CURRENCY_FMT, row_fill
        )
        write_data_cell(
            data_row, 10, float(entry.driver_bhatta), CURRENCY_FMT, row_fill
        )
        write_data_cell(data_row, 11, float(base_rate), CURRENCY_FMT, row_fill)
        write_data_cell(data_row, 12, float(entry.parking), CURRENCY_FMT, row_fill)
        write_data_cell(data_row, 13, float(entry.row_total), CURRENCY_FMT, row_fill)
        ws.row_dimensions[data_row].height = 16
        data_row += 1

    last_data_row = data_row - 1

    # ── Section 5: Grand Total ────────────────────────────────────
    ws.row_dimensions[last_data_row + 1].height = 6
    total_row = last_data_row + 2

    set_merged(
        f"A{total_row}:F{total_row}",
        _amount_to_words(slip.grand_total),
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
    gt_cell.value = f"Grand Total: {currency}{float(slip.grand_total):,.2f}"
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


def _build_entries_sheet(ws, entries, biz, currency, report_title, report_date):
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
        "Entries exported from the current database state",
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
        "Duty Slip",
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
    for idx, entry in enumerate(entries):
        row_fill = STRIPE_FILL if idx % 2 == 1 else None
        write_data_cell(data_row, 1, entry.date.strftime("%d/%m/%Y"), None, row_fill)
        write_data_cell(
            data_row,
            2,
            "Outstation Trip" if entry.entry_type == "outstation" else "Regular Trip",
            None,
            row_fill,
        )
        write_data_cell(data_row, 3, entry.party_name, None, row_fill)
        write_data_cell(data_row, 4, entry.company.name, None, row_fill)
        write_data_cell(data_row, 5, entry.car.name, None, row_fill)
        write_data_cell(data_row, 6, float(entry.total_kms), NUM_FMT, row_fill)
        write_data_cell(data_row, 7, float(entry.extra_hrs), NUM_FMT, row_fill)
        write_data_cell(data_row, 8, float(entry.driver_bhatta), CURRENCY_FMT, row_fill)
        write_data_cell(data_row, 9, float(entry.parking), CURRENCY_FMT, row_fill)
        write_data_cell(
            data_row,
            10,
            f"INV-{str(entry.duty_slip_id).zfill(3)}"
            if entry.duty_slip_id
            else "Unassigned",
            None,
            row_fill,
        )
        write_data_cell(data_row, 11, float(entry.row_total), CURRENCY_FMT, row_fill)
        ws.row_dimensions[data_row].height = 16
        data_row += 1

    last_data_row = data_row - 1
    ws.row_dimensions[last_data_row + 1].height = 6
    total_row = last_data_row + 2

    grand_total = sum((e.row_total for e in entries), Decimal("0"))

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
def download_invoice_excel(request, pk):
    slip = get_object_or_404(DutySlip.objects.select_related("company"), pk=pk)
    entries = list(
        DutySlipEntry.objects.filter(duty_slip=slip)
        .select_related("car")
        .order_by("date")
    )
    biz = BusinessSettings.objects.first()
    currency = "₹" if biz and biz.currency == "INR" else "$"
    year = datetime.date.today().year
    invoice_ref = f"786/110/{year}{str(slip.id).zfill(3)}"
    company_rates = {
        cr.car_id: cr for cr in CompanyCarRate.objects.filter(company=slip.company)
    }

    wb = Workbook()
    ws = wb.active
    ws.title = "Invoice"
    _build_invoice_sheet(ws, slip, entries, biz, currency, invoice_ref, company_rates)

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
def bulk_download_invoice_pdf(request):
    ids = request.data.get("ids", [])
    if not ids:
        return Response({"error": "No invoice IDs provided."}, status=400)

    slips = DutySlip.objects.filter(id__in=ids).select_related("company").order_by("id")
    biz = BusinessSettings.objects.first()
    currency = "₹" if biz and biz.currency == "INR" else "$"
    year = datetime.date.today().year
    today = datetime.date.today().strftime("%d %B %Y")
    request_base_url = request.build_absolute_uri()

    documents = []
    valid_refs = []
    for slip in slips:
        entries = (
            DutySlipEntry.objects.filter(duty_slip=slip)
            .select_related("car")
            .order_by("date")
        )
        entries_with_totals = []
        for entry in entries:
            entry.total_hrs = _calc_total_hrs(entry)
            entries_with_totals.append(entry)

        invoice_ref = f"786/110/{year}{str(slip.id).zfill(3)}"
        logo_url = biz.logo if biz and biz.logo else ""

        documents.append(
            _build_invoice_html(
                slip,
                entries_with_totals,
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
def download_entries_excel(request):
    qs = DutySlipEntry.objects.select_related("car", "company", "duty_slip")
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

    entries = list(qs.order_by("-date", "-id"))
    biz = BusinessSettings.objects.first()
    currency = "₹" if biz and biz.currency == "INR" else "$"
    report_date = datetime.date.today().strftime("%d/%m/%Y")

    wb = Workbook()
    ws = wb.active
    ws.title = "Entries"
    _build_entries_sheet(ws, entries, biz, currency, "Entries Report", report_date)

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    today = datetime.date.today().strftime("%Y%m%d")
    response = HttpResponse(
        buf.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="entries-export-{today}.xlsx"'
    )
    return response


@api_view(["POST"])
def bulk_export_excel(request):
    ids = request.data.get("ids", [])
    if not ids:
        return Response({"error": "No invoice IDs provided."}, status=400)

    slips = DutySlip.objects.filter(id__in=ids).select_related("company").order_by("id")
    biz = BusinessSettings.objects.first()
    currency = "₹" if biz and biz.currency == "INR" else "$"
    year = datetime.date.today().year

    wb = Workbook()
    wb.remove(wb.active)  # remove default blank sheet

    for slip in slips:
        entries = list(
            DutySlipEntry.objects.filter(duty_slip=slip)
            .select_related("car")
            .order_by("date")
        )
        invoice_ref = f"786/110/{year}{str(slip.id).zfill(3)}"
        company_rates = {
            cr.car_id: cr for cr in CompanyCarRate.objects.filter(company=slip.company)
        }
        ws = wb.create_sheet(title=f"INV-{str(slip.id).zfill(3)}")
        _build_invoice_sheet(
            ws, slip, entries, biz, currency, invoice_ref, company_rates
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
