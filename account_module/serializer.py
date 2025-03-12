from rest_framework import serializers
from .models import Patient, Doctor, Bookings 


class PatientSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Patient
        fields = ['id', 'email', 'password']
        
    def create(self, validated_data):
        patient = Patient(email=validated_data['email'], role='patient')
        patient.set_password(validated_data['password'])
        patient.save()
        return patient

class DoctorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'email', 'password', 'name', 'specialty', 'available_slots']  
            
    def create(self, validated_data):
        doctor = Doctor(
            email=validated_data['email'],
            role='doctor',
            name=validated_data['name'],
            specialty=validated_data['specialty']
        )
        
        doctor.set_password(validated_data['password'])
        doctor.save()
        return doctor
        

class BookingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = ['id', 'patient', 'doctor', 'booked_slot', 'status']