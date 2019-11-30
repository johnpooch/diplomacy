from django.conf import settings
from rest_framework import permissions


class IsAuthenticated(permissions.IsAuthenticated):
    """
    Overrides so that permissions are disabled during dev and enabled for
    tests.
    """
    def has_permission(self, request, view):
        if not settings.TESTING and settings.DEBUG:
            return True
        return bool(request.user and request.user.is_authenticated)


class IsCreatedByOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the user which created an object to edit
    it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user
