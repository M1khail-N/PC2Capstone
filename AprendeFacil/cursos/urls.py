from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, EnrollmentViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r"courses", CourseViewSet)
router.register(r"enrollments", EnrollmentViewSet)

urlpatterns = [path("", include(router.urls))]