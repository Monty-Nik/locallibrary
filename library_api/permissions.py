from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает полный доступ администраторам, остальным только чтение
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsBookCreatorOrAdmin(permissions.BasePermission):
    """
    Разрешает редактирование только создателю книги или администратору
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешаем администраторам
        if request.user and request.user.is_staff:
            return True

        # Разрешаем создателю книги
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user

        return False