from apps.users.models import User

from .models import Notification


def notify_schedule_change(schedule, actor, action):
    recipients = User.objects.filter(role__in=[User.Role.ADMIN, User.Role.TEACHER]).exclude(id=getattr(actor, "id", None))
    notifications = [
        Notification(
            user=user,
            notification_type=Notification.Type.SCHEDULE_CHANGED,
            message=f"Schedule for {schedule.course.code} was {action} by {getattr(actor, 'username', 'system')}.",
            payload={
                "schedule_id": schedule.id,
                "course_id": schedule.course_id,
                "teacher_id": schedule.teacher_id,
                "action": action,
            },
        )
        for user in recipients
    ]
    if notifications:
        Notification.objects.bulk_create(notifications)


def notify_schedule_import(result, actor):
    recipients = User.objects.filter(role=User.Role.ADMIN)
    notifications = [
        Notification(
            user=user,
            notification_type=Notification.Type.SCHEDULE_IMPORTED,
            message=f"Schedule import finished by {getattr(actor, 'username', 'system')}. Imported {result['summary']['imported_rows']} rows.",
            payload=result["summary"],
        )
        for user in recipients
    ]
    if notifications:
        Notification.objects.bulk_create(notifications)
