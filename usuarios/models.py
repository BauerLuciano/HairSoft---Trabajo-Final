# hairsoft/models.py
from django.db import models, transaction
from datetime import timedelta
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# ===============================
# MANAGER PERSONALIZADO PARA USUARIO
# ===============================
class UsuarioManager(BaseUserManager):
    def create_user(self, correo, password=None, **extra_fields):
        if not correo:
            raise ValueError('El correo es obligatorio')
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(correo, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(correo=username)

# ===============================
# ROLES
# ===============================

class Permiso(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    permisos = models.ManyToManyField('Permiso', blank=True, related_name='roles')

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "roles"


# ===============================
# CATEGORÍAS
# ===============================
class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "categorias_productos"


class CategoriaServicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "categorias_servicios"


# ===============================
# USUARIOS (CORREGIDO)
# ===============================
class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    dni = models.CharField(max_length=20, unique=True)
    contrasena = models.CharField(max_length=128)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(unique=True)
    
    # ✅ CAMPOS REQUERIDOS PARA AbstractBaseUser
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    # ✅ CONFIGURACIÓN PARA USER MODEL
    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre', 'apellido', 'dni']
    
    # ✅ MANAGER PERSONALIZADO
    objects = UsuarioManager()
    
    rol = models.ForeignKey('Rol', on_delete=models.SET_NULL, null=True)
    estado = models.CharField(max_length=15, default='ACTIVO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # ✅ MÉTODOS COMPATIBILIDAD
    def get_username(self):
        return self.correo

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rol.nombre if self.rol else 'Sin rol'})"

    class Meta:
        db_table = "usuarios"

# ===============================
# SERVICIOS
# ===============================
class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    duracion = models.PositiveIntegerField(help_text="Duración en minutos", default=20)
    categoria = models.ForeignKey(CategoriaServicio, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "servicios"


# ===============================
# PROVEEDORES
# ===============================
ESTADOS = [
    ('ACTIVO', 'Activo'),
    ('INACTIVO', 'Inactivo'),
]

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    cuit = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^[0-9\-]+$', 'Solo se permiten números y guiones.')]
    )
    contacto = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    productos_que_ofrece = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    categorias = models.ManyToManyField('CategoriaProducto', blank=True)
    productos_especificos = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# ===============================
# PRODUCTOS
# ===============================
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    stock_actual = models.PositiveIntegerField(default=0)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE, null=True, blank=True)
    proveedores = models.ManyToManyField(Proveedor, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "productos"


# ===============================
# TURNOS
# ===============================
class Turno(models.Model):
    CANAL_CHOICES = [
        ('WEB', 'Web'),
        ('PRESENCIAL', 'Presencial'),
    ]
    
    ESTADO_CHOICES = [
        ('RESERVADO', 'Reservado'),
        ('CONFIRMADO', 'Confirmado'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
    ]

    TIPO_PAGO_CHOICES = [
        ('SENA_50', 'Seña 50%'),
        ('TOTAL', 'Pago Total'),
        ('PENDIENTE', 'Pendiente de Pago'),
    ]
    
    MEDIO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('MERCADO_PAGO', 'Mercado Pago'),
        ('PENDIENTE', 'Pendiente'),
    ]

    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='RESERVADO')
    canal = models.CharField(max_length=15, choices=CANAL_CHOICES, default='PRESENCIAL')
    tipo_pago = models.CharField(max_length=15, choices=TIPO_PAGO_CHOICES, default='PENDIENTE')
    medio_pago = models.CharField(max_length=15, choices=MEDIO_PAGO_CHOICES, default='PENDIENTE')
    monto_seña = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    monto_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    reembolsado = models.BooleanField(default=False)
    
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="turnos_cliente")
    peluquero = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="turnos_peluquero")
    servicios = models.ManyToManyField(Servicio, db_table="turnos_servicios")

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fecha} {self.hora} - {self.cliente.nombre} ({self.estado})"

    def puede_ser_modificado(self):
        from django.utils import timezone
        ahora = timezone.now()
        fecha_turno = timezone.make_aware(
            timezone.datetime.combine(self.fecha, self.hora)
        )
        tres_horas_antes = fecha_turno - timedelta(hours=3)
        return (self.estado in ['RESERVADO', 'CONFIRMADO'] and ahora < tres_horas_antes)

    def puede_ser_cancelado(self):
        from django.utils import timezone
        ahora = timezone.now()
        fecha_turno = timezone.make_aware(
            timezone.datetime.combine(self.fecha, self.hora)
        )
        tres_horas_antes = fecha_turno - timedelta(hours=3)
        puede_cancelar = (self.estado in ['RESERVADO', 'CONFIRMADO'] and ahora < tres_horas_antes)
        return puede_cancelar, puede_cancelar  # segundo valor = hay_reembolso

    def calcular_duracion_total(self):
        return sum(servicio.duracion for servicio in self.servicios.all())
    
    def necesita_pago_mp(self):
        return self.medio_pago == 'MERCADO_PAGO'

    def save(self, *args, **kwargs):
        crear_venta = False
        if self.pk:
            old = Turno.objects.get(pk=self.pk)
            if old.estado != 'COMPLETADO' and self.estado == 'COMPLETADO':
                crear_venta = True

        super().save(*args, **kwargs)

    @transaction.atomic
    def crear_venta_turno(self):
        from ventas.models import Venta, DetalleVenta
        total_servicios = sum(servicio.precio for servicio in self.servicios.all())
        venta = Venta.objects.create(
            cliente=self.cliente,
            usuario=self.peluquero,
            total=total_servicios,
            tipo='TURNO'
        )
        for servicio in self.servicios.all():
            DetalleVenta.objects.create(
                venta=venta,
                servicio=servicio,
                turno=self,
                cantidad=1,
                precio_unitario=servicio.precio,
                subtotal=servicio.precio
            )
        venta.total = venta.detalles.aggregate(total=models.Sum('subtotal'))['total'] or 0
        venta.save()

    class Meta:
        db_table = "turnos"
        ordering = ['fecha', 'hora']

