from rest_framework import serializers

from listings.serializers import ListingSerializer

from .models import StayRequest


class StayRequestSerializer(serializers.ModelSerializer):
    guest_id = serializers.IntegerField(source="guest.id", read_only=True)
    listing_detail = ListingSerializer(source="listing", read_only=True)
    guest_nights = serializers.IntegerField(read_only=True)

    class Meta:
        model = StayRequest
        fields = (
            "id",
            "guest_id",
            "listing",
            "listing_detail",
            "check_in",
            "check_out",
            "guests_count",
            "message",
            "status",
            "guest_nights",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "created_at", "updated_at")

    def validate(self, attrs):
        check_in = attrs.get("check_in")
        check_out = attrs.get("check_out")
        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError({"check_out": "Must be after check_in"})
        return attrs


class StayRequestCreateSerializer(StayRequestSerializer):
    class Meta(StayRequestSerializer.Meta):
        extra_kwargs = {"listing": {"write_only": False}}
