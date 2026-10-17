from rest_framework import serializers

from .models import Availability, Listing, ListingPhoto


class ListingPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingPhoto
        fields = ("id", "image", "caption")
        read_only_fields = ("id",)


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ("id", "listing", "start_date", "end_date")
        read_only_fields = ("id", "listing")

    def validate(self, attrs):
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if start and end and end <= start:
            raise serializers.ValidationError("end_date must be after start_date")
        return attrs


class ListingSerializer(serializers.ModelSerializer):
    host_id = serializers.IntegerField(source="host.id", read_only=True)
    host_name = serializers.SerializerMethodField()
    photos = ListingPhotoSerializer(many=True, read_only=True)
    availabilities = AvailabilitySerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = (
            "id",
            "host_id",
            "host_name",
            "title",
            "description",
            "city",
            "address_area",
            "max_guests",
            "house_rules",
            "is_active",
            "photos",
            "availabilities",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_host_name(self, obj):
        profile = getattr(obj.host, "profile", None)
        return profile.display_name if profile else obj.host.email.split("@")[0]

    def validate_max_guests(self, value):
        if value < 1:
            raise serializers.ValidationError("max_guests must be at least 1")
        return value