# ===============================
# MÉTODOS DE PAGO (NUEVO MODELO)
# ===============================
class MetodoPago(models.Model):
    TIPO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),  # ✅ Unificado: débito/crédito
        ('TRANSFERENCIA', 'Transferencia/QR'),  # ✅ Unificado
    ]
    
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='EFECTIVO')
    activo = models.BooleanField(default=True)
    requiere_confirmacion = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre


# ===============================
# VENTAS
# ===============================
TIPO_VENTA_CHOICES = [
    ('PRODUCTO', 'Producto'),
    ('TURNO', 'Turno'),
]

class Venta(models.Model):
    cliente = models.ForeignKey(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='compras_realizadas',
        help_text="Cliente asociado a la venta. Puede ser null si es venta rápida."
    )
    usuario = models.ForeignKey(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='ventas_registradas',
        help_text="Empleado o usuario que registró la venta."
    )
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    anulada = models.BooleanField(default=False)
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_VENTA_CHOICES,
        default='PRODUCTO'
    )
    # ✅ CORRECCIÓN CLAVE: ForeignKey al nuevo modelo MetodoPago
    medio_pago = models.ForeignKey(
        'MetodoPago',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Método de pago utilizado para esta transacción."
    )

    def __str__(self):
        return f"Venta {self.id} - {self.tipo} ({self.fecha.strftime('%d/%m/%Y %H:%M')})"

    class Meta:
        db_table = "ventas"
        ordering = ['-fecha']
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        'Producto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    servicio = models.ForeignKey(
        'Servicio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    turno = models.ForeignKey(
        'Turno',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Precio unitario del producto o servicio al momento de la venta."
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.subtotal:
            self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        if self.producto:
            return f"{self.producto.nombre} x{self.cantidad}"
        elif self.servicio:
            return f"{self.servicio.nombre} x{self.cantidad}"
        elif self.turno:
            return f"Turno {self.turno.id}"
        return f"Detalle {self.id}"

    class Meta:
        db_table = "detalle_ventas"
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Ventas"

# ===============================
# PEDIDOS
# ===============================
# En usuarios/models.py - CORREGIR los estados del pedido
class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADO', 'Confirmado'),  # ✅ ESTADO NUEVO
        ('ENTREGADO', 'Entregado'),    # ✅ ESTADO NUEVO (en lugar de RECIBIDO)
        ('CANCELADO', 'Cancelado'),
    ]

    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.PROTECT,
        related_name='pedidos'
    )
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_esperada_recepcion = models.DateField(null=True, blank=True)
    fecha_recepcion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='PENDIENTE'
    )
    observaciones = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Auditoría
    usuario_creador = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='pedidos_creados',
        null=True,
        blank=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.proveedor.nombre} ({self.estado})"

    def calcular_total(self):
        """Calcula el total sumando todos los detalles"""
        return self.detalles.aggregate(total=models.Sum('subtotal'))['total'] or 0

    def puede_ser_cancelado(self):
        """Un pedido solo puede cancelarse si está pendiente"""
        return self.estado == 'PENDIENTE'

    def puede_ser_recibido(self):
        """Un pedido puede recibirse si está pendiente o parcial"""
        return self.estado in ['PENDIENTE', 'PARCIAL']

    @transaction.atomic
    def recibir_pedido(self):
        """Marca el pedido como recibido y actualiza stock"""
        if not self.puede_ser_recibido():
            raise ValueError("El pedido no puede ser recibido en su estado actual")
        
        # Actualizar stock de productos
        for detalle in self.detalles.all():
            if detalle.producto and detalle.cantidad_recibida > 0:
                detalle.producto.stock_actual += detalle.cantidad_recibida
                detalle.producto.save()
        
        # Verificar si fue recepción parcial o completa
        total_solicitado = self.detalles.aggregate(total=models.Sum('cantidad'))['total'] or 0
        total_recibido = self.detalles.aggregate(total=models.Sum('cantidad_recibida'))['total'] or 0
        
        if total_recibido == total_solicitado:
            self.estado = 'ENTREGADO'  # ✅ CAMBIADO DE 'RECIBIDO' A 'ENTREGADO'
        else:
            self.estado = 'PARCIAL'
            
        self.fecha_recepcion = timezone.now()
        self.save()

    @transaction.atomic
    def cancelar_pedido(self):
        """Cancela el pedido"""
        if not self.puede_ser_cancelado():
            raise ValueError("El pedido no puede ser cancelado")
        
        self.estado = 'CANCELADO'
        self.save()

    class Meta:
        db_table = "pedidos"
        ordering = ['-fecha_pedido']
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='detalles_pedidos'
    )
    cantidad = models.PositiveIntegerField(default=1)
    cantidad_recibida = models.PositiveIntegerField(default=0)
    precio_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Precio acordado con el proveedor"
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} - ${self.subtotal}"

    def porcentaje_recibido(self):
        """Calcula el porcentaje recibido de este producto"""
        if self.cantidad == 0:
            return 0
        return (self.cantidad_recibida / self.cantidad) * 100

    class Meta:
        db_table = "detalle_pedidos"
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedidos"
        unique_together = ['pedido', 'producto']