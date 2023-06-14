from rest_framework.permissions import BasePermission

class IsAuthority(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser