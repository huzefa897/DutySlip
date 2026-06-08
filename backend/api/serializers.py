from rest_framework import serializers
from .models import Company, Car, Invoice, DutySlip, BusinessSettings, CompanyCarRate


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = "__all__"


class DutySlipSerializer(serializers.ModelSerializer):
    car_name = serializers.CharField(source="car.name", read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = DutySlip
        fields = "__all__"
        read_only_fields = [
            "total_kms",
            "extra_kms",
            "extra_kms_amount",
            "extra_hrs",
            "extra_hrs_amount",
            "row_total",
        ]

    def validate(self, attrs):
        trip_type = attrs.get("trip_type")
        invoice = attrs.get("invoice")

        if self.instance:
            if trip_type is None:
                trip_type = self.instance.trip_type
            if invoice is None:
                invoice = self.instance.invoice

        if invoice and trip_type and invoice.invoice_type != trip_type:
            raise serializers.ValidationError(
                {"invoice": "Trip type must match the invoice type."}
            )

        return attrs


class InvoiceSerializer(serializers.ModelSerializer):
    trips = DutySlipSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)
    party_name = serializers.CharField(read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "company",
            "company_name",
            "party",
            "party_name",
            "invoice_type",
            "status",
            "payment_status",
            "grand_total",
            "created_at",
            "trips",
        ]
        read_only_fields = ["grand_total", "created_at", "party_name", "company_name"]


class BusinessSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessSettings
        fields = "__all__"


class CompanyCarRateSerializer(serializers.ModelSerializer):
    car_name = serializers.CharField(source="car.name", read_only=True)

    class Meta:
        model = CompanyCarRate
        fields = "__all__"
