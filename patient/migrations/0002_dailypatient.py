# Generated by Django 5.1.1 on 2024-10-09 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyPatient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('payment', models.IntegerField()),
                ('day', models.DateField(auto_now_add=True)),
                ('note', models.TextField(blank=True, null=True)),
            ],
        ),
    ]