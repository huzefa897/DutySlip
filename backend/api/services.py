from decimal import Decimal
from datetime import datetime
from .models import DutySlipEntry, DutySlip, CompanyCarRate

KM_THRESHOLD = Decimal('80')
HR_THRESHOLD = Decimal('8')


def get_car_rates(entry):
    """
    Returns effective rates for a car — company override if exists,
    otherwise falls back to global car rates.
    """
    try:
        override = CompanyCarRate.objects.get(
            company=entry.company,
            car=entry.car
        )
        base_rate     = override.base_rate     if override.base_rate     is not None else entry.car.base_rate
        extra_km_rate = override.extra_km_rate if override.extra_km_rate is not None else entry.car.extra_km_rate
        extra_hr_rate = override.extra_hr_rate if override.extra_hr_rate is not None else entry.car.extra_hr_rate
    except CompanyCarRate.DoesNotExist:
        base_rate     = entry.car.base_rate
        extra_km_rate = entry.car.extra_km_rate
        extra_hr_rate = entry.car.extra_hr_rate

    return base_rate, extra_km_rate, extra_hr_rate


def compute_entry(entry: DutySlipEntry) -> DutySlipEntry:
    base_rate, extra_km_rate, extra_hr_rate = get_car_rates(entry)

    # --- KMs ---
    total_kms = entry.end_kms - entry.start_kms
    extra_kms = max(Decimal('0'), total_kms - KM_THRESHOLD)
    extra_kms_amount = extra_kms * extra_km_rate

    # --- Hours ---
    start_dt = datetime.combine(entry.date, entry.start_time)
    end_dt = datetime.combine(entry.date, entry.end_time)

    if end_dt < start_dt:
        from datetime import timedelta
        end_dt += timedelta(days=1)

    total_hrs = Decimal(str((end_dt - start_dt).total_seconds() / 3600))
    extra_hrs = max(Decimal('0'), total_hrs - HR_THRESHOLD)
    extra_hrs_amount = extra_hrs * extra_hr_rate

    # --- Row Total ---
    row_total = (
        base_rate
        + extra_kms_amount
        + extra_hrs_amount
        + entry.driver_bhatta
        + entry.parking
    )

    # --- Assign back ---
    entry.total_kms       = total_kms
    entry.extra_kms       = extra_kms
    entry.extra_kms_amount = extra_kms_amount
    entry.extra_hrs       = extra_hrs
    entry.extra_hrs_amount = extra_hrs_amount
    entry.row_total       = row_total

    return entry


def compute_duty_slip_total(duty_slip: DutySlip) -> DutySlip:
    entries = DutySlipEntry.objects.filter(duty_slip=duty_slip)
    grand_total = sum((e.row_total for e in entries), Decimal('0'))
    duty_slip.grand_total = grand_total
    duty_slip.save()
    return duty_slip