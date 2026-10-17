from django.urls import path

from .review_views import ReviewCreateView, UserReviewListView
from .views import StayActionView, StayRequestDetailView, StayRequestListCreateView

urlpatterns = [
    path("stay-requests/", StayRequestListCreateView.as_view(), name="stay-request-list"),
    path("stay-requests/<int:pk>/", StayRequestDetailView.as_view(), name="stay-request-detail"),
    path("stay-requests/<int:pk>/<str:action>/", StayActionView.as_view(), name="stay-request-action"),
    path("reviews/", ReviewCreateView.as_view(), name="review-create"),
    path("users/<int:user_id>/reviews/", UserReviewListView.as_view(), name="user-reviews"),
]
