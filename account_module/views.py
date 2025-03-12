import jwt
import datetime
from rest_framework import status
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Patient, Doctor, Bookings, User
from .serializer import PatientSerializer, DoctorSerializer

def generate_jwt_token(user):
    payload = {
        'email': user.email,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

class SignUpView(APIView):
    def post(self, request):
        role = request.data.get('role')
        
        if role == 'patient':
            serializer = PatientSerializer(data=request.data)
        elif role == 'doctor':
            serializer = DoctorSerializer(data=request.data)
        else:
            return Response({'error': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'{role.capitalize()} signed up successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.get(email=email, password=password)
        if user:
            refresh = generate_jwt_token(user)
            return Response({
                'message': 'Login successful.',
                'access_token': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)
        

class DoctorProfileAPIView(APIView):
    def post(self, request):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return Response({'success': False, 'message': 'Authorization header missing'}, status=status.HTTP_401_UNAUTHORIZED)

            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            email = payload.get('email')  
            user = User.objects.filter(email=email).first()  

            if not user:
                return Response({'success': False, 'message': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

            user_id = user.id

        except jwt.ExpiredSignatureError:
            return Response({'success': False, 'message': 'Token has expired.'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'success': False, 'message': 'Invalid token.'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        serializer = DoctorSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user_id=user_id)
            return Response({
                'success': True,
                'message': 'Doctor profile created successfully.',
                'doctor_id': serializer.data['id']
            }, status=status.HTTP_201_CREATED)
        
        return Response({'success': False, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
