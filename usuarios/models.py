# hairsoft/models.py
from django.db import models, transaction
from datetime import timedelta, datetime
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid
import secrets
from django.core.signing import Signer

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

    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    categorias = models.ManyToManyField('CategoriaProducto', blank=True)

    def __str__(self):
        return self.nombre

# ===============================
# MARCAS DE PRODUCTOS
# ===============================
class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "marcas"
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"

# ===============================
# PRODUCTOS
# ===============================
class Producto(models.Model):
    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]
    
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey('CategoriaProducto', on_delete=models.CASCADE, null=True, blank=True)
    proveedores = models.ManyToManyField('Proveedor', blank=True, related_name='productos')
    marca = models.ForeignKey('Marca', on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    stock_actual = models.IntegerField(default=0)
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVO')

    def clean(self):
        if self.precio is not None and self.precio < 0:
            raise ValidationError({'precio': 'El precio no puede ser negativo'})
        if self.stock_actual is not None and self.stock_actual < 0:
            raise ValidationError({'stock_actual': 'El stock no puede ser negativo'})

    def generar_codigo(self):
        if self.categoria:
            abreviatura = self.categoria.nombre[:3].upper()
            
            # Filtrar productos de la misma categoría que ya tienen código
            productos_categoria = Producto.objects.filter(
                categoria=self.categoria,
                codigo__startswith=abreviatura + "-"
            )
            
            # Si el producto ya existe (está siendo editado), excluirlo
            if self.pk:
                productos_categoria = productos_categoria.exclude(pk=self.pk)
            
            max_num = 0
            for producto in productos_categoria:
                try:
                    partes = producto.codigo.split('-')
                    if len(partes) == 2:
                        num = int(partes[1])
                        if num > max_num:
                            max_num = num
                except (ValueError, IndexError):
                    continue
            
            self.codigo = f"{abreviatura}-{max_num + 1:03d}"

    def save(self, *args, **kwargs):
        # Genera el código SIEMPRE si la categoría existe y codigo está vacío
        if self.categoria and not self.codigo:
            self.generar_codigo()
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.marca:
            return f"{self.nombre} ({self.marca.nombre})"
        return self.nombre

    class Meta:
        db_table = "productos"

# ===============================
# TURNOS - ACTUALIZADO CON REOFERTA
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
        ('DISPONIBLE', 'Disponible'), 
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

    # NUEVOS CAMPOS PARA REOFERTA MASIVA
    oferta_activa = models.BooleanField(default=False)
    fecha_expiracion_oferta = models.DateTimeField(null=True, blank=True)
    token_reoferta = models.CharField(max_length=100, blank=True, null=True)
    cliente_asignado_reoferta = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name="turnos_asignados_reoferta")

    def __str__(self):
        return f"{self.fecha} {self.hora} - {self.cliente.nombre} ({self.estado})"

    def puede_ser_modificado(self):
        ahora = timezone.now()
        # Nota: Asumo que en un entorno de producción, la base de datos y Django usarán UTC
        # Para hacer el combine, usamos la versión naive y luego la hacemos aware si es necesario
        fecha_turno_naive = datetime.combine(self.fecha, self.hora)
        fecha_turno = timezone.make_aware(fecha_turno_naive)
        tres_horas_antes = fecha_turno - timedelta(hours=3)
        return (self.estado in ['RESERVADO', 'CONFIRMADO'] and ahora < tres_horas_antes)

    def puede_ser_cancelado(self):
        if self.estado in ['COMPLETADO', 'CANCELADO']:
            return False, False, "No se puede cancelar un turno completado o ya cancelado"
        
        ahora = timezone.now()
        fecha_turno_naive = datetime.combine(self.fecha, self.hora)
        fecha_turno = timezone.make_aware(fecha_turno_naive)

        # No se pueden cancelar turnos pasados
        if ahora >= fecha_turno:
            return False, False, "No se puede cancelar un turno que ya pasó"
        
        tiempo_restante = fecha_turno - ahora
        puede_cancelar = True
        hay_reembolso = tiempo_restante >= timedelta(hours=3)
        
        mensaje = "Puede cancelar el turno"
        if hay_reembolso:
            mensaje += " con reembolso de seña"
        else:
            mensaje += " sin reembolso (menos de 3 horas de anticipación)"
        
        return puede_cancelar, hay_reembolso, mensaje
    
    def calcular_duracion_total(self):
        return sum(servicio.duracion for servicio in self.servicios.all())
    
    def necesita_pago_mp(self):
        return self.medio_pago == 'MERCADO_PAGO'

    # NUEVOS MÉTODOS PARA REOFERTA MASIVA
    def puede_reofertar(self):
        """Verifica si el turno puede ser reofertado"""
        if self.estado != 'CANCELADO':
            return False
            
        fecha_turno_naive = datetime.combine(self.fecha, self.hora)
        fecha_turno = timezone.make_aware(fecha_turno_naive)
        tiempo_restante = fecha_turno - timezone.now()
        
        # Debe quedar un tiempo razonable para reofertar
        return tiempo_restante > timedelta(minutes=5) and not self.oferta_activa
    
    def obtener_interesados(self):
            """
            ✅ CORREGIDO: Obtiene clientes interesados para este slot específico.
            Filtra por fecha, hora, peluquero y estado 'pendiente'.
            """
            print(f"🔍🔍🔍 BUSCANDO INTERESADOS PARA TURNO {self.id}:")

            # 1. Filtro base: Mismo slot (Fecha, Hora, Peluquero) y estado pendiente
            interesados = InteresTurnoLiberado.objects.filter(
                fecha_deseada=self.fecha,
                hora_deseada=self.hora,
                peluquero=self.peluquero,
                estado_oferta='pendiente' # Solo notificar a quienes no han sido contactados aún
            ).order_by('fecha_registro') # FIFO (First In, First Out)
            
            # 🚨 DEBUG Y FLEXIBILIDAD (Corregido para evitar NameError)
            # NOTA: Desactivamos el filtro por servicio para la prueba, ya que solo complica la depuración.
            
            servicios_ids = list(self.servicios.all().values_list('id', flat=True))

            print(f"   - Parámetros de búsqueda CORREGIDOS:")
            print(f"     fecha_deseada: {self.fecha}")
            print(f"     hora_deseada: {self.hora}") 
            print(f"     peluquero: {self.peluquero.id}")
            # 💡 Muestra los IDs de los servicios del turno, pero no filtra por ellos
            print(f"     Servicios en turno: {servicios_ids}") 
            print(f"   - Resultados encontrados (sin filtro de servicio): {interesados.count()}")

            return interesados
        
    def iniciar_reoferta(self):
        """Inicia el proceso de reoferta para este turno"""
        from .tasks import procesar_reoferta_masiva
        
        if self.puede_reofertar():
            self.oferta_activa = True
            # Asignar expiración de la reoferta 5 minutos antes del turno, por defecto
            fecha_turno_naive = datetime.combine(self.fecha, self.hora)
            fecha_turno = timezone.make_aware(fecha_turno_naive)
            self.fecha_expiracion_oferta = fecha_turno - timedelta(minutes=5)
            self.token_reoferta = secrets.token_urlsafe(32)
            self.save()
            
            # Disparar tarea async
            procesar_reoferta_masiva.delay(self.id)
            return True
        return False

    def save(self, *args, **kwargs):
        crear_venta = False
        if self.pk:
            old = Turno.objects.get(pk=self.pk)
            # Solo si el estado pasó a COMPLETADO
            if old.estado != 'COMPLETADO' and self.estado == 'COMPLETADO':
                crear_venta = True

        super().save(*args, **kwargs)

        if crear_venta:
            self.crear_venta_turno()

    @transaction.atomic
    def crear_venta_turno(self):
        # NOTA: Importa los modelos de Venta aquí si están en otro archivo/app
        # Si Venta y DetalleVenta están en esta misma app (usuarios), ignora el 'from ventas.models...'
        # Asumo que Venta y DetalleVenta están en esta misma app 'usuarios' dado el listado.
        
        total_servicios = sum(servicio.precio for servicio in self.servicios.all())
        # Buscamos el método de pago por defecto, si no existe, usamos el tipo de pago del turno
        medio_pago_obj = MetodoPago.objects.filter(nombre__iexact=self.medio_pago).first() 

        venta = Venta.objects.create(
            cliente=self.cliente,
            usuario=self.peluquero, # Asumimos que el peluquero registra el completado o un recepcionista (se podría cambiar a usuario logueado)
            total=total_servicios,
            tipo='TURNO',
            medio_pago=medio_pago_obj if medio_pago_obj else None
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
        # Recalcular total por si acaso
        venta.total = venta.detalles.aggregate(total=models.Sum('subtotal'))['total'] or 0
        venta.save()

    class Meta:
        db_table = "turnos"
        ordering = ['fecha', 'hora']

# Clientess interesados en turnos liberados - ACTUALIZADO Y CORREGIDO
class InteresTurnoLiberado(models.Model):
    """Clientes interesados en horarios específicos - ACTUALIZADO PARA REOFERTA"""
    ESTADO_OFERTA_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviada', 'Oferta Enviada'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('expirada', 'Expirada'),
    ]
    
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="intereses_turnos")
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    peluquero = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="intereses_peluquero")
    fecha_deseada = models.DateField()
    hora_deseada = models.TimeField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    # ✅ Relación directa con el turno liberado que se les está ofreciendo
    turno_liberado = models.ForeignKey(
        'Turno', 
        on_delete=models.SET_NULL, # Usar SET_NULL para no borrar el Interes si borran el Turno, solo desvincular
        related_name="intereses_asociados",
        null=True, 
        blank=True
    )
    
    # Campos para el proceso de reoferta masiva
    estado_oferta = models.CharField(max_length=20, choices=ESTADO_OFERTA_CHOICES, default='pendiente')
    token_oferta = models.CharField(max_length=100, unique=True, blank=True, null=True)
    fecha_envio_oferta = models.DateTimeField(null=True, blank=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    ip_aceptacion = models.GenericIPAddressField(null=True, blank=True)
    
    # Configuración de oferta
    descuento_aplicado = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)
    tiempo_limite_respuesta = models.IntegerField(default=60) 	# minutos
    
    # Para seguimiento del proceso FIFO
    prioridad = models.IntegerField(default=0)
    orden_notificacion = models.IntegerField(default=0)
    
    class Meta:
        db_table = "intereses_turnos_liberados"
        ordering = ['fecha_registro', 'prioridad']
        # ✅ CORRECCIÓN: Evitar duplicados para el mismo slot
        unique_together = ['cliente', 'peluquero', 'fecha_deseada', 'hora_deseada'] 
        # Se elimina 'servicio' del unique_together para permitir al cliente 
        # registrar interés por el mismo slot pero con distinto servicio (si fuera necesario).

    def __str__(self):
        return f"{self.cliente.nombre} - {self.fecha_deseada} {self.hora_deseada}"

    def save(self, *args, **kwargs):
        if not self.token_oferta:
            self.token_oferta = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def puede_ser_notificado(self):
        """Verifica si puede ser notificado"""
        return self.estado_oferta == 'pendiente'
    
    def oferta_expirada(self):
        """Verifica si la oferta ya expiró"""
        if not self.fecha_envio_oferta:
            return False
        tiempo_transcurrido = timezone.now() - self.fecha_envio_oferta
        # Usamos el tiempo límite de la configuración global si es nulo, si no, el del interés
        limite = self.tiempo_limite_respuesta or ConfiguracionReoferta.get_configuracion().tiempo_limite_respuesta
        return tiempo_transcurrido.total_seconds() > (limite * 60)
    
    def aceptar_oferta(self, ip_address=None):
        """Marca la oferta como aceptada"""
        self.estado_oferta = 'aceptada'
        self.fecha_respuesta = timezone.now()
        self.ip_aceptacion = ip_address
        self.save()
    
    def rechazar_oferta(self):
        """Marca la oferta como rechazada"""
        self.estado_oferta = 'rechazada'
        self.fecha_respuesta = timezone.now()
        self.save()
    
    def marcar_enviada(self):
        """Marca la oferta como enviada"""
        self.estado_oferta = 'enviada'
        self.fecha_envio_oferta = timezone.now()
        self.save()
