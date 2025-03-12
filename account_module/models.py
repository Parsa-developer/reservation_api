from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class User(models.Model):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]
    email = models.EmailField(max_length=255, unique=True)
    hashed_password = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True 

    def __str__(self):
        return self.email
    
    def set_password(self, password):
        self.hashed_password = make_password(password)

    def check_password(self, password):
        return check_password(password, self.hashed_password)

 
class Patient(User):  
    class Meta:
        db_table = 'patients'

class Doctor(User): 
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    available_slots = models.JSONField(default=list)  

    class Meta:
        db_table = 'doctors'
    
    def __str__(self):
        return f"{self.name} ({self.specialty})"
    
class Bookings(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
        
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    booked_slot = models.JSONField(default=list)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookings'
    
    def __str__(self):
        return f"Booking {self.patient.id} - {self.patient.email} with Dr. {self.doctor.name}"