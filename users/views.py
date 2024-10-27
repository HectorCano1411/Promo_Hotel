from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.core.mail import send_mail
from .serializers import CustomUserSerializer, AdminLoginSerializer
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from .tasks import send_verification_email  # Asegúrate de tener configurada la tarea de Celery
from django.views.generic import TemplateView
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token  
import random
import logging


logger = logging.getLogger(__name__)



class HomeView(TemplateView):
    template_name = 'home.html'  # Asegúrate de tener un archivo home.html




class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generar el enlace de verificación
            verification_link = f"{settings.FRONTEND_URL}{reverse('verify_email', kwargs={'token': user.verification_token})}"

            # Envía el correo de verificación utilizando Celery
            subject = 'Verificación de correo electrónico'
            message_text = f'Hola, por favor verifica tu correo haciendo clic en el siguiente enlace: {verification_link}'
            email_result = send_verification_email.delay(subject, message_text, user.email, user.verification_token)

            # Manejar posibles errores en el envío del correo
            if isinstance(email_result, dict) and 'error' in email_result:
                return Response({'message': 'Usuario registrado, pero hubo un error al enviar el correo de verificación.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Usuario registrado. Por favor verifica tu correo.',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class EmailAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("Datos recibidos en request.data: %s", request.data)  # Depuración
        try:
            email = request.data.get("email")
            name = request.data.get("name")  # Obtener el nombre de la solicitud

            user = CustomUser.objects.get(email=email)  # Asegúrate de que el usuario exista
            
            # Puedes usar el nombre en el mensaje del correo
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_link = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"  # Cambia esto según tu ruta

            subject = "Verifica tu correo"
            message = f"Hola {name}, por favor verifica tu correo haciendo clic en el siguiente enlace: {activation_link}"

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
            logger.info("Correo de verificación enviado a: %s", email)  # Registro de éxito
            return Response({"message": "Correo de verificación enviado."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            logger.error("El usuario con el correo %s no existe.", email)  # Mensaje de error específico
            return Response({"message": "El usuario no existe."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Error en el envío de correo: %s", e)  # Depuración de error específico
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            user = CustomUser.objects.get(verification_token=token)
            user.is_active = True
            user.verification_token = None  # Limpiar el token después de la verificación
            user.save()
            return Response({'message': 'Correo verificado con éxito.'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'message': 'Token inválido.'}, status=status.HTTP_400_BAD_REQUEST)


class SetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.is_active:
            return Response({'error': 'Debes verificar tu correo electrónico antes de establecer la contraseña.'}, status=status.HTTP_400_BAD_REQUEST)

        password = request.data.get('password')
        if password:
            user.set_password(password)
            user.is_verified = True  # Asumiendo que quieres marcar al usuario como verificado aquí
            user.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Contraseña establecida exitosamente.',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'La contraseña es obligatoria.'}, status=status.HTTP_400_BAD_REQUEST)


class AdminLoginView(APIView):
    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({'message': 'Inicio de sesión exitoso. Bienvenido al panel de administración.'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_superuser:
            return Response({'message': 'Bienvenido al panel de administración.'}, status=status.HTTP_200_OK)
        return Response({'message': 'Acceso denegado. No tienes permisos de administrador.'}, status=status.HTTP_403_FORBIDDEN)


class GenerateWinnerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_superuser:
            eligible_users = CustomUser.objects.filter(is_active=True)

            if eligible_users.exists():
                winner = random.choice(eligible_users)

                # Envío del correo al ganador usando Celery
                email_result = send_verification_email.delay("¡Felicidades! Has ganado el sorteo.", "¡Felicidades! Has ganado el sorteo.", winner.email)

                # Manejar posibles errores en el envío del correo
                if isinstance(email_result, dict) and 'error' in email_result:
                    return Response({'message': 'Ganador generado, pero hubo un error al enviar el correo al ganador.'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                return Response({'message': f'Ganador generado: {winner.email}'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'No hay usuarios elegibles para el sorteo.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'Acceso denegado.'}, status=status.HTTP_403_FORBIDDEN)