# ===============================
# MÉTODOS DE PAGO (NUEVO MODELO)
# ===============================
class MetodoPago(models.Model):
    TIPO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'), 
        ('TRANSFERENCIA', 'Transferencia/QR'), 
    ]
    
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='EFECTIVO')
    activo = models.BooleanField(default=True)
    requiere_confirmacion = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "metodos_pago"

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

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADO', 'Confirmado'),
        ('COMPLETADO', 'Completado'),
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
        """Calcula el total usando los precios de la lista"""
        return self.detalles.aggregate(total=models.Sum('subtotal'))['total'] or 0

    def puede_ser_confirmado(self):
        """Solo se puede confirmar si está PENDIENTE"""
        return self.estado == 'PENDIENTE'

    def puede_ser_completado(self):
        """Solo si ya fue CONFIRMADO"""
        return self.estado == 'CONFIRMADO'
    
    def puede_ser_cancelado(self):
        """Solo se pueden cancelar pedidos PENDIENTES o CONFIRMADOS"""
        return self.estado in ['PENDIENTE', 'CONFIRMADO']

    @transaction.atomic
    def confirmar_pedido(self):
        """Confirma el pedido con los precios de la lista"""
        if not self.puede_ser_confirmado():
            raise ValueError("El pedido no puede ser confirmado en su estado actual")

        self.estado = 'CONFIRMADO'
        self.total = self.calcular_total()
        self.save()

    @transaction.atomic
    def completar_pedido(self):
        """Marca el pedido como COMPLETADO y actualiza stock"""
        if not self.puede_ser_completado():
            raise ValueError("El pedido no puede ser completado en su estado actual")

        # Actualizar stock
        for detalle in self.detalles.all():
            if detalle.producto and detalle.cantidad_recibida > 0:
                detalle.producto.stock_actual += detalle.cantidad_recibida
                detalle.producto.save()

        self.estado = 'COMPLETADO'
        self.fecha_recepcion = timezone.now()
        self.save()

    @transaction.atomic
    def cancelar_pedido(self):
        """Cancela el pedido"""
        if not self.puede_ser_cancelado():
            raise ValueError("El pedido no puede ser cancelado en su estado actual")
            
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

    # 🆕 Campo nuevo: precio propuesto por el proveedor
    precio_propuesto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Precio ofrecido por el proveedor"
    )

    # Precio confirmado (después de aceptar la cotización)
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Precio acordado final"
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Calcular subtotal solo si hay precio confirmado
        self.subtotal = (self.cantidad * self.precio_unitario) if self.precio_unitario else 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
    
    def porcentaje_recibido(self):
        if self.cantidad == 0:
            return 0
        return (self.cantidad_recibida / self.cantidad) * 100

    class Meta:
        db_table = "detalle_pedidos"
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedidos"

