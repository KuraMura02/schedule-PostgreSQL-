from django.db.models import Q

from apps.system.models import SystemSettings


def get_overlap_filter(start_time, end_time):
    return Q(start_time__lt=end_time, end_time__gt=start_time)


def get_schedule_conflicts(day, start_time, end_time, teacher, room, student_group="", exclude_id=None):
    from apps.schedule.models import Schedule

    # Overlap condition: an existing slot starts before the new slot ends
    # and ends after the new slot starts.
    queryset = Schedule.objects.filter(day=day).filter(get_overlap_filter(start_time, end_time))
    if exclude_id:
        queryset = queryset.exclude(pk=exclude_id)

    conflicts = {}

    teacher_conflict = queryset.filter(teacher=teacher).exists()
    if teacher_conflict:
        conflicts["teacher"] = "Teacher already has another class during this time."

    room_conflict = queryset.filter(room__iexact=room).exists()
    if room_conflict:
        conflicts["room"] = "Room is already occupied during this time."

    settings = SystemSettings.get_solo()
    if settings.enforce_student_group_conflicts and student_group:
        student_group_conflict = queryset.filter(student_group__iexact=student_group).exists()
        if student_group_conflict:
            conflicts["student_group"] = "Student group already has another class during this time."

    if queryset.exists() and "non_field_errors" not in conflicts:
        conflicts["non_field_errors"] = ["Schedule overlaps with an existing slot."]

    return conflicts
