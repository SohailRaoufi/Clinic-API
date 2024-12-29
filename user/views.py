from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate

from patient.models import Patient, Payment, DailyPatient
from user.perms import IsAdmin
from .consumers import get_room, sync_get_room
from user.models import Messages, Task
from .token_factory import create_token
from django.contrib.auth.models import User
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from .serializers import StaffSerializer
from rest_framework.permissions import IsAuthenticated, BasePermission
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .serializers import MsgSerializer, TaskSerializer
from django.utils.dateparse import parse_date
from django.db.models import Sum
from datetime import datetime
from django.db.models import Q
from rest_framework.decorators import action


class ChatViewSet(ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = StaffSerializer

    def list(self, request, *args, **kwargs):
        all_users = User.objects.exclude(id=request.user.id)
        serializer = StaffSerializer(all_users, many=True)
        return Response(
            serializer.data
        )

    def create(self, request):
        patient = request.data.get("id")
        patient_instance = get_object_or_404(Patient, id=patient)
        users = request.data.get("users").split(",")
        channel_layer = get_channel_layer()
        for user_email in users:
            try:
                user = User.objects.get(email=user_email)
            except Exception as e:
                print(str(e))

            if user:  # type:ignore
                room = sync_get_room(request.user, user)
                msg = Messages.objects.create(  # type:ignore
                    room=room,
                    type="share",
                    text=f"{patient_instance.id},{patient_instance.name} {
                        patient_instance.last_name}",
                    sender=request.user,
                    receiver=user
                )
                async_to_sync(channel_layer.group_send)(  # type:ignore
                    f"room_{room.id}",  # type:ignore
                    {
                        "type": "chat_message",
                        "message": MsgSerializer(msg).data
                    }
                )
        return Response(status=status.HTTP_201_CREATED)

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    
    def get_permissions(self):
        if self.request.method == "GET" or self.request.method == "PATCH":
            return [IsAuthenticated()]
        else:
            return [IsAdmin()]
    
    def list(self,request):
        date = request.GET.get("date")

        if not date:
            return Response(
                {
                    "date":"date Param Required!"
                },
                status = status.HTTP_400_BAD_REQUEST
            )
        tasks = Task.objects.filter(created_at=date).order_by("status")

        serializer = TaskSerializer(tasks, many = True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    @action(detail = False, methods=["GET"])
    def userTasks(self,request):
        date = request.GET.get("date")

        if not date:
            return Response(
                {
                    "date":"date Param Required!"
                },
                status = status.HTTP_400_BAD_REQUEST
            )
        tasks = Task.objects.filter(created_at=date, assigned_to=request.user.id).order_by("status")

        serializer = TaskSerializer(tasks, many = True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    def partial_update(self,request, pk = None):
        try:
            task = Task.objects.get(id=pk)
        except Task.DoesNotExist:
            return Response(
                {"error": "Task not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TaskSerializer(instance=task, data=request.data, partial = True)

        if not serializer.is_valid():
            return Response(
                {
                    "wrong" :"Wront data sent!"
                },
            )
        serializer.save()
        return Response(
            serializer.data
            ,status=status.HTTP_200_OK)


class JwtToken(APIView):
    def post(self, request):
        email = request.data.get("username", None)
        password = request.data.get("password", None)
        if not email or not password:
            return Response(
                {"detail": "'username' and 'password' required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=email, password=password)
        if user:
            token = create_token(user)
            return Response(
                {
                    "token": token,
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Invalid User"},
                status=status.HTTP_400_BAD_REQUEST
            )








class Staff(ModelViewSet):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = StaffSerializer
    permission_classes = [IsAdmin]

    def create_user(self, username, password, email,is_staff):
        user = User.objects.create_user(
            username=username, email=email, password=password, is_staff=is_staff
        )
        user.save()

    def create(self, request):
        username = request.data.get("username", None)
        email = request.data.get("email", None)
        password = request.data.get("password", None)
        role = request.data.get("role","STAFF")

        if not username or not password:
            return Response(
                {"detail": "'username' and 'password' required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        is_staff = True if role == "STAFF" else False
        self.create_user(username, password, email,is_staff=is_staff)
        return Response(
            status=status.HTTP_200_OK
        )


class AnalyticsAPIView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        analytics_type = request.query_params.get("type")
        data = request.query_params.get("data")

        if not analytics_type or not data:
            return Response({"error": "Both 'type' and 'data' parameters are required."}, status=400)

        try:
            if analytics_type == 'day':
                date_obj = parse_date(data)
                if not date_obj:
                    raise ValueError
            elif analytics_type == 'month':
                date_obj = datetime.strptime(data, "%Y-%m")
            elif analytics_type == 'year':
                date_obj = datetime.strptime(data, "%Y")
            else:
                return Response({"error": "Invalid 'type' parameter. Use 'day', 'month', or 'year'."}, status=400)
        except ValueError:
            return Response({"error": "Invalid 'data' format."}, status=400)

        if analytics_type == 'day':
            payments_daily_patient = DailyPatient.objects.filter(
                day=date_obj)  # type:ignore
            payments_treatment = Payment.objects.filter(
                created_at__date=date_obj)  # type:ignore

            result = []
            total_payment = 0
            for payment in payments_daily_patient:
                result.append({
                    "name": payment.name,
                    "payment": payment.payment,
                    "source": "DailyPatient"
                })
                total_payment += payment.payment

            for payment in payments_treatment:
                result.append({
                    "name": payment.treatment.patient.full_name(),
                    "payment": payment.amount,
                    "name": payment.treatment.type_of_treatment,
                    "source": "Treatment"
                })
                total_payment += payment.amount

            return Response({
                "date": data,
                "payments": result,
                "total": total_payment
            })

        elif analytics_type == 'month':
            payments_daily_patient = DailyPatient.objects.filter(
                day__year=date_obj.year, day__month=date_obj.month)  # type:ignore
            payments_treatment = Payment.objects.filter(
                created_at__year=date_obj.year, created_at__month=date_obj.month)  # type:ignore

            result = {}
            total_payment = 0
            for payment in payments_daily_patient:
                day_str = payment.day.strftime("%Y-%m-%d")
                if day_str not in result:
                    result[day_str] = 0
                result[day_str] += payment.payment
                total_payment += payment.payment

            for payment in payments_treatment:
                day_str = payment.created_at.strftime("%Y-%m-%d")
                if day_str not in result:
                    result[day_str] = 0
                result[day_str] += payment.amount
                total_payment += payment.amount

            return Response({
                "month": data,
                "daily_payments": result,
                "total": total_payment
            })

        elif analytics_type == 'year':
            payments_daily_patient = DailyPatient.objects.filter(
                day__year=date_obj.year)  # type:ignore
            payments_treatment = Payment.objects.filter(
                created_at__year=date_obj.year)  # type:ignore

            result = {}
            total_payment = 0
            for payment in payments_daily_patient:
                month_str = payment.day.strftime("%Y-%m")
                if month_str not in result:
                    result[month_str] = 0
                result[month_str] += payment.payment
                total_payment += payment.payment

            for payment in payments_treatment:
                month_str = payment.created_at.strftime("%Y-%m")
                if month_str not in result:
                    result[month_str] = 0
                result[month_str] += payment.amount
                total_payment += payment.amount
            return Response({
                "year": data,
                "monthly_payments": result,
                "total": total_payment
            })
