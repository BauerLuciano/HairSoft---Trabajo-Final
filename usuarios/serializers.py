from rest_framework import serializers
from .models import Usuario, Turno, Servicio

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellido', 'dni', 'telefono', 'correo', 'contrasena', 'rol', 'estado', 'fecha_creacion']

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'

class TurnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turno
        fields = '__all__'