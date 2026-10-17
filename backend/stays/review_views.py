from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Review
from .review_serializers import ReviewSerializer


class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]


class UserReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(reviewee_id=self.kwargs["user_id"]).select_related(
            "reviewer", "reviewee", "stay_request"
        )
