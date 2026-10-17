from django.contrib import admin

from .models import Review, StayRequest


@admin.register(StayRequest)
class StayRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "guest", "listing", "status", "check_in", "check_out")
    list_filter = ("status",)
    search_fields = ("guest__email", "listing__title")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("stay_request", "reviewer", "reviewee", "rating")
