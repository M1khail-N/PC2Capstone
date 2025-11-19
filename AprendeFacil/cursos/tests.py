from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer


# ============================================================
# 1) TESTS DE MODELOS
# ============================================================

class CourseModelTest(TestCase):

    def test_str_representation(self):
        course = Course.objects.create(title="Python Básico")
        self.assertEqual(str(course), "Python Básico")


class EnrollmentModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="user1")
        self.course = Course.objects.create(title="Curso Test")
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course,
            progress=10.0
        )

    def test_advance_increases_progress(self):
        new_progress = self.enrollment.advance(20)
        self.assertEqual(new_progress, 30.0)

    def test_advance_clamps_to_100(self):
        new_progress = self.enrollment.advance(999)
        self.assertEqual(new_progress, 100.0)

    def test_advance_clamps_to_zero(self):
        new_progress = self.enrollment.advance(-999)
        self.assertEqual(new_progress, 0.0)


# ============================================================
# 2) TESTS DE SERIALIZERS
# ============================================================

class CourseSerializerTest(TestCase):

    def test_course_serializer(self):
        course = Course.objects.create(
            title="Django Avanzado",
            description="Construyendo APIs"
        )
        serializer = CourseSerializer(course)
        data = serializer.data

        self.assertIn("id", data)
        self.assertEqual(data["title"], "Django Avanzado")
        self.assertEqual(data["description"], "Construyendo APIs")


class EnrollmentSerializerTest(TestCase):

    def test_enrollment_serializer(self):
        user = User.objects.create_user(username="user2")
        course = Course.objects.create(title="Docker Básico")

        enrollment = Enrollment.objects.create(
            user=user,
            course=course,
            progress=50.0
        )

        serializer = EnrollmentSerializer(enrollment)
        data = serializer.data

        self.assertEqual(data["user"], user.id)
        self.assertEqual(data["course"], course.id)
        self.assertAlmostEqual(float(data["progress"]), 50.0)


# ============================================================
# 3) TESTS DE API (INTEGRACIÓN)
# ============================================================

class CourseAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_course(self):
        payload = {
            "title": "Nuevo Curso",
            "description": "Descripción"
        }
        resp = self.client.post("/api/courses/", payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["title"], "Nuevo Curso")


class EnrollmentAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="alumno")
        self.course = Course.objects.create(title="Curso API")
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course
        )

    def test_create_enrollment(self):
        payload = {
            "user": self.user.id,
            "course": self.course.id
        }
        resp = self.client.post("/api/enrollments/", payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["progress"], 0.0)

    def test_advance_progress_api(self):
        url = f"/api/enrollments/{self.enrollment.id}/advance/"
        resp = self.client.post(url, {"percent": 25}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["progress"], 25.0)