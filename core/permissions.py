from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.system.models import SystemSettings
from apps.users.models import User


class ReadOnlyOrAdminPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.ADMIN)


class UserManagementPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.ADMIN)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == User.Role.ADMIN or request.user.pk == obj.pk


class NotificationPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return not request.user.is_authenticated or obj.user_id == request.user.id or request.user.role == User.Role.ADMIN
        return bool(request.user and request.user.is_authenticated and (obj.user_id == request.user.id or request.user.role == User.Role.ADMIN))


class CoursePermission(BasePermission):
    allowed_write_roles = {User.Role.TEACHER, User.Role.ADMIN}

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.role in self.allowed_write_roles)


class SystemSettingsPermission(ReadOnlyOrAdminPermission):
    pass


class SchedulePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == User.Role.ADMIN:
            return True

        # The active scheduling policy lives in the database and can be changed without redeploying.
        mode = SystemSettings.get_solo().mode
        if mode == SystemSettings.Mode.SELF_SERVICE:
            return request.user.role == User.Role.STUDENT
        if mode == SystemSettings.Mode.FIXED:
            return request.user.role == User.Role.TEACHER
        return request.user.role in {User.Role.STUDENT, User.Role.TEACHER}
