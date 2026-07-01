from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, StudentViewSet, EnrollmentViewSet

router = DefaultRouter()

router.register(r'courses', CourseViewSet)
router.register(r'students', StudentViewSet)
router.register(r'enrollments', EnrollmentViewSet)

urlpatterns = router.urls