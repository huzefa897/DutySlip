from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        profile = getattr(user, "profile", None)
        token["role"] = profile.role if profile else "client"
        token["company_ids"] = (
            list(profile.companies.values_list("id", flat=True)) if profile else []
        )
        token["email"] = user.email
        token["name"] = user.get_full_name() or user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        profile = getattr(self.user, "profile", None)
        if profile and not profile.is_active:
            raise serializers.ValidationError("Account is deactivated.")
        return data
