from rest_framework import serializers
from .models import Patient, Doctor, Bookings
from django.db import transaction
from django.core.validators import RegexValidator


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['email', 'password']

class DoctorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Doctor
        fields = ['name', 'speciality', 'available_slots']

class BookingsSerializer(serializers.ModelSerializer):
    time_slot = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^([0-1][0-9]|2[0-3]):[0-5][0-9]-([0-1][0-9]|2[0-3]):[0-5][0-9]$',
                message='Time slot must be in "HH:MM-HH:MM" format (24-hour)'
            )
        ]
    )

    class Meta:
        model = Bookings
        fields = ['id', 'patient', 'doctor', 'date', 'time_slot']
        read_only_fields = ['patient']

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            doctor = validated_data['doctor']
            date_str = validated_data['date'].strftime("%Y-%m-%d")
            time_slot = validated_data['time_slot']

            doctor = Doctor.objects.select_for_update().get(pk=doctor.pk)
            available_slots = doctor.available_slots.copy()

            slot_entry = next(
                (entry for entry in available_slots if entry['date'] == date_str),
                None
            )

            if not slot_entry:
                raise serializers.ValidationError("No available slots for this date")

            if time_slot not in slot_entry['slots']:
                raise serializers.ValidationError("Time slot not available")

            slot_entry['slots'].remove(time_slot)

            if not slot_entry['slots']:
                available_slots = [
                    entry for entry in available_slots
                    if entry['date'] != date_str
                ]

            doctor.available_slots = available_slots
            doctor.save()

            booking = Bookings.objects.create(**validated_data)
            return booking
