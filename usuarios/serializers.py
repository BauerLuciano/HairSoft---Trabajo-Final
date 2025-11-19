# usuarios/serializers.py
from rest_framework import serializers, viewsets
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import *

# ----------------------------------------------------------------------
# SERIALIZADOR DE LOGIN
# ----------------------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        error_messages={'required': 'El email o nombre de usuario es obligatorio.'}
    )
    password = serializers.CharField(
        style={'input_type': 'password'}, 
        write_only=True,
        required=True,
        error_messages={'required': 'La contraseña es obligatoria.'}
    )
    
    def validate(self, data):
        return data

# ----------------------------------------------------------------------
# USUARIO
# ----------------------------------------------------------------------
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellido', 'dni', 'telefono', 'correo', 'rol', 'estado', 'fecha_creacion']

# ----------------------------------------------------------------------
# SERVICIO Y CATEGORIAS
# ----------------------------------------------------------------------
class ServicioSerializer(serializers.ModelSerializer):
    categoria = serializers.SerializerMethodField()

    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'precio', 'duracion', 'categoria']

    def get_categoria(self, obj):
        return {'id': obj.categoria.id, 'nombre': obj.categoria.nombre} if obj.categoria else None

class CategoriaServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaServicio
        fields = ['id', 'nombre', 'descripcion']

# ----------------------------------------------------------------------
# TURNO
# ----------------------------------------------------------------------
class TurnoSerializer(serializers.ModelSerializer):
    servicios = ServicioSerializer(many=True, read_only=True)
    cliente = UsuarioSerializer(read_only=True)
    peluquero = UsuarioSerializer(read_only=True)

    class Meta:
        model = Turno
        fields = ['id', 'fecha', 'hora', 'estado', 'cliente', 'peluquero', 'servicios']

# ----------------------------------------------------------------------
# CATEGORIAS DE PRODUCTOS
# ----------------------------------------------------------------------
class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = ['id', 'nombre', 'descripcion']

# ----------------------------------------------------------------------
# PERMISOS Y ROLES
# ----------------------------------------------------------------------
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
        permisos = validated_data.pop('permisos_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if permisos is not None:
            instance.permisos.set(permisos)
        return instance

# ----------------------------------------------------------------------
# PROVEEDOR
# ----------------------------------------------------------------------
class ProveedorSerializer(serializers.ModelSerializer):
    categorias_nombres = serializers.StringRelatedField(many=True, source='categorias', read_only=True)
    categorias = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CategoriaProducto.objects.all(),
        required=False
    )
    productos = serializers.SerializerMethodField()

    class Meta:
        model = Proveedor
        fields = [
            'id', 'nombre', 'cuit', 'contacto', 'telefono', 'email',
            'direccion', 'productos_que_ofrece', 'estado',
            'fecha_creacion', 
            'categorias_nombres', 'categorias',
            'productos_especificos',
            'productos'
        ]
        read_only_fields = ['fecha_creacion', 'categorias_nombres', 'productos']

    def get_productos(self, obj):
        return list(obj.producto_set.values_list('nombre', flat=True))

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

# ----------------------------------------------------------------------
# PRODUCTO
# ----------------------------------------------------------------------
class ProductoSerializer(serializers.ModelSerializer):
    categoria_id = serializers.IntegerField(source='categoria.id', read_only=True) 
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    # ✅ CORREGIR: Hacer stock readable y writeable
    stock_actual = serializers.IntegerField(read_only=True)  # Para lectura
    stock = serializers.IntegerField(source='stock_actual', required=False, write_only=True)  # Para escritura
    
    # ✅ CORRECCIÓN: Hacer proveedores writeable
    proveedores = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Proveedor.objects.all(),
        required=False,
        allow_empty=True
    )
    
    proveedores_nombres = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 
            'nombre', 
            'precio', 
            'codigo',
            'descripcion',
            'stock_actual',  # ✅ AGREGAR para lectura
            'stock',         # ✅ Mantener para escritura
            'categoria_id',         
            'categoria_nombre',
            'proveedores',
            'proveedores_nombres',
        ]
        extra_kwargs = {
            'nombre': {'required': True},
            'precio': {'required': True},
            'categoria': {'required': True},
        }

    def get_proveedores_nombres(self, obj):
        return [proveedor.nombre for proveedor in obj.proveedores.all()]
