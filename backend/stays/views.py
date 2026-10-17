from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import IsParticipant

from .models import StayRequest
from .serializers import StayRequestSerializer
from .services import (
    accept_stay_request,
    cancel_stay_request,
    complete_stay_request,
    create_stay_request,
    decline_stay_request,
)


class StayRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = StayRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        role = self.request.query_params.get("role", "guest")
        qs = StayRequest.objects.select_related("listing", "listing__host", "guest", "guest__profile")
        if role == "host":
            return qs.filter(listing__host=self.request.user)
        return qs.filter(guest=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        stay = create_stay_request(
            guest=request.user,
            listing=serializer.validated_data["listing"],
            check_in=serializer.validated_data["check_in"],
            check_out=serializer.validated_data["check_out"],
            guests_count=serializer.validated_data["guests_count"],
            message=serializer.validated_data.get("message", ""),
        )
        return Response(StayRequestSerializer(stay).data, status=status.HTTP_201_CREATED)


class StayRequestDetailView(generics.RetrieveAPIView):
    serializer_class = StayRequestSerializer
    permission_classes = [IsAuthenticated, IsParticipant]
    queryset = StayRequest.objects.select_related("listing", "listing__host", "guest")


class StayActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, action):
        try:
            stay = StayRequest.objects.select_related("listing", "listing__host", "guest").get(pk=pk)
        except StayRequest.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound("Stay request not found")

        actions = {
            "accept": accept_stay_request,
            "decline": decline_stay_request,
            "cancel": cancel_stay_request,
            "complete": complete_stay_request,
        }
        if action not in actions:
            return Response({"error": True, "message": "Unknown action"}, status=400)
        updated = actions[action](stay, request.user)
        return Response(StayRequestSerializer(updated).data)
