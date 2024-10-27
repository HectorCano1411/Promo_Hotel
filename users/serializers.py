from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import CustomUser
import uuid

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        # Creación de usuario desactivado hasta que se verifique el correo
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            verification_token=uuid.uuid4(),
            is_active=False  # Usuario no activo hasta verificar el correo
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# Esta vista permitirá que los administradores inicien sesión.
class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Credenciales incorrectas.")
        if not user.is_superuser:
            raise serializers.ValidationError("No tienes permisos de administrador.")
        return {'user': user}
