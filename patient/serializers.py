from rest_framework import serializers

from patient.models import Appointment, Patient, PatientLogs, Treatment, DailyPatient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        exclude = ["created_at", "updated_at"]


class PatientLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientLogs
        fields = "__all__"


class AppointmentCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"


class AppointmentSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        exclude = ["created_at", "updated_at"]

    def get_time(self, obj):
        return obj.time.strftime("%I:%M %p")


class TreatmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    patient_last_name = serializers.SerializerMethodField()
    real_amount = serializers.SerializerMethodField()

    class Meta:
        model = Treatment
        fields = "__all__"

    def get_real_amount(self, obj):
        return obj.remaining_amount()

    def get_patient_name(self, obj):
        return obj.patient.name

    def get_patient_last_name(self, obj):
        return obj.patient.last_name


class PatientListSerializer(serializers.ModelSerializer):
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = "__all__"

    def get_total_amount(self, obj):
        return obj.total_amount()


class DailySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPatient
        fields = "__all__"
