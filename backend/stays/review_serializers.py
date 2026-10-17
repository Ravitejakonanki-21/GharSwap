from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Review, StayRequest


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_id = serializers.IntegerField(source="reviewer.id", read_only=True)
    reviewee_id = serializers.IntegerField(source="reviewee.id", read_only=True)

    class Meta:
        model = Review
        fields = (
            "id",
            "stay_request",
            "reviewer_id",
            "reviewee_id",
            "rating",
            "comment",
            "created_at",
        )
        read_only_fields = ("id", "reviewer_id", "reviewee_id", "created_at")

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def create(self, validated_data):
        reviewer = self.context["request"].user
        stay = validated_data["stay_request"]
        if stay.status != StayRequest.Status.COMPLETED:
            raise ValidationError("Reviews are allowed only after a completed stay")
        if reviewer.id not in {stay.guest_id, stay.listing.host_id}:
            raise ValidationError("Only stay participants can leave a review")
        if Review.objects.filter(stay_request=stay, reviewer=reviewer).exists():
            raise ValidationError("You have already reviewed this stay")
        reviewee_id = stay.listing.host_id if reviewer.id == stay.guest_id else stay.guest_id
        validated_data["reviewer"] = reviewer
        validated_data["reviewee_id"] = reviewee_id
        return super().create(validated_data)
