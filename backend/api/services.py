from decimal import Decimal
from datetime import datetime
from .models import DutySlipEntry, DutySlip

KM_THRESHOLD = Decimal('80')
HR_THRESHOLD = Decimal('8')


def compute_entry(entry: DutySlipEntry) -> DutySlipEntry:
    """
    Computes all derived fields for a DutySlipEntry.
    Does NOT save — caller is responsible for saving.
    """
    car = entry.car

    # --- KMs ---
    total_kms = entry.end_kms - entry.start_kms
    extra_kms = max(Decimal('0'), total_kms - KM_THRESHOLD)
    extra_kms_amount = extra_kms * car.extra_km_rate

    # --- Hours ---
    start_dt = datetime.combine(entry.date, entry.start_time)
    end_dt = datetime.combine(entry.date, entry.end_time)

    # handle overnight (end time past midnight)
    if end_dt < start_dt:
        from datetime import timedelta
        end_dt += timedelta(days=1)

    total_hrs = Decimal(str((end_dt - start_dt).total_seconds() / 3600))
    extra_hrs = max(Decimal('0'), total_hrs - HR_THRESHOLD)
    extra_hrs_amount = extra_hrs * car.extra_hr_rate

    # --- Row Total ---
    row_total = (
        car.base_rate
        + extra_kms_amount
        + extra_hrs_amount
        + entry.driver_bhatta
        + entry.parking
    )

    # --- Assign back ---
    entry.total_kms = total_kms
    entry.extra_kms = extra_kms
    entry.extra_kms_amount = extra_kms_amount
    entry.extra_hrs = extra_hrs
    entry.extra_hrs_amount = extra_hrs_amount
    entry.row_total = row_total

    return entry


def compute_duty_slip_total(duty_slip: DutySlip) -> DutySlip:
    """
    Sums all entry row_totals and saves grand_total to DutySlip.
    """
    entries = DutySlipEntry.objects.filter(duty_slip=duty_slip)
    grand_total = sum((e.row_total for e in entries), Decimal('0'))
    duty_slip.grand_total = grand_total
    duty_slip.save()
    return duty_slip