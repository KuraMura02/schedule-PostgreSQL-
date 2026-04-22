from datetime import time

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.courses.models import Course
from apps.schedule.models import Schedule
from apps.system.models import SystemSettings
from apps.users.models import User


class ScheduleConflictTests(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="teacher1", password="pass123", role=User.Role.TEACHER)
        self.course = Course.objects.create(code="CS101", name="Algorithms")
        Schedule.objects.create(
            day=Schedule.Day.MONDAY,
            start_time=time(9, 0),
            end_time=time(10, 0),
            room="A-101",
            teacher=self.teacher,
            course=self.course,
        )

    def test_teacher_time_overlap_is_rejected(self):
        self.client.force_authenticate(user=self.teacher)
        serializer_data = {
            "day": Schedule.Day.MONDAY,
            "start_time": "09:30:00",
            "end_time": "10:30:00",
            "room": "B-202",
            "teacher": self.teacher.id,
            "course": self.course.id,
            "student_group": "",
        }
        response = self.client.post(reverse("schedule-list"), serializer_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SchedulePermissionTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username="student1", password="pass123", role=User.Role.STUDENT)
        self.teacher = User.objects.create_user(username="teacher2", password="pass123", role=User.Role.TEACHER)
        self.course = Course.objects.create(code="MATH101", name="Discrete Math")
        self.settings = SystemSettings.get_solo()
        self.payload = {
            "day": Schedule.Day.TUESDAY,
            "start_time": "11:00:00",
            "end_time": "12:00:00",
            "room": "B-201",
            "teacher": self.teacher.id,
            "course": self.course.id,
            "student_group": "G-1",
        }

    def test_student_cannot_create_schedule_in_fixed_mode(self):
        self.settings.mode = SystemSettings.Mode.FIXED
        self.settings.save()
        self.client.force_authenticate(user=self.student)

        response = self.client.post(reverse("schedule-list"), self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_create_schedule_in_fixed_mode(self):
        self.settings.mode = SystemSettings.Mode.FIXED
        self.settings.save()
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(reverse("schedule-list"), self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
