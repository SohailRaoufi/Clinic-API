from django.contrib import admin
from django.urls import include, path
from user.views import ChatViewSet, JwtToken, Staff
from rest_framework import routers
from patient.views import AppointmentViewSet, PatientView, TreatmentViewSet, DailyViewSet
from django.conf.urls.static import static
from django.conf import settings

router = routers.DefaultRouter()
router.register("patient", PatientView)
router.register("treatment", TreatmentViewSet)
router.register("appointment", AppointmentViewSet)
router.register("staff", Staff)
router.register("chats", ChatViewSet, basename="chats")
router.register("daily", DailyViewSet, basename="daily")


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/", JwtToken.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
