# usuarios/serializers.py
from rest_framework import serializers, viewsets
from django.db import transaction
from decimal import Decimal
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
    # Para MOSTRAR el nombre (Lectura)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    # Para GUARDAR el ID (Escritura) - Esto arregla el error al editar categorías
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaServicio.objects.all(),
        required=False,
        allow_null=True
    )
    
    # ✅ CORREGIDO: Se quitó read_only=True. Ahora permite guardar el dato.
    porcentaje_comision = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        required=False
    )
    
    # Para que el switch de activo/inactivo funcione bien
    activo = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = Servicio
        fields = [
            'id', 'nombre', 'precio', 'duracion', 
            'categoria', 'categoria_nombre', 
            'porcentaje_comision', 'activo', 'descripcion'
        ]

class CategoriaServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaServicio
        fields = ['id', 'nombre', 'descripcion']


class TurnoSerializer(serializers.ModelSerializer):
    cliente = UsuarioSerializer(read_only=True)
    peluquero = UsuarioSerializer(read_only=True)
    servicios = ServicioSerializer(many=True, read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_apellido = serializers.CharField(source='cliente.apellido', read_only=True)
    peluquero_nombre = serializers.CharField(source='peluquero.nombre', read_only=True)
    
    # 🔥 NUEVO: Campo para recibir el ID de la silla al crear/editar
    silla_id = serializers.PrimaryKeyRelatedField(
        source='silla',                # se asigna al campo 'silla' del modelo
        queryset=Silla.objects.all(),
        allow_null=True,
        required=False
    )
    silla_nombre = serializers.CharField(source='silla.nombre', read_only=True, allow_null=True)

    precio_total = serializers.SerializerMethodField()
    info_descuento = serializers.SerializerMethodField()

    class Meta:
        model = Turno
        fields = [
            'id', 'fecha', 'hora', 'estado', 'canal', 'tipo_pago', 'medio_pago',
            'monto_total', 'monto_seña', 'duracion_total', 'precio_total',
            'oferta_activa', 'reembolsado', 'reembolso_estado',
            'mp_payment_id', 'mp_refund_id', 'nro_transaccion', 'motivo_cancelacion',
            'obs_cancelacion', 'cliente', 'cliente_nombre', 'cliente_apellido',
            'peluquero', 'peluquero_nombre', 'servicios',
            'codigo_transaccion', 'entidad_pago', 'info_descuento',
            'silla', 'silla_nombre', 'silla_id',
            'medio_pago_restante', 'entidad_pago_restante', 'codigo_transaccion_restante'  
        ]
        extra_kwargs = {
            'silla': {'read_only': True}  # El campo original del modelo lo dejamos solo lectura
        }

    def get_precio_total(self, obj):
        if obj.monto_total and obj.monto_total > 0:
            return obj.monto_total
        return sum(s.precio for s in obj.servicios.all())

    def get_info_descuento(self, obj):
        try:
            promo = obj.promo_usada.first()
            if promo:
                return {
                    'tipo': 'FIDELIZACION',
                    'texto': 'Cliente Recuperado',
                    'porcentaje': promo.descuento_porcentaje
                }
        except Exception:
            pass
        return None
# ----------------------------------------------------------------------
# CATEGORIAS DE PRODUCTOS
# ----------------------------------------------------------------------
class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = ['id', 'nombre', 'descripcion']

# ----------------------------------------------------------------------
# CATALOGO DE PRODUCTOS
# ---------------------------------------------------------------------
class ProductoCatalogoSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True, default="Genérico")

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'marca_nombre', 'descripcion', 'precio', 'imagen', 'stock_actual']


# ----------------------------------------------------------------------
# SERIALIZER DE PERMISOS
# ----------------------------------------------------------------------
class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = '__all__'

# ----------------------------------------------------------------------
# SERIALIZER DE ROLES
# ----------------------------------------------------------------------
class RolSerializer(serializers.ModelSerializer):
    # 1. Para LEER (GET): Muestra el objeto completo del permiso
    permisos = PermisoSerializer(many=True, read_only=True)
    
    # 2. Para ESCRIBIR (POST/PUT): Recibe solo los IDs
    permisos_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permiso.objects.all(), 
        many=True, 
        write_only=True, 
        required=False
    )

    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion', 'activo', 'permisos', 'permisos_ids']

    def create(self, validated_data):
        # Sacamos los IDs de la data validada
        permisos = validated_data.pop('permisos_ids', [])
        
        # Creamos el Rol
        rol = Rol.objects.create(**validated_data)
        
        # Asignamos los permisos (Many-to-Many)
        rol.permisos.set(permisos)
        return rol

    def update(self, instance, validated_data):
        # Sacamos los IDs (si no vienen, es None)
        permisos = validated_data.pop('permisos_ids', None)
        
        # Actualizamos los campos normales (nombre, descripcion, activo)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Solo actualizamos los permisos si se enviaron en la petición
        if permisos is not None:
            instance.permisos.set(permisos)
            
        return instance

