import jwt
import datetime
from rest_framework import status, generics
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Patient, Doctor, Bookings
from .serializer import PatientSerializer, DoctorSerializer, BookingsSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
import requests
from django.conf import settings

# def generate_jwt_token(user):
#     payload = {
#         'email': user.email,
#     }
#     token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
#     return token

# def decode_jwt_token(token):
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
#         return payload
#     except jwt.ExpiredSignatureError:
#         return None 
#     except jwt.InvalidTokenError:
#         return None

class SignUpView(APIView):
    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            email = request.data.get("email")
            password = request.data.get("password")
            if Patient.objects.filter(email=email).exists():
                return Response({
                    "error": "Email is already registered."
                })
            serializer.save(email=email, password=password)
            return Response({
                "message": "User signed up successfully."
            })
        return Response({
            "error": "Invalid email or password."
        })


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = Patient.objects.get(email=email, password=password)
        if user:
            return Response({
                'message': 'Login successful.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)
        

class DoctorProfileAPIView(APIView):
    def get(self, request):
        doctors = Doctor.objects.all()
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = DoctorSerializer(data=request.data)
        if serializer.is_valid():
            name = request.data.get("name")
            speciality = request.data.get("speciality")
            doctor_id = request.data.get("id")
            available_slots = request.data.get("available_slots")
            if Doctor.objects.filter(name=name, speciality=speciality).exists():
                return Response({
                    "error": "This doctor is already registered."
                })
            serializer.save(name=name, speciality=speciality, available_slots=available_slots)
            return Response({
                "success": True,
                "message": "Doctor signed up successfully.",
                "doctor_id": doctor_id
            })
        return Response({
            "success": False,
            "error": "Invalid user ID or missing data."
        })


# class AppointmentBookingView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = BookingsSerializer(data=request.data, context={'request': request})
#         if not serializer.is_valid():
#             return Response({
#                 "success": False,
#                 "message": "Invalid request data."
#             }, status=status.HTTP_400_BAD_REQUEST)

#         doctor_id = serializer.validated_data['doctor'].id
#         date = serializer.validated_data['date']
#         time_slot = serializer.validated_data['time_slot']

#         try:
#             doctor = Doctor.objects.select_for_update().get(id=doctor_id)
#             available_slots = doctor.available_slots.get(date, [])
#             if time_slot not in available_slots:
#                 return Response({
#                     "success": False,
#                     "message": "Mentor is not available at the selected time."
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             if Bookings.objects.filter(doctor=doctor, date=date, 
#                                     time_slot=time_slot, status='confirmed').exists():
#                 return Response({
#                     "success": False,
#                     "message": "The requested time slot is not available."
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             booking = Bookings.objects.create(
#                 user=request.user,
#                 doctor=doctor,
#                 date=date,
#                 time_slot=time_slot,
#                 status='confirmed'
#             )

#         except Doctor.DoesNotExist:
#             return Response({
#                 "success": False,
#                 "message": "Doctor not found."
#             }, status=status.HTTP_404_NOT_FOUND)
        
#         new_doctor = Doctor.objects.get(id=doctor_id)
#         new_doctor.available_slots['slots'] = None
#         new_doctor.save()

#         return Response({
#             "success": True,
#             "message": "Booking confirmed!",
#             "booking": {
#                 "mentor_id": doctor.id,
#                 "date": date,
#                 "time_slot": time_slot,
#                 "status": "confirmed"
#             }
#         }, status=status.HTTP_201_CREATED)
    
#     def get(self, request):
#         book = Bookings.objects.all()
#         serializer = BookingsSerializer(book, many=True)
#         return Response(serializer.data)

    # def send_confirmation_sms(self, booking, user):
    #     doctor_name = booking.doctor.name
    #     user_name = user.get_full_name() or user.username
    #     message = f"Dear {user_name}, your appointment with {doctor_name} is confirmed for {booking.date} at {booking.time_slot}. Thank you!"
        
    #     url = "https://sms.ir/api/v1/send/verify"
    #     headers = {
    #         "X-API-KEY": settings.SMS_IR_API_KEY,
    #         "ACCEPT": "application/json",
    #         "Content-Type": "application/json"
    #     }
    #     data = {
    #         "mobile": user.phone_number,
    #         "templateId": 100000,
    #         "parameters": [
    #             {"name": "NAME", "value": user_name},
    #             {"name": "DATE", "value": booking.date},
    #             {"name": "TIME", "value": booking.time_slot}
    #         ]
    #     }
    #     response = requests.post(url, json=data, headers=headers)
    #     response.raise_for_status()

class AppointmentBookingView(generics.CreateAPIView):
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer

    def perform_create(self, serializer):
        # Automatically set the patient to the current user
        patient = Patient.objects.get(id=1)
        serializer.save(patient=patient)