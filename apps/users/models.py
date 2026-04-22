from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import TimestampedModel


class User(AbstractUser, TimestampedModel):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=16, choices=Role.choices, default=Role.STUDENT)

    class Meta:
        ordering = ["username"]

    def __str__(self):
        return f"{self.username} ({self.role})"