# ----------------------------------------------------------------------
# DETALLEVENTA Y VENTA
# ----------------------------------------------------------------------
class DetalleVentaSerializer(serializers.ModelSerializer):
    producto = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(), 
        required=False, 
        allow_null=True
    )
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    servicio_nombre = serializers.CharField(source='servicio.nombre', read_only=True)
    servicio = serializers.PrimaryKeyRelatedField(queryset=Servicio.objects.all(), required=False, allow_null=True)
    turno = serializers.PrimaryKeyRelatedField(queryset=Turno.objects.all(), required=False, allow_null=True)

    class Meta:
        model = DetalleVenta
        fields = [
            'id', 'venta', 'producto', 'producto_nombre',
            'servicio', 'servicio_nombre', 'turno',
            'cantidad', 'precio_unitario', 'subtotal'
        ]
        read_only_fields = ['venta']

class VentaSerializer(serializers.ModelSerializer):
    cliente = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        required=False,     
        allow_null=True     
    ) 
    detalles = DetalleVentaSerializer(many=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)

    usuario = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        required=True
    )
    
    medio_pago = serializers.PrimaryKeyRelatedField(
        queryset=MetodoPago.objects.filter(activo=True),
        required=True
    )
    medio_pago_nombre = serializers.CharField(source='medio_pago.nombre', read_only=True)
    
    medio_pago_tipo = serializers.SerializerMethodField()

    class Meta:
        model = Venta
        fields = [
            'id', 'cliente', 'cliente_nombre',
            'usuario', 'usuario_nombre',
            'fecha', 'total', 'anulada', 'tipo', 
            'medio_pago', 'medio_pago_nombre', 'medio_pago_tipo',
            'detalles'
        ]

    def get_medio_pago_tipo(self, obj):
        if obj.medio_pago:
            return obj.medio_pago.tipo
        return 'SIN_METODO'

    @transaction.atomic
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        
        # Validación de stock
        for detalle in detalles_data:
            producto = detalle.get('producto')
            if producto:
                if producto.stock_actual < detalle['cantidad']:
                    raise serializers.ValidationError({
                        'detalles': f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock_actual}, Solicitado: {detalle['cantidad']}."
                    })
        
        # Crear venta
        venta = Venta.objects.create(**validated_data)

        # Crear detalles
        for detalle in detalles_data:
            producto = detalle.get('producto')
            servicio = detalle.get('servicio')
            turno = detalle.get('turno')
            
            subtotal = detalle.get('subtotal', detalle['cantidad'] * detalle['precio_unitario'])
            
            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                servicio=servicio,
                turno=turno,
                cantidad=detalle['cantidad'],
                precio_unitario=detalle['precio_unitario'],
                subtotal=subtotal
            )

            if producto:
                producto.stock_actual -= detalle['cantidad']
                producto.save()

        # Recalcular total desde los detalles
        from django.db.models import Sum
        venta.total = venta.detalles.aggregate(total=Sum('subtotal'))['total'] or 0
        venta.save()

        return venta

class VentaUpdateSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True)
    
    class Meta:
        model = Venta
        fields = [
            'id', 'cliente', 'usuario', 'total', 'anulada', 'tipo', 
            'medio_pago', 'detalles'
        ]
        read_only_fields = ('fecha', 'usuario')

    @transaction.atomic
    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        
        # Actualizar campos principales
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Restaurar stock de los detalles antiguos
        for detalle_antiguo in instance.detalles.all():
            if detalle_antiguo.producto:
                detalle_antiguo.producto.stock_actual += detalle_antiguo.cantidad
                detalle_antiguo.producto.save()
        
        # Eliminar detalles antiguos
        instance.detalles.all().delete()
        
        # Crear nuevos detalles y validar stock
        for detalle_data in detalles_data:
            producto = detalle_data.get('producto')
            if producto:
                if producto.stock_actual < detalle_data['cantidad']:
                    raise serializers.ValidationError({
                        'detalles': f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock_actual}, Solicitado: {detalle_data['cantidad']}."
                    })
        
        # Crear nuevos detalles
        for detalle_data in detalles_data:
            producto = detalle_data.get('producto')
            servicio = detalle_data.get('servicio')
            turno = detalle_data.get('turno')
            
            subtotal = detalle_data.get('subtotal', detalle_data['cantidad'] * detalle_data['precio_unitario'])
            
            DetalleVenta.objects.create(
                venta=instance,
                producto=producto,
                servicio=servicio,
                turno=turno,
                cantidad=detalle_data['cantidad'],
                precio_unitario=detalle_data['precio_unitario'],
                subtotal=subtotal
            )

            if producto:
                producto.stock_actual -= detalle_data['cantidad']
                producto.save()

        # Recalcular total
        from django.db.models import Sum
        instance.total = instance.detalles.aggregate(total=Sum('subtotal'))['total'] or 0
        instance.save()

        return instance

