from typing import Any, Dict
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from .models import Appointment, Patient, PatientLogs, Payment, Treatment, DailyPatient
from .serializers import AppointmentCreationSerializer, AppointmentSerializer, PatientListSerializer, PatientLogsSerializer, PatientSerializer, TreatmentSerializer, DailySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import action
from .utils import get_curr_time
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page'
    max_page_size = 1000


class PatientView(ModelViewSet):
    queryset: Patient = Patient.objects.all()  # type:ignore
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):  # type:ignore
        if self.action in ["list", "retrieve"]:
            return PatientListSerializer
        else:
            return PatientSerializer

    @action(detail=False, methods=["GET"])
    def search(self, request):
        type_of = request.query_params.get("type")
        data = request.query_params.get("data")

        query_set = self.queryset

        if type_of == "number":
            query_set = query_set.filter(
                phone_no__icontains=data)  # type:ignore

        elif type_of == "name":
            query_set = query_set.filter(  # type:ignore
                Q(name__icontains=data) | Q(
                    last_name__icontains=data)  # type:ignore
            )

        else:
            return Response({"detail": "Invalid search type."}, status=400)

        page = self.paginate_queryset(query_set)
        if page is not None:
            serializer = PatientListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PatientListSerializer(query_set, many=True)
        return Response(serializer.data)

    def handle_treatments(
            self,
            *,
            treatments: Dict[str, Dict],
            request: Any,
            patient: Patient
    ) -> None:
        for _, treatment in treatments.items():
            treatment["patient"] = patient.id  # type:ignore
            serializer = TreatmentSerializer(data=treatment)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()

            PatientLogs.objects.create(  # type:ignore
                patient=patient,
                user=request.user,
                msg=f"Created Treatment '{instance.type_of_treatment}' With Price Of {
                    instance.amount} By {request.user.username} on {get_curr_time()}"
            )

            if treatment.get("paid", None):
                payment_instance = Payment.objects.create(  # type:ignore
                    treatment=instance,
                    amount=treatment.get("paid")
                )

                PatientLogs.objects.create(
                    patient=patient,
                    user=request.user,
                    msg=f"Received {treatment.get("paid")} by {request.user.username} on {
                        get_curr_time()}",
                )

    @action(
        detail=False,
        methods=["POST", "GET"],
        url_path='(?P<pk>\d+)/treatments',
        url_name="new treatment for user",
    )
    def new_treatment(self, request, pk=None):
        instance = self.get_object()
        if request.method == "GET":
            treatmentss = Treatment.objects.filter(
                patient=instance)  # type:ignore

            paginator = PageNumberPagination()
            paginator.page_size = 10
            paginated_treatmentss = paginator.paginate_queryset(
                treatmentss, request)

            serializer = TreatmentSerializer(paginated_treatmentss, many=True)

            return paginator.get_paginated_response(serializer.data)

        else:
            treatments = request.data.get("treatments")
            if not treatments:
                return Response(
                    {
                        "detail": "treatments required"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            self.handle_treatments(
                treatments=treatments,
                request=request,
                patient=instance
            )

            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    def create(self, request) -> Response:
        """
        Expects data like this,
        not mentioned fields are optional,
        although treatments and paid field is also optional
        {
          "name" : "Ahmad",
          "last_name" : "Hamidi",
          "age" : "22",
          "phone_no" : "0787676818",
          "gender" : "male",
          "treatments" : {
            "1" : {
              "teeths" : "1234",
              "amount" : "6000",
              "type_of_treatment" : "RCT",
              "paid" : "3000"
            }
          }
        }
        """

        serializer = PatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient: Patient = serializer.save()  # type:ignore

        PatientLogs.objects.create(  # type:ignore
            patient=patient,
            msg=f"Created by {request.user.username} on {get_curr_time()}",
            user=request.user
        )

        treatments = request.data.get("treatments")

        if not treatments:
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

        self.handle_treatments(
            treatments=treatments,
            request=request,
            patient=patient
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    def destroy(self, request, pk=None):
        instance: Patient = self.get_object()
        if request.data.get("archive", False):
            instance.archive = True  # type:ignore

            PatientLogs.objects.create(  # type:ignore
                user=request.user,
                patient=instance,
                msg=f"Archived By {request.user.username} on {get_curr_time()}"
            )
            instance.save()

        else:
            instance.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    def update(self, request, pk=None):
        instance = Patient.objects.get(id=pk)
        serializer = PatientSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        patient: Patient = serializer.save()  # type:ignore

        PatientLogs.objects.create(  # type:ignore
            patient=patient,
            msg=f"Updated by {request.user.username} on {get_curr_time()}",
            user=request.user
        )

        return Response(
            status=status.HTTP_200_OK
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        treatments = Treatment.objects.filter(
            patient=instance
        )
        treat_serializer = TreatmentSerializer(treatments, many=True)
        patient_logs = PatientLogs.objects.filter(
            patient=instance
        ).order_by("-created_at")

        logs_serializer = PatientLogsSerializer(patient_logs, many=True)
        serializer = PatientSerializer(instance)
        return Response(
            {
                "data": serializer.data,
                "logs": logs_serializer.data,
                "treatments": treat_serializer.data
            },
        )


class AppointmentViewSet(DestroyModelMixin, ListModelMixin, CreateModelMixin, GenericViewSet):
    queryset = Appointment.objects.all()
    serializer_class = Appointment

    def list(self, request):
        day = request.GET.get("day")
        if not day:
            return Response(
                {
                    "detail": "day required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        appointments = Appointment.objects.filter(
            day=day
        ).order_by("time")

        serializer = AppointmentSerializer(appointments, many=True)
        return Response(
            serializer.data
        )

    def create(self, request, *args, **kwargs):
        instance = AppointmentCreationSerializer(data=request.data)
        instance.is_valid(raise_exception=True)
        instance.save()
        return Response(
            instance.data
        )


class TreatmentViewSet(
    RetrieveModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
    GenericViewSet
):
    queryset: object = Treatment.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = TreatmentSerializer

    @ action(
        detail=False,
        methods=["POST", "GET"],
        url_path='(?P<pk>\d+)/pay',
        url_name="new treatment for user",
    )
    def pay_fees(self, request, pk=None):
        instance = self.get_object()
        paid = request.data.get("paid")
        if not paid:
            return Response(
                {
                    "detail": "paid required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if instance.remaining_amount() < int(paid):
            return Response(
                {
                    "wrong amount": "amount should less than required amount",
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        payment_instance = Payment.objects.create(  # type:ignore
            treatment=instance,
            amount=paid
        )

        PatientLogs.objects.create(
            patient=instance.patient,
            user=request.user,
            msg=f"Received {paid} by {
                request.user.username} on {get_curr_time()}"
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class DailyViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = DailyPatient.objects.all()
    serializer_class = DailySerializer

    def list(self, request):
        day = request.GET.get("day")
        if not day:
            return Response(
                {
                    "Param Required": "Day Rquired"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        daily = DailyPatient.objects.filter(day=day)
        serailizer = DailySerializer(daily, many=True)
        return Response(
            serailizer.data
        )
