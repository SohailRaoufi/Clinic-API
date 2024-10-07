from django.contrib import admin
from django.urls import include, path
from user.views import JwtToken, Staff
from rest_framework import routers
from patient.views import AppointmentViewSet, PatientView, TreatmentViewSet


router = routers.DefaultRouter()
router.register("patient", PatientView)
router.register("treatment", TreatmentViewSet)
router.register("appointment", AppointmentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/", JwtToken.as_view()),
    path("api/auth/create", Staff.as_view())
]
