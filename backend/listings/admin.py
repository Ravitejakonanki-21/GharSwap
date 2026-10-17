from django.contrib import admin

from .models import Availability, Listing, ListingPhoto


class ListingPhotoInline(admin.TabularInline):
    model = ListingPhoto
    extra = 0


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 0


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "city", "host", "max_guests", "is_active")
    list_filter = ("city", "is_active")
    search_fields = ("title", "city", "address_area", "host__email")
    inlines = [ListingPhotoInline, AvailabilityInline]


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ("listing", "start_date", "end_date")
