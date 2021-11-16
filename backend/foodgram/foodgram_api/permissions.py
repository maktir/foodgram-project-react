from rest_framework import permissions


class RecipePermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if view.action in ('create', 'update',
                           'partial_update', 'delete'):
            return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return True
        if view.action in ['update', 'partial_update', 'destroy']:
            if (request.user == obj.author
                    or request.user.is_staff):
                return True
            return False
        return False
