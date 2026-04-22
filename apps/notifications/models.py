from django.conf import settings
from django.db import models

from core.models import TimestampedModel


class Notification(TimestampedModel):
    class Type(models.TextChoices):
        SCHEDULE_CHANGED = "schedule_changed", "Schedule Changed"
        SCHEDULE_IMPORTED = "schedule_imported", "Schedule Imported"
        SYSTEM = "system", "System"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=32, choices=Type.choices, default=Type.SYSTEM)
    message = models.TextField()
    payload = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.notification_type} -> {self.user}"
