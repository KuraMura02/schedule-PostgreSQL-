from datetime import date, datetime, timedelta


DAY_TO_ICS = {
    "mon": "MO",
    "tue": "TU",
    "wed": "WE",
    "thu": "TH",
    "fri": "FR",
    "sat": "SA",
    "sun": "SU",
}

DAY_TO_INDEX = {
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6,
}


class ScheduleExportService:
    def __init__(self, queryset):
        self.queryset = queryset.select_related("course", "teacher")

    def export(self, export_format):
        if export_format == "ics":
            content = self._build_ics()
            return content, "text/calendar", f"schedules-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.ics"
        if export_format in {"xlsx", "pdf"}:
            raise NotImplementedError(f"{export_format.upper()} export is prepared as an extension point and not implemented yet.")
        raise NotImplementedError("Unsupported export format.")

    def _build_ics(self):
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Schedule Backend//EN",
            "CALSCALE:GREGORIAN",
        ]
        for schedule in self.queryset:
            # Schedule stores weekday + time only, so we export a weekly recurring event
            # anchored to the next occurrence of that weekday.
            start_at, end_at = self._next_occurrence(schedule.day, schedule.start_time, schedule.end_time)
            lines.extend(
                [
                    "BEGIN:VEVENT",
                    f"UID:schedule-{schedule.pk}@schedule-backend",
                    f"SUMMARY:{schedule.course.code} {schedule.course.name}",
                    f"DESCRIPTION:Teacher {schedule.teacher.username}; Room {schedule.room}",
                    f"LOCATION:{schedule.room}",
                    f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
                    f"DTSTART:{start_at.strftime('%Y%m%dT%H%M%S')}",
                    f"DTEND:{end_at.strftime('%Y%m%dT%H%M%S')}",
                    f"RRULE:FREQ=WEEKLY;BYDAY={DAY_TO_ICS[schedule.day]}",
                    "END:VEVENT",
                ]
            )
        lines.append("END:VCALENDAR")
        return "\r\n".join(lines)

    @staticmethod
    def _next_occurrence(day_code, start_time, end_time):
        today = date.today()
        target_index = DAY_TO_INDEX[day_code]
        delta_days = (target_index - today.weekday()) % 7
        target_date = today + timedelta(days=delta_days)
        return (
            datetime.combine(target_date, start_time),
            datetime.combine(target_date, end_time),
        )
