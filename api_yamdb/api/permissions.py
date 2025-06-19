from rest_framework.permissions import BasePermission, SAFE_METHODS


class AdminRole(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return request.user.role == 'admin' or request.user.is_superuser


class IsAuthorModeratorAdminOrReadOnly(BasePermission):
    message = 'Нет прав доступа.'

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user == obj.author
            or request.user.role == 'moderator'
            or request.user.role == 'admin'
        )
