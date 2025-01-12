from rest_framework import serializers

from patient.models import (
        Appointment,
        DentalLab,
        Patient,
        PatientLogs,
        Treatment,
        DailyPatient,
        Payment
)


class DentalLabSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    class Meta:
        model = DentalLab
        fields = "__all__"
    

    def get_status(self,obj):
        return obj.status






class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = DentalLab
        fields = "__all__"




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




class PaymentSerializer(serializers.ModelSerializer):
    treatment_name = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    

    class Meta:
        model = Payment
        fields = "__all__"
    
    
    def get_total_amount(self,obj):
        return obj.treatment.amount

    def get_remaining_amount(self,obj):
        return obj.treatment.remaining_amount()

    def get_treatment_name(self,obj):
        return obj.treatment.type_of_treatment

    def get_patient(self,obj):
        return obj.treatment.patient.full_name


