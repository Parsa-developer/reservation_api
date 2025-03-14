from django.db import models

 
class Patient(models.Model):  
    phone_number = models.CharField(max_length=12)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)


class Doctor(models.Model): 
    name = models.CharField(max_length=100)
    speciality = models.CharField(max_length=100)
    available_slots = models.JSONField(default=list, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.speciality})"
    
class Bookings(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Booking {self.patient.id} - {self.patient.email} with Dr. {self.doctor.name}"