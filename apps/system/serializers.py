from rest_framework import serializers

from .models import SystemSettings


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = [
            "id",
            "mode",
            "enforce_student_group_conflicts",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
