from datetime import datetime


def format_schedule_time(start, end):
    return f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"


def current_day():
    return datetime.now().strftime("%A")


def success_response(data=None, message="OK"):
    return {"status": "success", "message": message, "data": data}


def error_response(message="Error", data=None):
    return {"status": "error", "message": message, "data": data}
