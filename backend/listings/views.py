from datetime import datetime

from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import IsOwner
from safety.services import users_are_blocked
from stays.models import StayRequest

from .models import Availability, Listing, ListingPhoto
from .serializers import AvailabilitySerializer, ListingPhotoSerializer, ListingSerializer


def parse_date(value, field_name):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValidationError({field_name: "Use YYYY-MM-DD"}) from exc


def listing_covers_dates(listing, check_in, check_out) -> bool:
    return listing.availabilities.filter(
        start_date__lte=check_in, end_date__gte=check_out
    ).exists()


def listing_has_accepted_overlap(listing, check_in, check_out) -> bool:
    return StayRequest.objects.filter(
        listing=listing,
        status=StayRequest.Status.ACCEPTED,
        check_in__lt=check_out,
        check_out__gt=check_in,
    ).exists()


class ListingListCreateView(generics.ListCreateAPIView):
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Listing.objects.filter(is_active=True).select_related("host", "host__profile").prefetch_related(
            "photos", "availabilities"
        )
        user = self.request.user
        if user.is_authenticated:
            blocked_ids = list(
                user.blocks_made.values_list("blocked_user_id", flat=True)
            ) + list(user.blocks_received.values_list("blocker_id", flat=True))
            if blocked_ids:
                qs = qs.exclude(host_id__in=blocked_ids)

        city = self.request.query_params.get("city")
        if city:
            qs = qs.filter(city__icontains=city.strip())

        guests = self.request.query_params.get("guests")
        if guests:
            try:
                qs = qs.filter(max_guests__gte=int(guests))
            except ValueError as exc:
                raise ValidationError({"guests": "Must be an integer"}) from exc

        check_in = parse_date(self.request.query_params.get("check_in"), "check_in")
        check_out = parse_date(self.request.query_params.get("check_out"), "check_out")
        if check_in and check_out:
            if check_out <= check_in:
                raise ValidationError({"check_out": "Must be after check_in"})
            matching_ids = []
            for listing in qs.prefetch_related("availabilities"):
                if listing_covers_dates(listing, check_in, check_out) and not listing_has_accepted_overlap(
                    listing, check_in, check_out
                ):
                    matching_ids.append(listing.id)
            qs = qs.filter(id__in=matching_ids)
        return qs

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)


class MyListingListView(generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Listing.objects.filter(host=self.request.user)
            .select_related("host", "host__profile")
            .prefetch_related("photos", "availabilities")
        )


class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Listing.objects.select_related("host", "host__profile").prefetch_related(
            "photos", "availabilities"
        )

    def get_object(self):
        obj = super().get_object()
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            if users_are_blocked(self.request.user, obj.host):
                from rest_framework.exceptions import NotFound

                raise NotFound("Listing not found")
            return obj
        if obj.host != self.request.user:
            raise PermissionDenied("You can only edit your own listings")
        return obj


class ListingPhotoCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        listing = Listing.objects.filter(pk=pk, host=request.user).first()
        if listing is None:
            raise PermissionDenied("You can only add photos to your listings")
        serializer = ListingPhotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(listing=listing)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AvailabilityListCreateView(generics.ListCreateAPIView):
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated]

    def get_listing(self):
        listing = Listing.objects.filter(pk=self.kwargs["pk"]).first()
        if listing is None:
            from rest_framework.exceptions import NotFound

            raise NotFound("Listing not found")
        if listing.host != self.request.user:
            raise PermissionDenied("You can only manage availability for your listings")
        return listing

    def get_queryset(self):
        return Availability.objects.filter(listing=self.get_listing())

    def perform_create(self, serializer):
        serializer.save(listing=self.get_listing())


class AvailabilityDeleteView(generics.DestroyAPIView):
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated]
    queryset = Availability.objects.select_related("listing")

    def perform_destroy(self, instance):
        if instance.listing.host != self.request.user:
            raise PermissionDenied("You can only delete your own availability")
        instance.delete()
