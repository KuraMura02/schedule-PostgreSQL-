# Schedule Management Backend

Production-oriented backend for university or school scheduling with Django, DRF, PostgreSQL, and Docker.

## Features

- API-first CRUD for users, courses, schedules, notifications, and system settings
- Role-aware write permissions with dynamic system mode stored in the database
- Schedule conflict validation for time overlap, teacher, room, and optional student group collisions
- Import endpoint for `.xlsx` and `.pdf` schedule files with row-level logging and validation
- Notification stubs triggered on schedule changes and imports
- Export service scaffold with implemented `.ics` output and extension points for Excel/PDF
- Environment-based settings, logging, pagination, filtering, and Dockerized deployment

## Stack

- Django
- Django REST Framework
- PostgreSQL
- Docker / docker-compose

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

API will be available at `http://localhost:8000/api/`.

## Main Endpoints

- `GET/POST /api/users/`
- `GET/POST /api/courses/`
- `GET/POST /api/schedules/`
- `GET/POST /api/notifications/`
- `GET/POST /api/system-settings/`
- `POST /api/import/`
- `GET /api/schedules/export/?format=ics`

## Filtering

Schedules support filtering by:

- `day`
- `course`
- `teacher`
- `student_group`

## Import Contract

### Excel columns

Required columns:

- `day`
- `start_time`
- `end_time`
- `room`
- `teacher`
- `course`

Optional column:

- `student_group`

### PDF format

Each line should look like:

```text
mon | 09:00 | 10:30 | A-101 | teacher_username | CS101 | Group A
```

## System Modes

- `self`: students can mutate schedules
- `fixed`: teachers can mutate schedules
- `hybrid`: students and teachers can mutate schedules
- `admin`: always has full write access regardless of mode

## Notes

- Conflict detection is enforced in both serializer validation and model `clean()`.
- Student group conflict checks are enabled through `SystemSettings.enforce_student_group_conflicts`.
- Excel/PDF import currently uses parser-driven extraction with an architecture that can be extended with AI parsing later.
