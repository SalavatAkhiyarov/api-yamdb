from rest_framework.permissions import BasePermission, SAFE_METHODS


class AdminRole(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return request.user.is_admin


class IsAuthorModeratorAdminOrReadOnly(BasePermission):
    message = 'Нет прав доступа.'

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user == obj.author
            or request.user.is_moderator
            or request.user.is_admin
        )


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )
