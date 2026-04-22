from rest_framework import serializers

from apps.courses.models import Course
from apps.system.models import SystemSettings
from apps.users.models import User

from .models import Schedule
from .services.conflicts import get_schedule_conflicts


class ScheduleSerializer(serializers.ModelSerializer):
    teacher_detail = serializers.StringRelatedField(source="teacher", read_only=True)
    course_detail = serializers.StringRelatedField(source="course", read_only=True)

    class Meta:
        model = Schedule
        fields = [
            "id",
            "day",
            "start_time",
            "end_time",
            "room",
            "teacher",
            "teacher_detail",
            "course",
            "course_detail",
            "student_group",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_teacher(self, value):
        if value.role != User.Role.TEACHER:
            raise serializers.ValidationError("Selected user must have the teacher role.")
        return value

    def validate_course(self, value):
        if not isinstance(value, Course):
            raise serializers.ValidationError("Invalid course.")
        return value

    def validate(self, attrs):
        instance = self.instance
        day = attrs.get("day", getattr(instance, "day", None))
        start_time = attrs.get("start_time", getattr(instance, "start_time", None))
        end_time = attrs.get("end_time", getattr(instance, "end_time", None))
        teacher = attrs.get("teacher", getattr(instance, "teacher", None))
        room = attrs.get("room", getattr(instance, "room", None))
        student_group = attrs.get("student_group", getattr(instance, "student_group", ""))

        if end_time <= start_time:
            raise serializers.ValidationError({"end_time": "End time must be later than start time."})

        conflicts = get_schedule_conflicts(
            day=day,
            start_time=start_time,
            end_time=end_time,
            teacher=teacher,
            room=room,
            student_group=student_group,
            exclude_id=getattr(instance, "pk", None),
        )
        if conflicts:
            raise serializers.ValidationError(conflicts)
        return attrs


class ScheduleImportSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        ext = value.name.rsplit(".", 1)[-1].lower() if "." in value.name else ""
        if ext not in {"xlsx", "pdf"}:
            raise serializers.ValidationError("Supported formats are .xlsx and .pdf.")
        return value


class ExportQuerySerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=("xlsx", "pdf", "ics"))


class SystemModeAwareSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=SystemSettings.Mode.choices)
