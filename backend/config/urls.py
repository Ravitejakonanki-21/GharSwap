from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from accounts.urls import profile_urlpatterns
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health(_request):
    return Response({"status": "ok", "service": "gharswap"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/health/", health),
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/", include((profile_urlpatterns, "accounts"), namespace="profiles")),
    path("api/v1/", include("listings.urls")),
    path("api/v1/", include("stays.urls")),
    path("api/v1/", include("credits.urls")),
    path("api/v1/", include("safety.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
