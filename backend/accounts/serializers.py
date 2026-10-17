from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Profile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    display_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("email", "password", "phone", "display_name")

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        display_name = validated_data.pop("display_name", "") or ""
        user = User.objects.create_user(**validated_data)
        if display_name:
            profile = user.profile
            profile.display_name = display_name
            profile.save(update_fields=["display_name"])
        return user


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "phone", "is_verified")
        read_only_fields = ("id", "email", "is_verified")


class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    is_verified = serializers.BooleanField(source="user.is_verified", read_only=True)

    class Meta:
        model = Profile
        fields = (
            "user_id",
            "email",
            "display_name",
            "bio",
            "city",
            "languages",
            "photo",
            "id_verified",
            "is_verified",
        )
        read_only_fields = ("id_verified",)

    def validate_languages(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("languages must be a list of strings")
        return [str(item).strip() for item in value if str(item).strip()]


class PublicProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = Profile
        fields = (
            "user_id",
            "display_name",
            "bio",
            "city",
            "languages",
            "photo",
            "id_verified",
        )
