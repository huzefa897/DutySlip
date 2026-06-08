from rest_framework import serializers
from .models import Company, Car, DutySlip, DutySlipEntry, BusinessSettings
from .models import (
    CompanyCarRate,
)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = "__all__"


class DutySlipEntrySerializer(serializers.ModelSerializer):
    car_name = serializers.CharField(source="car.name", read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = DutySlipEntry
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
        entry_type = attrs.get("entry_type")
        duty_slip = attrs.get("duty_slip")

        if self.instance:
            if entry_type is None:
                entry_type = self.instance.entry_type
            if duty_slip is None:
                duty_slip = self.instance.duty_slip

        if duty_slip and entry_type and duty_slip.slip_type != entry_type:
            raise serializers.ValidationError(
                {"duty_slip": "Entry type must match the duty slip type."}
            )

        return attrs


class DutySlipSerializer(serializers.ModelSerializer):
    entries = DutySlipEntrySerializer(many=True, read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = DutySlip
        fields = "__all__"
        read_only_fields = ["grand_total"]


class BusinessSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessSettings
        fields = "__all__"


class CompanyCarRateSerializer(serializers.ModelSerializer):
    car_name = serializers.CharField(source="car.name", read_only=True)

    class Meta:
        model = CompanyCarRate
        fields = "__all__"
