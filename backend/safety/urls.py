from django.urls import path

from .views import BlockListCreateView, ReportCreateView, UnblockView

urlpatterns = [
    path("reports/", ReportCreateView.as_view(), name="report-create"),
    path("blocks/", BlockListCreateView.as_view(), name="block-list"),
    path("blocks/<int:user_id>/", UnblockView.as_view(), name="block-delete"),
]
