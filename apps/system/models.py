from django.core.exceptions import ValidationError
from django.db import models

from core.models import TimestampedModel


class SystemSettings(TimestampedModel):
    class Mode(models.TextChoices):
        SELF_SERVICE = "self", "Self"
        FIXED = "fixed", "Fixed"
        HYBRID = "hybrid", "Hybrid"

    singleton_enforcer = models.PositiveSmallIntegerField(default=1, unique=True, editable=False)
    mode = models.CharField(max_length=16, choices=Mode.choices, default=Mode.HYBRID)
    enforce_student_group_conflicts = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "System settings"

    def clean(self):
        if self.singleton_enforcer != 1:
            raise ValidationError({"singleton_enforcer": "System settings must use the singleton marker 1."})

    def save(self, *args, **kwargs):
        self.singleton_enforcer = 1
        self.full_clean()
        return super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(singleton_enforcer=1)
        return obj

    def __str__(self):
        return f"System mode: {self.mode}"
