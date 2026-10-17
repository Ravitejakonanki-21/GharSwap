from django.conf import settings
from django.db import models


class Listing(models.Model):
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listings"
    )
    title = models.CharField(max_length=140)
    description = models.TextField()
    city = models.CharField(max_length=80, db_index=True)
    address_area = models.CharField(
        max_length=160, help_text="Neighborhood or area, never a full street address"
    )
    max_guests = models.PositiveIntegerField()
    house_rules = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.city})"


class ListingPhoto(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="listings/")
    caption = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]


class Availability(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="availabilities"
    )
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ["start_date"]
        verbose_name_plural = "availabilities"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.end_date <= self.start_date:
            raise ValidationError("end_date must be after start_date")