# ----------------------------------------------------------------------
# MÉTODO DE PAGO (NUEVO)
# ----------------------------------------------------------------------
class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = ['id', 'nombre', 'descripcion', 'tipo', 'requiere_confirmacion']


# ----------------------------------------------------------------------
# PEDIDOS
# ----------------------------------------------------------------------
class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_codigo = serializers.CharField(source='producto.codigo', read_only=True)
    producto_stock_actual = serializers.IntegerField(source='producto.stock_actual', read_only=True)
    porcentaje_recibido = serializers.SerializerMethodField()

    class Meta:
        model = DetallePedido
        fields = [
            'id',
            'producto',
            'producto_nombre',
            'producto_codigo',
            'producto_stock_actual',
            'cantidad',
            'cantidad_recibida',
            'precio_propuesto',      
            'precio_unitario',       
            'subtotal',
            'porcentaje_recibido'
        ]
        read_only_fields = ['subtotal']

    def get_porcentaje_recibido(self, obj):
        return obj.porcentaje_recibido()



class PedidoSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)
    proveedor_contacto = serializers.CharField(source='proveedor.contacto', read_only=True)
    usuario_creador_nombre = serializers.CharField(source='usuario_creador.nombre', read_only=True)
    detalles = DetallePedidoSerializer(many=True, required=False)

    # Campos calculados
    total_calculado = serializers.SerializerMethodField()
    puede_cancelar = serializers.SerializerMethodField()
    puede_completar = serializers.SerializerMethodField()  # ✅ CAMBIÉ EL NOMBRE
    cantidad_productos = serializers.SerializerMethodField()
    tiene_precios_pendientes = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = [
            'id',
            'proveedor',
            'proveedor_nombre',
            'proveedor_contacto',
            'fecha_pedido',
            'fecha_esperada_recepcion',
            'fecha_recepcion',
            'estado',
            'observaciones',
            'total',
            'usuario_creador',
            'usuario_creador_nombre',
            'fecha_creacion',
            'fecha_modificacion',
            'detalles',
            'total_calculado',
            'puede_cancelar',
            'puede_completar',  # ✅ CAMBIÉ EL NOMBRE
            'cantidad_productos',
            'tiene_precios_pendientes'
        ]
        read_only_fields = [
            'fecha_pedido',
            'fecha_creacion',
            'fecha_modificacion',
            'usuario_creador',
            'total',
            'total_calculado'
        ]

    def get_total_calculado(self, obj):
        return obj.calcular_total()

    def get_puede_cancelar(self, obj):
        return obj.puede_ser_cancelado()

    def get_puede_completar(self, obj):  # ✅ CAMBIÉ EL NOMBRE Y MÉTODO
        return obj.puede_ser_completado()

    def get_cantidad_productos(self, obj):
        return obj.detalles.count()

    def get_tiene_precios_pendientes(self, obj):
        """Verifica si hay productos sin precio confirmado"""
        return obj.detalles.filter(precio_unitario__isnull=True).exists()

    @transaction.atomic
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])

        # Asignar usuario creador por defecto
        if 'usuario_creador' not in validated_data or not validated_data['usuario_creador']:
            usuario_default = Usuario.objects.filter(estado='ACTIVO').first()
            if not usuario_default:
                from django.contrib.auth.hashers import make_password
                rol_admin = Rol.objects.filter(nombre__iexact='administrador').first()
                if not rol_admin:
                    rol_admin = Rol.objects.create(nombre='Administrador', descripcion='Rol temporal')

                usuario_default = Usuario.objects.create(
                    nombre='Admin',
                    apellido='Temporal',
                    dni='99999999',
                    correo='admin@temp.com',
                    contrasena=make_password('temp123'),
                    rol=rol_admin,
                    estado='ACTIVO'
                )
            validated_data['usuario_creador'] = usuario_default

        # Validar que haya productos
        if not detalles_data:
            raise serializers.ValidationError({'detalles': 'El pedido debe tener al menos un producto.'})

        # Crear pedido
        pedido = Pedido.objects.create(**validated_data)

        # Crear detalles del pedido
        for detalle_data in detalles_data:
            DetallePedido.objects.create(pedido=pedido, **detalle_data)

        # Actualizar total del pedido
        pedido.total = pedido.calcular_total()
        pedido.save()

        return pedido


