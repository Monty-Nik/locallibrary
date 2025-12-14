from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):


    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsBookCreatorOrAdmin(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешение администраторам
        if request.user and request.user.is_staff:
            return True

        # Разрешение создателю книги
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user

        return False