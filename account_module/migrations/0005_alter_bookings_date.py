# Generated by Django 5.1.7 on 2025-03-13 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account_module', '0004_alter_doctor_available_slots'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookings',
            name='date',
            field=models.DateField(),
        ),
    ]