# ----------------------------------------------------------------------
# PROVEEDOR
# ----------------------------------------------------------------------
class ProveedorSerializer(serializers.ModelSerializer):
    # Lectura de nombres para el listado
    categorias_nombres = serializers.StringRelatedField(
        many=True, 
        source='categorias',
        read_only=True
    )
    
    # Manejo de IDs para los Checkboxes (Escritura y Lectura)
    categorias = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CategoriaProducto.objects.all(),
        required=False
    )

    productos = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Producto.objects.all(),
        required=False
    )

    class Meta:
        model = Proveedor
        fields = [
            'id', 'nombre', 'cuit', 'contacto', 'telefono', 'email', 'direccion', 
            'estado', 'fecha_creacion', 'categorias_nombres', 'categorias', 
            'productos'
            # 'productos_especificos' # <--- DESCOMENTÁ ESTO SOLO SI YA LO AGREGASTE AL MODELO Y MIGRÁSTE
        ]
        
        read_only_fields = [
            'fecha_creacion', 
            'categorias_nombres'
        ]

    def create(self, validated_data):
        categorias_data = validated_data.pop('categorias', [])
        productos_data = validated_data.pop('productos', [])
        proveedor = Proveedor.objects.create(**validated_data)
        proveedor.categorias.set(categorias_data)
        proveedor.productos.set(productos_data)
        return proveedor

    def update(self, instance, validated_data):
        # Extraemos las relaciones ManyToMany
        categorias_data = validated_data.pop('categorias', None)
        productos_data = validated_data.pop('productos', None)
        
        # Actualizamos campos normales
        instance = super().update(instance, validated_data)
        
        # Actualizamos relaciones
        if categorias_data is not None:
            instance.categorias.set(categorias_data)
        if productos_data is not None:
            instance.productos.set(productos_data)
            
        return instance


