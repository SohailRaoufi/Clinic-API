# Permissions
from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser  


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_staff and not request.user.is_superuser


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff and not request.user.is_superuser


class IsAdminOrStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.is_staff

