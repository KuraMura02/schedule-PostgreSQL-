from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.courses.models import Course
from core.models import TimestampedModel

from .services.conflicts import get_schedule_conflicts


class Schedule(TimestampedModel):
    class Day(models.TextChoices):
        MONDAY = "mon", "Monday"
        TUESDAY = "tue", "Tuesday"
        WEDNESDAY = "wed", "Wednesday"
        THURSDAY = "thu", "Thursday"
        FRIDAY = "fri", "Friday"
        SATURDAY = "sat", "Saturday"
        SUNDAY = "sun", "Sunday"

    day = models.CharField(max_length=3, choices=Day.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=64)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="teaching_schedules",
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="schedules")
    student_group = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ["day", "start_time", "room"]
        indexes = [
            models.Index(fields=["day", "start_time", "end_time"]),
            models.Index(fields=["teacher", "day", "start_time"]),
            models.Index(fields=["room", "day", "start_time"]),
            models.Index(fields=["course", "day", "start_time"]),
        ]

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError({"end_time": "End time must be later than start time."})
        if getattr(self.teacher, "role", None) and self.teacher.role != "teacher":
            raise ValidationError({"teacher": "Selected user must have the teacher role."})

        conflicts = get_schedule_conflicts(
            day=self.day,
            start_time=self.start_time,
            end_time=self.end_time,
            teacher=self.teacher,
            room=self.room,
            student_group=self.student_group,
            exclude_id=self.pk,
        )
        if conflicts:
            raise ValidationError(conflicts)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course} / {self.day} {self.start_time}-{self.end_time}"
