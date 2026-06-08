from decimal import Decimal
from datetime import datetime
from .models import DutySlip, Invoice, CompanyCarRate

KM_THRESHOLD = Decimal("80")
HR_THRESHOLD = Decimal("8")


def get_car_rates(trip):
    try:
        override = CompanyCarRate.objects.get(company=trip.company, car=trip.car)
        base_rate = (
            override.base_rate if override.base_rate is not None else trip.car.base_rate
        )
        extra_km_rate = (
            override.extra_km_rate
            if override.extra_km_rate is not None
            else trip.car.extra_km_rate
        )
        extra_hr_rate = (
            override.extra_hr_rate
            if override.extra_hr_rate is not None
            else trip.car.extra_hr_rate
        )
        outstation_rate = (
            override.outstation_rate
            if override.outstation_rate is not None
            else trip.car.outstation_rate
        )
    except CompanyCarRate.DoesNotExist:
        base_rate = trip.car.base_rate
        extra_km_rate = trip.car.extra_km_rate
        extra_hr_rate = trip.car.extra_hr_rate
        outstation_rate = trip.car.outstation_rate

    return base_rate, extra_km_rate, extra_hr_rate, outstation_rate


def compute_trip(trip: DutySlip) -> DutySlip:
    if trip.trip_type == "outstation":
        return compute_outstation_trip(trip)
    return compute_regular_trip(trip)


def compute_regular_trip(trip: DutySlip) -> DutySlip:
    base_rate, extra_km_rate, extra_hr_rate, _ = get_car_rates(trip)

    # KMs
    total_kms = trip.end_kms - trip.start_kms
    extra_kms = max(Decimal("0"), total_kms - KM_THRESHOLD)
    extra_kms_amount = extra_kms * extra_km_rate

    # Hours
    start_dt = datetime.combine(trip.date, trip.start_time)
    end_dt = datetime.combine(trip.date, trip.end_time)
    if end_dt < start_dt:
        from datetime import timedelta

        end_dt += timedelta(days=1)

    total_hrs = Decimal(str((end_dt - start_dt).total_seconds() / 3600))
    extra_hrs = max(Decimal("0"), total_hrs - HR_THRESHOLD)
    extra_hrs_amount = extra_hrs * extra_hr_rate

    row_total = (
        base_rate
        + extra_kms_amount
        + extra_hrs_amount
        + trip.driver_bhatta
        + trip.parking
    )

    trip.total_kms = total_kms
    trip.extra_kms = extra_kms
    trip.extra_kms_amount = extra_kms_amount
    trip.extra_hrs = extra_hrs
    trip.extra_hrs_amount = extra_hrs_amount
    trip.row_total = row_total

    return trip


def compute_outstation_trip(trip: DutySlip) -> DutySlip:
    _, _, _, outstation_rate = get_car_rates(trip)

    total_kms = trip.end_kms - trip.start_kms
    km_cost = total_kms * outstation_rate

    row_total = km_cost + trip.driver_bhatta + trip.parking

    trip.total_kms = total_kms
    trip.outstation_rate = outstation_rate
    trip.extra_kms = Decimal("0")
    trip.extra_kms_amount = Decimal("0")
    trip.extra_hrs = Decimal("0")
    trip.extra_hrs_amount = Decimal("0")
    trip.row_total = row_total

    return trip


def compute_invoice_total(invoice: Invoice) -> Invoice:
    trips = DutySlip.objects.filter(invoice=invoice)
    grand_total = sum((t.row_total for t in trips), Decimal("0"))
    invoice.grand_total = grand_total
    invoice.save()
    return invoice
