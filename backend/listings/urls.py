from django.urls import path

from .views import (
    AvailabilityDeleteView,
    AvailabilityListCreateView,
    ListingDetailView,
    ListingListCreateView,
    ListingPhotoCreateView,
    MyListingListView,
)

urlpatterns = [
    path("listings/", ListingListCreateView.as_view(), name="listing-list"),
    path("listings/mine/", MyListingListView.as_view(), name="listing-mine"),
    path("listings/<int:pk>/", ListingDetailView.as_view(), name="listing-detail"),
    path("listings/<int:pk>/photos/", ListingPhotoCreateView.as_view(), name="listing-photos"),
    path(
        "listings/<int:pk>/availability/",
        AvailabilityListCreateView.as_view(),
        name="listing-availability",
    ),
    path("availability/<int:pk>/", AvailabilityDeleteView.as_view(), name="availability-delete"),
]