class PedidoRecepcionSerializer(serializers.ModelSerializer):
    """Serializer específico para recepción de pedidos"""
    detalles_recepcion = DetallePedidoSerializer(many=True, source='detalles')

    class Meta:
        model = Pedido
        fields = ['id', 'estado', 'detalles_recepcion']
        read_only_fields = ['estado']

    @transaction.atomic
    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        
        # Actualizar cantidades recibidas
        for detalle_data in detalles_data:
            detalle_id = detalle_data.get('id')
            cantidad_recibida = detalle_data.get('cantidad_recibida', 0)
            
            try:
                detalle = DetallePedido.objects.get(id=detalle_id, pedido=instance)
                detalle.cantidad_recibida = cantidad_recibida
                detalle.save()
                
            except DetallePedido.DoesNotExist:
                raise serializers.ValidationError({
                    'detalles': f'Detalle de pedido con ID {detalle_id} no encontrado.'
                })
        
        # Procesar recepción del pedido
        instance.completar_pedido()  # ✅ CAMBIÉ POR EL NUEVO MÉTODO
        
        return instance


class PedidoBusquedaSerializer(serializers.ModelSerializer):
    """Serializer para búsqueda de pedidos - VERSIÓN CORREGIDA"""
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)
    proveedor_contacto = serializers.CharField(source='proveedor.contacto', read_only=True)
    usuario_creador_nombre = serializers.CharField(source='usuario_creador.nombre', read_only=True)
    cantidad_productos = serializers.SerializerMethodField()
    total_calculado = serializers.SerializerMethodField()
    puede_cancelar = serializers.SerializerMethodField()
    puede_completar = serializers.SerializerMethodField()  # ✅ CAMBIÉ EL NOMBRE
    
    # Incluir los detalles del pedido
    detalles = DetallePedidoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'proveedor_nombre', 'proveedor_contacto', 'fecha_pedido', 'estado', 
            'total', 'usuario_creador_nombre', 'cantidad_productos', 'total_calculado',
            'puede_cancelar', 'puede_completar', 'observaciones', 'detalles'  # ✅ CAMBIÉ EL NOMBRE
        ]

    def get_cantidad_productos(self, obj):
        return obj.detalles.count()

    def get_total_calculado(self, obj):
        return obj.calcular_total()

    def get_puede_cancelar(self, obj):
        return obj.puede_ser_cancelado()

    def get_puede_completar(self, obj):  # ✅ CAMBIÉ EL NOMBRE Y MÉTODO
        return obj.puede_ser_completado()
# ----------------------------------------------------------------------
# LISTAS DE PRECIOS DE PROVEEDORES
# ----------------------------------------------------------------------
class ListaPrecioProveedorSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_codigo = serializers.CharField(source='producto.codigo', read_only=True)
    precio_sugerido_venta = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = ListaPrecioProveedor
        fields = '__all__'
    

class HistorialPreciosSerializer(serializers.ModelSerializer):
    lista_precio_info = serializers.CharField(source='lista_precio.__str__', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)

    class Meta:
        model = HistorialPrecios
        fields = [
            'id', 'lista_precio', 'lista_precio_info', 'precio_anterior', 'precio_nuevo',
            'margen_anterior', 'margen_nuevo', 'usuario', 'usuario_nombre', 
            'fecha_cambio', 'motivo'
        ]
        read_only_fields = ['fecha_cambio']


class PrecioSugeridoSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    proveedor_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)


class ActualizarListaPreciosSerializer(serializers.Serializer):
    proveedor_id = serializers.IntegerField()
    precios = serializers.ListField(
        child=serializers.DictField()
    )