class ProductoSerializer(serializers.ModelSerializer):
    codigo = serializers.CharField(read_only=True)
    
    # ✅ PRECIO: Decimal
    precio = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2,
        required=True,
        min_value=Decimal('0.01')
    )
    
    # ======= CATEGORÍA =======
    categoria_id = serializers.IntegerField(source='categoria.id', read_only=True) 
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaProducto.objects.all(),
        required=True
    )

    # ======= MARCA =======
    marca_id = serializers.IntegerField(source='marca.id', read_only=True)
    marca_nombre = serializers.CharField(source='marca.nombre', read_only=True)
    marca = serializers.PrimaryKeyRelatedField(
        queryset=Marca.objects.all(),
        required=True
    )

    # ======= ESTADO =======
    estado = serializers.CharField(
        max_length=10, 
        required=False,
        default='ACTIVO'
    )

    # ======= CONFIGURACIÓN DE STOCK =======
    stock_actual = serializers.IntegerField(required=True, min_value=0)
    stock_minimo = serializers.IntegerField(required=False, default=5, min_value=0)
    lote_reposicion = serializers.IntegerField(required=False, default=1, min_value=1)

    # ======= PROVEEDORES =======
    proveedores = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Proveedor.objects.all(),
        required=False,
        allow_empty=True
    )

    proveedores_nombres = serializers.SerializerMethodField()

    # ======= IMAGEN (OPCIONAL) =======
    # Agregamos esto para que el serializer sepa manejar el archivo
    imagen = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'precio',
            'codigo',
            'descripcion',
            'estado',
            'stock_actual',
            'stock_minimo',
            'lote_reposicion',
            'categoria',
            'categoria_id',
            'categoria_nombre',
            'marca',
            'marca_id',
            'marca_nombre',
            'proveedores',
            'proveedores_nombres',
            'imagen',  # <--- 🛑 ESTO FALTABA. SI NO ESTÁ ACÁ, DJANGO LA IGNORA.
        ]
        extra_kwargs = {
            'estado': {'required': False, 'default': 'ACTIVO'}
        }

    def get_proveedores_nombres(self, obj):
        return [p.nombre for p in obj.proveedores.all()]

    def create(self, validated_data):
        proveedores_data = validated_data.pop('proveedores', [])
        producto = Producto.objects.create(**validated_data)
        if proveedores_data:
            producto.proveedores.set(proveedores_data)
        return producto
        
    def update(self, instance, validated_data):
        if 'proveedores' in validated_data:
            proveedores_data = validated_data.pop('proveedores')
            instance.proveedores.set(proveedores_data)
        return super().update(instance, validated_data)
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
    cliente_apellido = serializers.CharField(source='cliente.apellido', read_only=True) # Agregué apellido por si las dudas
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
        # 🔥 AGREGAMOS LOS CAMPOS DE TRAZABILIDAD AQUÍ 🔥
        fields = [
            'id', 'cliente', 'cliente_nombre', 'cliente_apellido',
            'usuario', 'usuario_nombre',
            'fecha', 'total', 'anulada', 'tipo', 
            'medio_pago', 'medio_pago_nombre', 'medio_pago_tipo',
            'entidad_pago',       # Nuevo
            'codigo_transaccion', # Nuevo
            'nro_transaccion',    # Viejo (por compatibilidad)
            'mp_payment_id',      # Viejo (por compatibilidad)
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
        
        # Crear venta (validated_data ya incluye entidad_pago y codigo_transaccion si vienen en el request)
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
        total_real = venta.detalles.aggregate(total=Sum('subtotal'))['total'] or 0
        venta.total = total_real
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
# usuarios/serializers.py

class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
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
        # 'producto' NO debe estar en read_only_fields para poder crear
        read_only_fields = ['subtotal', 'producto_nombre', 'producto_codigo']

    def get_porcentaje_recibido(self, obj):
        return obj.porcentaje_recibido()


class PedidoSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.ReadOnlyField(source='proveedor.nombre')
    proveedor_contacto = serializers.CharField(source='proveedor.contacto', read_only=True)
    usuario_creador_nombre = serializers.CharField(source='usuario_creador.nombre', read_only=True)
    
    # ⚠️ CORRECCIÓN CLAVE: Quitamos 'read_only=True' para que acepte datos al crear
    detalles = DetallePedidoSerializer(many=True)

    # Campos calculados
    total_calculado = serializers.SerializerMethodField()
    puede_cancelar = serializers.SerializerMethodField()
    puede_completar = serializers.SerializerMethodField()
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
            'puede_completar',
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
        # Protección contra el Error 500 si la validación falla
        if isinstance(obj, dict): return 0
        return obj.calcular_total()

    def get_puede_cancelar(self, obj):
        if isinstance(obj, dict): return False
        return obj.puede_ser_cancelado()

    def get_puede_completar(self, obj):
        if isinstance(obj, dict): return False
        return obj.puede_ser_completado()

    def get_cantidad_productos(self, obj):
        if isinstance(obj, dict): return 0
        return obj.detalles.count()

    def get_tiene_precios_pendientes(self, obj):
        if isinstance(obj, dict): return False
        return obj.detalles.filter(precio_unitario__isnull=True).exists()

    @transaction.atomic
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])

        # Validar que haya productos
        if not detalles_data:
            raise serializers.ValidationError({'detalles': 'El pedido debe tener al menos un producto.'})

        # Asignar usuario creador por defecto (Tu lógica original)
        if 'usuario_creador' not in validated_data or not validated_data['usuario_creador']:
            usuario_default = Usuario.objects.filter(estado='ACTIVO').first()
            if not usuario_default:
                # Fallback seguro para desarrollo
                pass 
            # Si ya viene en validated_data desde la view, genial.

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

class DetallePedidoWebSerializer(serializers.ModelSerializer):
    nombre_producto = serializers.ReadOnlyField(source='producto.nombre')
    
    class Meta:
        model = DetallePedidoWeb
        fields = ['id', 'producto', 'nombre_producto', 'cantidad', 'precio_unitario', 'subtotal']
        # ✅ FIX: El precio lo pone el back, no lo pide al front (Evita el Error 400)
        read_only_fields = ['precio_unitario']

class PedidoWebSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoWebSerializer(many=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    cliente_nombre = serializers.SerializerMethodField()
    cliente_email = serializers.CharField(source='cliente.correo', read_only=True)

    class Meta:
        model = PedidoWeb
        fields = [
            'id', 'cliente', 'cliente_nombre', 'cliente_email', 
            'fecha_creacion', 'estado', 'estado_display', 
            'tipo_entrega', 'direccion_envio', 'costo_envio', 
            'total', 'detalles',
            'datos_entrega_interna', # ✅ CORRECCIÓN: Ahora el dato viaja al Front
            'mp_payment_id'
        ]
        read_only_fields = ['cliente', 'fecha_creacion', 'estado', 'total', 'mp_payment_id']

    def get_cliente_nombre(self, obj):
        if obj.cliente:
            nombre = f"{obj.cliente.nombre} {obj.cliente.apellido}".strip()
            return nombre if nombre else obj.cliente.username
        return "Cliente Desconocido"

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        
        with transaction.atomic():
            pedido = PedidoWeb.objects.create(**validated_data)
            total_acumulado = 0

            for detalle_data in detalles_data:
                producto = detalle_data['producto']
                cantidad = detalle_data['cantidad']
                producto_db = Producto.objects.select_for_update().get(pk=producto.pk)

                if producto_db.stock_actual < cantidad:
                    raise serializers.ValidationError(f"Stock insuficiente para {producto_db.nombre}.")

                producto_db.stock_actual -= cantidad
                producto_db.save()

                DetallePedidoWeb.objects.create(
                    pedido=pedido,
                    producto=producto_db,
                    cantidad=cantidad,
                    precio_unitario=producto_db.precio
                )
                total_acumulado += (producto_db.precio * cantidad)

            pedido.total = total_acumulado + pedido.costo_envio
            pedido.save()
            return pedido
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

# ================================
# SERIALIZERS REOFERTA AUTOMÁTICA
# ================================

class InteresTurnoLiberadoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_correo = serializers.CharField(source='cliente.correo', read_only=True)
    servicio_nombre = serializers.CharField(source='servicio.nombre', read_only=True)
    peluquero_nombre = serializers.CharField(source='peluquero.nombre', read_only=True)
    
    class Meta:
        model = InteresTurnoLiberado
        fields = [
            'id', 'cliente', 'cliente_nombre', 'cliente_correo',
            'servicio', 'servicio_nombre', 'peluquero', 'peluquero_nombre',
            'fecha_deseada', 'hora_deseada', 'fecha_registro',
            'notificado', 'fecha_notificacion', 'prioridad',
            'oferta_enviada', 'fecha_oferta_enviada', 'oferta_aceptada',
            'fecha_respuesta', 'descuento_aplicado', 'tiempo_limite_respuesta',
            'orden_notificacion'
        ]

class ConfiguracionReofertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionReoferta
        fields = '__all__'

class MarcaSerializer(serializers.ModelSerializer):
    productos_count = serializers.IntegerField(read_only=True)
    total_proveedores = serializers.IntegerField(read_only=True)
    proveedores_nombres = serializers.ListField(child=serializers.CharField(), read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Marca
        fields = [
            'id',
            'nombre',
            'descripcion',
            'estado',
            'estado_display',
            'productos_count',
            'total_proveedores',
            'proveedores_nombres',
            'fecha_creacion',
        ]

class CotizacionExternaSerializer(serializers.ModelSerializer):
    # Usamos ReadOnlyField para entrar a las relaciones sin fallar
    # cotizacion -> solicitud -> producto -> nombre
    producto_nombre = serializers.ReadOnlyField(source='solicitud.producto.nombre')
    cantidad_requerida = serializers.ReadOnlyField(source='solicitud.cantidad_requerida')
    proveedor_nombre = serializers.ReadOnlyField(source='proveedor.nombre')

    class Meta:
        model = Cotizacion
        fields = [
            'id', 'token', 'producto_nombre', 'cantidad_requerida', 
            'proveedor_nombre', 'precio_ofrecido', 'dias_entrega', 
            'comentarios', 'respondio'
        ]
# ==============================================================================
# EVALUACIÓN DE PRESUPUESTOS (administrador)
# ==============================================================================
class CotizacionDetalleSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)
    score = serializers.SerializerMethodField()

    class Meta:
        model = Cotizacion
        fields = [
            'id', 'proveedor', 'proveedor_nombre', 
            'precio_ofrecido', 'dias_entrega', 
            'cantidad_ofertada', 
            'comentarios', 'respondio', 'score', 'es_la_mejor'
        ]

    def get_score(self, obj):
        if obj.score == float('inf'):
            return None 
        return obj.score

class SolicitudPresupuestoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_stock = serializers.IntegerField(source='producto.stock_actual', read_only=True)
    cotizaciones = CotizacionDetalleSerializer(many=True, read_only=True)
    
    mejor_opcion_id = serializers.SerializerMethodField()

    class Meta:
        model = SolicitudPresupuesto
        fields = [
            'id', 'producto', 'producto_nombre', 'producto_stock', 
            'cantidad_requerida', 'fecha_creacion', 'estado', 
            'cotizaciones', 'mejor_opcion_id'
        ]

    def get_mejor_opcion_id(self, obj):
        """Devuelve el ID de la cotización con mejor puntaje (score)"""
        candidatas = [c for c in obj.cotizaciones.all() if c.respondio and c.precio_ofrecido]
        if not candidatas:
            return None
        # Ordenamos por score (menor es mejor)
        mejor = sorted(candidatas, key=lambda x: x.score)[0]
        return mejor.id

class AuditoriaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True, default='Sistema')
    usuario_apellido = serializers.CharField(source='usuario.apellido', read_only=True, default='')
    usuario_rol = serializers.CharField(source='usuario.rol.nombre', read_only=True, default='-')
    usuario_email = serializers.CharField(source='usuario.correo', read_only=True, default='')
    
    # ✅ NUEVO: Campos extraídos de 'detalles'
    navegador_info = serializers.SerializerMethodField()
    sistema_operativo = serializers.SerializerMethodField()
    dispositivo_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Auditoria
        fields = '__all__'
    
    def get_navegador_info(self, obj):
        """Extrae información del navegador de los detalles"""
        if not obj.detalles:
            return ''
        
        detalles = obj.detalles
        if isinstance(detalles, str):
            try:
                detalles = json.loads(detalles)
            except:
                return ''
        
        if not isinstance(detalles, dict):
            return ''
        
        # Buscar en diferentes ubicaciones posibles
        if '__meta__' in detalles and 'navegador' in detalles['__meta__']:
            return detalles['__meta__']['navegador']
        
        # También podría estar en otras ubicaciones
        for key in ['user_agent', 'browser', 'navegador', 'ua']:
            if key in detalles:
                return detalles[key]
        
        return ''
    
    def get_sistema_operativo(self, obj):
        """Extrae información del sistema operativo"""
        if not obj.detalles:
            return ''
        
        detalles = obj.detalles
        if isinstance(detalles, str):
            try:
                detalles = json.loads(detalles)
            except:
                return ''
        
        if not isinstance(detalles, dict):
            return ''
        
        if '__meta__' in detalles and 'so' in detalles['__meta__']:
            return detalles['__meta__']['so']
        
        for key in ['os', 'platform', 'sistema_operativo']:
            if key in detalles:
                return detalles[key]
        
        return ''
    
    def get_dispositivo_info(self, obj):
        """Información completa del dispositivo"""
        navegador = self.get_navegador_info(obj)
        sistema = self.get_sistema_operativo(obj)
        
        if not navegador and not sistema:
            return f"IP: {obj.ip_address or 'No registrada'}"
        
        if navegador and sistema:
            return f"{navegador} en {sistema} (IP: {obj.ip_address or 'N/A'})"
        
        if navegador:
            return f"{navegador} (IP: {obj.ip_address or 'N/A'})"
        
        return f"{sistema} (IP: {obj.ip_address or 'N/A'})"

# ================================
# Recuperar contra desde el login
# ================================
class SolicitarResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordConfirmarSerializer(serializers.Serializer):
    token = serializers.CharField()
    nueva_password = serializers.CharField(min_length=6)
    confirmar_password = serializers.CharField(min_length=6)

    def validate(self, data):
        if data['nueva_password'] != data['confirmar_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return data

class LiquidacionSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre', read_only=True)
    empleado_apellido = serializers.CharField(source='empleado.apellido', read_only=True)
    fecha_pago = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Liquidacion
        fields = '__all__'

class ConfiguracionSistemaSerializer(serializers.ModelSerializer):
    # ✅ Cambiado a ImageField para que permita RECIBIR y GUARDAR archivos
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = ConfiguracionSistema
        fields = '__all__'

    def to_representation(self, instance):
        """
        Este método se encarga de que, al ENVIAR datos al frontend,
        la URL del logo sea completa (http://localhost:8000/media/...)
        """
        ret = super().to_representation(instance)
        request = self.context.get('request')
        if instance.logo and request:
            ret['logo'] = request.build_absolute_uri(instance.logo.url)
        return ret

#Silla
class SillaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Silla
        fields = '__all__' # Devuelve id, nombre, activa, orden