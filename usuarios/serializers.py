# usuarios/serializers.py
from rest_framework import serializers
from .models import Usuario, Turno, Servicio, CategoriaServicio, CategoriaProducto, Permiso, Rol, Proveedor
# ----------------------------------------------------------------------
# SERIALIZADOR DE LOGIN (Añadir esta nueva clase)
# ----------------------------------------------------------------------

class LoginSerializer(serializers.Serializer):
    """
    Serializador para validar las credenciales de inicio de sesión (username y password).
    """
    username = serializers.CharField(
        required=True,
        error_messages={'required': 'El email o nombre de usuario es obligatorio.'}
    )
    password = serializers.CharField(
        style={'input_type': 'password'}, 
        write_only=True, # No se muestra en la respuesta de la API
        required=True,
        error_messages={'required': 'La contraseña es obligatoria.'}
    )
    
    def validate(self, data):
        # Opcional: Puedes añadir validaciones aquí si es necesario
        return data

# ----------------------------------------------------------------------

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

class ProveedorSerializer(serializers.ModelSerializer):

    categorias_nombres = serializers.StringRelatedField(many=True, source='categorias', read_only=True)
    categorias = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CategoriaProducto.objects.all(), # Aseguramos que solo se acepten IDs válidos
        required=False
    )
    
    class Meta:
        model = Proveedor
        fields = [
            'id', 'nombre', 'contacto', 'telefono', 'email', 
            'direccion', 'productos_que_ofrece', 'estado',
            'fecha_creacion', 
            'categorias_nombres',  # Campo para mostrar los nombres
            'categorias',          # Campo para recibir/mostrar los IDs
            'productos_especificos'
        ]
        # Aseguramos que 'categorias_nombres' sea solo de lectura.
        read_only_fields = ['fecha_creacion', 'categorias_nombres']
    
    # Los métodos create y update se mantienen porque manejan correctamente el campo 'categorias' (los IDs).
    def create(self, validated_data):
        categorias_data = validated_data.pop('categorias', [])
        proveedor = Proveedor.objects.create(**validated_data)
        proveedor.categorias.set(categorias_data)
        return proveedor
    
    def update(self, instance, validated_data):
        categorias_data = validated_data.pop('categorias', None)
        instance = super().update(instance, validated_data)
        if categorias_data is not None:
            instance.categorias.set(categorias_data)
        return instance