# ===Lista Precio por Proveedor================
class ListaPrecioProveedor(models.Model):
    proveedor = models.ForeignKey(
        'Proveedor',
        on_delete=models.CASCADE,
        related_name='listas_precios'
    )
    producto = models.ForeignKey(
        'Producto', 
        on_delete=models.CASCADE,
        related_name='listas_precios_proveedores'
    )
    precio_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio base del proveedor"
    )
    margen_ganancia = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.0,
        help_text="Porcentaje de ganancia (ej: 30 para +30%)"
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lista_precios_proveedores"
        verbose_name = "Lista de precios de proveedor"
        verbose_name_plural = "Listas de precios de proveedores"

    def __str__(self):
        return f"{self.proveedor.nombre} - {self.producto.nombre} (${self.precio_base})"

    @property
    def precio_sugerido_venta(self):
        """Calcula el precio final sugerido según el margen"""
        return self.precio_base * (1 + (self.margen_ganancia / 100))

    def puede_ser_editado(self):
        """Verifica si la lista de precios puede ser editada"""
        return self.activo


class HistorialPrecios(models.Model):
    lista_precio = models.ForeignKey(
        ListaPrecioProveedor,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    precio_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    precio_nuevo = models.DecimalField(max_digits=10, decimal_places=2)
    margen_anterior = models.DecimalField(max_digits=5, decimal_places=2)
    margen_nuevo = models.DecimalField(max_digits=5, decimal_places=2)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "historial_precios"
        ordering = ['-fecha_cambio']
        verbose_name = "Historial de precios"
        verbose_name_plural = "Historial de precios"

    def __str__(self):
        return f"Cambio {self.lista_precio} - {self.fecha_cambio.strftime('%d/%m/%Y')}"

#Reofera automatica del proceso automatizado!
class ConfiguracionReoferta(models.Model):
    """Configuración del módulo de reoferta automática"""
    descuento_por_defecto = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)
    tiempo_limite_respuesta = models.IntegerField(default=60) 	# minutos
    max_intentos_notificacion = models.IntegerField(default=3)
    activo = models.BooleanField(default=True)
    
    # Configuración de notificaciones
    notificar_email = models.BooleanField(default=True)
    notificar_whatsapp = models.BooleanField(default=False)
    
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "configuracion_reoferta"
        verbose_name = "Configuración de Reoferta"
        verbose_name_plural = "Configuraciones de Reoferta"

    def __str__(self):
        return f"Configuración Reoferta ({'Activo' if self.activo else 'Inactivo'})"

    @classmethod
    def get_configuracion(cls):
        """Obtiene la configuración activa, crea una por defecto si no existe"""
        config = cls.objects.first()
        if not config:
            config = cls.objects.create()
        return config