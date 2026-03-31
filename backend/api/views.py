from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Company, Car, DutySlip, DutySlipEntry, BusinessSettings
from .serializers import (
    CompanySerializer, CarSerializer,
    DutySlipSerializer, DutySlipEntrySerializer,
    BusinessSettingsSerializer
)
from .services import compute_entry, compute_duty_slip_total

# ── Business Settings ─────────────────────────────────────────────────────────
@api_view(['GET'])
def business_settings(request):
    settings = BusinessSettings.objects.first()
    if not settings:
        return Response({'error': 'Business settings not configured'}, status=404)
    return Response(BusinessSettingsSerializer(settings).data)

@api_view(['GET', 'PATCH'])
def business_settings(request):
    settings_obj = BusinessSettings.objects.first()
    if not settings_obj:
        return Response({'error': 'Business settings not configured'}, status=404)

    if request.method == 'GET':
        return Response(BusinessSettingsSerializer(settings_obj).data)

    # PATCH — partial update
    serializer = BusinessSettingsSerializer(
        settings_obj, data=request.data, partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# ── Companies ────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def company_list(request):
    if request.method == 'GET':
        companies = Company.objects.all()
        return Response(CompanySerializer(companies, many=True).data)

    serializer = CompanySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET', 'PUT', 'DELETE'])
def company_detail(request, pk):
    try:
        company = Company.objects.get(pk=pk)
    except Company.DoesNotExist:
        return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(CompanySerializer(company).data)

    if request.method == 'PUT':
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        try:
            company.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {'error': 'Cannot delete — company is used in existing records.'},
                status=status.HTTP_400_BAD_REQUEST
            )

# ── Cars ─────────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def car_list(request):
    if request.method == 'GET':
        cars = Car.objects.all()
        return Response(CarSerializer(cars, many=True).data)

    serializer = CarSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def car_detail(request, pk):
    try:
        car = Car.objects.get(pk=pk)
    except Car.DoesNotExist:
        return Response({'error': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(CarSerializer(car).data)

    if request.method == 'PUT':
        serializer = CarSerializer(car, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        try:
            car.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {'error': 'Cannot delete — car is used in existing entries.'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ── DutySlipEntry ─────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def entry_list(request):
    if request.method == 'GET':
        entries = DutySlipEntry.objects.all().order_by('-date')
        return Response(DutySlipEntrySerializer(entries, many=True).data)

    serializer = DutySlipEntrySerializer(data=request.data)
    if serializer.is_valid():
        entry = serializer.save()
        entry = compute_entry(entry)
        entry.save()
        return Response(DutySlipEntrySerializer(entry).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def entry_detail(request, pk):
    try:
        entry = DutySlipEntry.objects.get(pk=pk)
    except DutySlipEntry.DoesNotExist:
        return Response({'error': 'Entry not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(DutySlipEntrySerializer(entry).data)

    if request.method == 'PUT':
        serializer = DutySlipEntrySerializer(entry, data=request.data)
        if serializer.is_valid():
            entry = serializer.save()
            entry = compute_entry(entry)
            entry.save()
            # recompute duty slip total if entry is assigned
            if entry.duty_slip:
                compute_duty_slip_total(entry.duty_slip)
            return Response(DutySlipEntrySerializer(entry).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        duty_slip = entry.duty_slip
        entry.delete()
        if duty_slip:
            compute_duty_slip_total(duty_slip)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── DutySlip ──────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def dutyslip_list(request):
    if request.method == 'GET':
        slips = DutySlip.objects.all().order_by('-created_at')
        return Response(DutySlipSerializer(slips, many=True).data)

    serializer = DutySlipSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
def dutyslip_detail(request, pk):
    try:
        slip = DutySlip.objects.get(pk=pk)
    except DutySlip.DoesNotExist:
        return Response({'error': 'DutySlip not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(DutySlipSerializer(slip).data)

    if request.method == 'DELETE':
        slip.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def assign_entries_to_dutyslip(request, pk):
    """
    Assign a list of entry IDs to a DutySlip.
    Body: { "entry_ids": [1, 2, 3] }
    """
    try:
        slip = DutySlip.objects.get(pk=pk)
    except DutySlip.DoesNotExist:
        return Response({'error': 'DutySlip not found'}, status=status.HTTP_404_NOT_FOUND)

    entry_ids = request.data.get('entry_ids', [])
    entries = DutySlipEntry.objects.filter(id__in=entry_ids)
    entries.update(duty_slip=slip)
    compute_duty_slip_total(slip)

    return Response(DutySlipSerializer(slip).data)


@api_view(['POST'])
def remove_entry_from_dutyslip(request, pk, entry_id):
    """
    Remove a single entry from a DutySlip (sets duty_slip to NULL).
    """
    try:
        slip = DutySlip.objects.get(pk=pk)
        entry = DutySlipEntry.objects.get(pk=entry_id, duty_slip=slip)
    except (DutySlip.DoesNotExist, DutySlipEntry.DoesNotExist):
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    entry.duty_slip = None
    entry.save()
    compute_duty_slip_total(slip)

    return Response(DutySlipSerializer(slip).data)