from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.courses.views import CourseViewSet
from apps.notifications.views import NotificationViewSet
from apps.schedule.views import ScheduleImportView, ScheduleViewSet
from apps.system.views import SystemSettingsViewSet
from apps.users.views import UserViewSet


router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"schedules", ScheduleViewSet, basename="schedule")
router.register(r"notifications", NotificationViewSet, basename="notification")
router.register(r"system-settings", SystemSettingsViewSet, basename="system-settings")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/import/", ScheduleImportView.as_view(), name="schedule-import"),
    path("api/", include("apps.users.urls")),
]
