from django.contrib import admin

from .models import Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("course", "teacher", "day", "start_time", "end_time", "room", "student_group")
    list_filter = ("day", "teacher", "course")
    search_fields = ("course__code", "course__name", "teacher__username", "room", "student_group")
