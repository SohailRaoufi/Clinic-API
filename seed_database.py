import os

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # Replace 'core.settings' with your project's settings module

import django
django.setup()  # Initialize Django before importing models

import random
from django.utils import timezone
from datetime import timedelta
from patient.models import Patient, PatientLogs, Treatment, Payment, Appointment, DailyPatient,TREATMENT_CHOICES

# Seed data
def seed_database():
    print("Seeding database...")

    # Create 40 Patients if they don't already exist
    for i in range(1, 41):
        # Check if patient already exists to avoid duplicates
        phone_no = f"07{random.randint(10000000, 99999999)}"
        patient, created = Patient.objects.get_or_create(
            phone_no=phone_no,
            defaults={
                'name': f"PatientName{i}",
                'last_name': f"LastName{i}",
                'addr': f"Address {i}",
                'job': f"Job {i}",
                'age': random.randint(18, 80),
                'gender': random.choice(['male', 'female']),
                'martial_status': random.choice(['married', 'single']),
                'hiv': random.choice([True, False]),
                'hcv': random.choice([True, False]),
                'hbs': random.choice([True, False]),
                'pregnancy': False if i % 2 == 0 else True,
                'diabetes': random.choice([True, False]),
                'reflux_esophagitis': random.choice([True, False]),
                'archive': random.choice([True, False]),
                'notes': f"Notes for Patient {i}"
            }
        )

        if created:
            print(f"Created Patient {patient.name} {patient.last_name}")

            # Create 1-3 Treatment records for each new patient
            for _ in range(random.randint(1, 3)):
                treatment_type = random.choice([choice[0] for choice in TREATMENT_CHOICES])
                treatment = Treatment.objects.create(
                    patient=patient,
                    type_of_treatment=treatment_type,
                    teeths=f"{random.randint(1, 32)}",
                    amount=random.randint(100, 500)
                )

                # Create 1-2 Payment records for each treatment
                for _ in range(random.randint(1, 2)):
                    Payment.objects.create(
                        treatment=treatment,
                        amount=random.randint(50, treatment.amount)
                    )

            # Create 1-2 PatientLogs for each new patient
            for _ in range(random.randint(1, 2)):
                PatientLogs.objects.create(
                    msg=f"Log message for Patient {i}",
                    patient=patient
                )

            # Create 1 Appointment record for each new patient
            Appointment.objects.create(
                day=timezone.now().date() + timedelta(days=random.randint(1, 30)),
                time=(timezone.now() + timedelta(minutes=random.randint(0, 1440))).time(),
                patient=f"{patient.name} {patient.last_name}"
            )

            # Create a DailyPatient record
            DailyPatient.objects.create(
                name=f"{patient.name} {patient.last_name}",
                payment=random.randint(50, 300),
                note=f"Daily note for {patient.name}"
            )

    print("Database seeding complete!")

# Run the seed function
if __name__ == "__main__":
    seed_database()

