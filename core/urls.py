from django.contrib import admin
from django.urls import include, path

from .backup import BackupView
from user.views import AnalyticsAPIView,ChatViewSet, JwtToken, Staff, TaskViewSet
from rest_framework import routers
from patient.views import AppointmentViewSet, DentalLabViewSet, MedicineViewSet, PatientView, TreatmentViewSet, DailyViewSet
from django.conf.urls.static import static
from django.conf import settings

router = routers.DefaultRouter()
router.register("patient", PatientView)
router.register("treatment", TreatmentViewSet)
router.register("appointment", AppointmentViewSet)
router.register("staff", Staff)
router.register("chats", ChatViewSet, basename="chats")
router.register("daily", DailyViewSet, basename="daily")
router.register("tasks", TaskViewSet)
router.register("medicine", MedicineViewSet,basename="medicine")
router.register('lab',DentalLabViewSet,basename="dentallab")

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/", JwtToken.as_view()),
    path("api/analytics/",AnalyticsAPIView.as_view()),
    path("api/backup/",BackupView.as_view())
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
