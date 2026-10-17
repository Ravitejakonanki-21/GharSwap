from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """Object owner is `user`, `host`, or `owner` depending on the model."""

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "user", None) or getattr(obj, "host", None)
        return owner == request.user


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, "user", None) or getattr(obj, "host", None)
        return owner == request.user


class IsParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        guest = getattr(obj, "guest", None)
        listing = getattr(obj, "listing", None)
        host = getattr(listing, "host", None) if listing is not None else getattr(obj, "host", None)
        return request.user in {guest, host}
