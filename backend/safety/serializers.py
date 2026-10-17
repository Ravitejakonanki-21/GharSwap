from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Block, Report


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ("id", "reported_user", "reason", "details", "status", "created_at")
        read_only_fields = ("id", "status", "created_at")

    def validate_reported_user(self, value):
        if value == self.context["request"].user:
            raise ValidationError("You cannot report yourself")
        return value

    def create(self, validated_data):
        validated_data["reporter"] = self.context["request"].user
        return super().create(validated_data)


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ("id", "blocked_user", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_blocked_user(self, value):
        if value == self.context["request"].user:
            raise ValidationError("You cannot block yourself")
        return value

    def create(self, validated_data):
        validated_data["blocker"] = self.context["request"].user
        block, _ = Block.objects.get_or_create(
            blocker=validated_data["blocker"],
            blocked_user=validated_data["blocked_user"],
        )
        return block
