from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone


GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female')
]

MARTIAL_STATUS_CHOICES = [
    ('married', 'Married'),
    ('single', 'Single')
]

TREATMENT_CHOICES = [
    ("Extraction", "Extraction"),
    ("Apoxtomy", "Apoxtomy"),
    ("Colemectomy", "Colemectomy"),
    ("RCT", "RCT"),
    ("Filling", "Filling"),
    ("Repair & Retreive", "Repair & Retreive"),
    ("Implant", "Implant"),
    ("Orthodontics", "Orthodontics"),
    ("Removable Denture", "Removable Denture"),
    ("Crown Metal", "Crown Metal"),
    ("Crown Porcelin", "Crown Porcelin"),
    ("Crown Zarconia", "Crown Zarconia"),
    ("Crown Cadlcam", "Crown Cadlcam"),
    ("Preflex Felxinylon", "Preflex Felxinylon"),
    ("Scaling & Air Polishing", "Scaling & Air Polishing"),
    ("Tooth gems", "Tooth gems"),
    ("Bleach", "Bleach"),
    ("Venner", "Venner")
]


class Patient(models.Model):
    name = models.CharField(blank=False, null=False, max_length=250)
    last_name = models.CharField(blank=False, null=False, max_length=250)
    addr = models.CharField(max_length=250, null=True, blank=True)
    job = models.CharField(max_length=250, null=True, blank=True)
    age = models.IntegerField()
    phone_regex = r"^07[02346789]\d{7}|02[0]\d{7}"
    phone_validator = RegexValidator(
        regex=phone_regex, message="Enter a valid phone number."
    )
    phone_no = models.CharField(
        max_length=55, validators=[phone_validator], blank=False, null=False, unique=True
    )
    gender = models.CharField(choices=GENDER_CHOICES, max_length=25)
    martial_status = models.CharField(
        choices=MARTIAL_STATUS_CHOICES, max_length=25, default="single")

    hiv = models.BooleanField(default=False)
    hcv = models.BooleanField(default=False)
    hbs = models.BooleanField(default=False)
    pregnancy = models.BooleanField(default=False)
    diabetes = models.BooleanField(default=False)
    reflux_esophagitis = models.BooleanField(default=False)
    xray = models.CharField(max_length=250, null=True, blank=True)
    archive = models.BooleanField(default=False)

    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name} {self.last_name}"

    def total_amount(self) -> int:
        res = 0
        for treatment in Treatment.objects.filter(
                patient=self
        ):
            res += treatment.remaining_amount()
        return res
    
    @property
    def full_name(self) -> str:
        return f"{self.name} {self.last_name}"


class PatientLogs(models.Model):
    msg = models.TextField(blank=False, null=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.msg)


class Treatment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    type_of_treatment = models.CharField(
        max_length=100, choices=TREATMENT_CHOICES)
    teeths = models.CharField(max_length=250, blank=False, null=False)
    amount = models.IntegerField(blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def remaining_amount(self) -> int:
        return self.amount-self.total_paid()

    def total_paid(self) -> int:
        total = 0
        for payment in Payment.objects.filter(
            treatment=self
        ):
            total += payment.amount

        return total

    def __str__(self) -> str:
        return str(self.teeths)


class Payment(models.Model):
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    amount = models.IntegerField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.amount)


class Appointment(models.Model):
    day = models.DateField(blank=False, null=False)
    time = models.TimeField(blank=False, null=False)
    patient = models.CharField(max_length=250, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.patient} {self.time}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["day","time"],name="unique_pair_day_time")
        ]


class DailyPatient(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    payment = models.IntegerField(blank=False, null=False)
    day = models.DateField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)





class DentalLab(models.Model):
    name = models.CharField(max_length=256,null=False,blank=False)
    day = models.DateTimeField() 
    to = models.DateTimeField()
    patient = models.ForeignKey(Patient, null=True, blank=True, on_delete=models.CASCADE)
    labratory_name = models.CharField(max_length=256,null=True,blank=True)
    dental_type = models.CharField(max_length=256,null=True,blank=True)
    # just to make sure
    phone_no = models.CharField(max_length=128,null=True,blank=True)
    teeths = models.CharField(max_length=250, blank=False, null=False)
    is_called = models.BooleanField(default=False)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return self.name

    @property
    def status(self):
        if self.is_done:
            return "done"
        elif self.is_called:
            return "waiting"
        elif self.to > timezone.now():
            return "pending"
        else:
            return "warning"


class Perscription(models.Model):
    patient = models.ForeignKey(Patient,null=True,blank=True,on_delete=models.CASCADE)
    name = models.CharField(max_length=150,null=True,blank=True)
    age = models.IntegerField(null=True,blank=True)
    gender = models.CharField(max_length=120,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return self.name


class Medicine(models.Model):
    name = models.CharField(max_length=250,null=False,blank=False)
    company = models.CharField(max_length=250,null=False,blank=False)
    issue_date = models.DateField()
    expire_date = models.DateField()
    # add choices from frontend
    type_of = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




    def __str__(self) -> str:
        return self.name

class PrescriptionMedicine(models.Model):
    prescription = models.ForeignKey(Perscription, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  
    instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('prescription', 'medicine')  

    def __str__(self) -> str:
        return f"{self.prescription.name} - {self.medicine.name} (Qty: {self.quantity})"

