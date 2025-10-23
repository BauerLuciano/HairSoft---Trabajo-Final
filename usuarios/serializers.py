# usuarios/serializers.py
from rest_framework import serializers
from .models import Usuario, Turno, Servicio, CategoriaServicio, CategoriaProducto, Permiso

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellido', 'dni', 'telefono', 'correo', 'rol', 'estado', 'fecha_creacion']

class ServicioSerializer(serializers.ModelSerializer):
    categoria = serializers.SerializerMethodField()

    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'precio', 'duracion', 'categoria']

    def get_categoria(self, obj):
        return {'id': obj.categoria.id, 'nombre': obj.categoria.nombre} if obj.categoria else None

class TurnoSerializer(serializers.ModelSerializer):
    servicios = ServicioSerializer(many=True, read_only=True)
    cliente = UsuarioSerializer(read_only=True)
    peluquero = UsuarioSerializer(read_only=True)

    class Meta:
        model = Turno
        fields = ['id', 'fecha', 'hora', 'estado', 'cliente', 'peluquero', 'servicios']


class CategoriaServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaServicio
        fields = ['id', 'nombre', 'descripcion']


class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = ['id', 'nombre', 'descripcion']

class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = '__all__'


class RolSerializer(serializers.ModelSerializer):
    permisos = PermisoSerializer(many=True, read_only=True)
    permisos_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permiso.objects.all(), many=True, write_only=True, required=False
    )

    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion', 'activo', 'permisos', 'permisos_ids']

    def create(self, validated_data):
        permisos = validated_data.pop('permisos_ids', [])
        rol = Rol.objects.create(**validated_data)
        rol.permisos.set(permisos)
        return rol

    def update(self, instance, validated_data):
        permisos = validated_data.pop('permisos_ids', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if permisos:
            instance.permisos.set(permisos)
        return instance