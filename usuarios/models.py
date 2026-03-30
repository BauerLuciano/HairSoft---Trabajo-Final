# hairsoft/models.py
from django.db import models, transaction
from datetime import timedelta, datetime
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.mail import get_connection, EmailMessage
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.signing import Signer
import secrets, time, threading, uuid, pytz

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
class CategoriaServicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "categorias_servicios"

class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "categorias_productos"

# ===============================
# USUARIOS (CORREGIDO)
# ===============================
class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    dni = models.CharField(max_length=20, unique=True)
    contrasena = models.CharField(max_length=128)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(unique=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre', 'apellido', 'dni']
    
    objects = UsuarioManager()
    
    rol = models.ForeignKey('Rol', on_delete=models.SET_NULL, null=True)
    estado = models.CharField(max_length=15, default='ACTIVO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    sueldo_fijo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Sueldo Fijo Mensual",
        help_text="Usar solo para empleados con fijo (ej. Recepción)"
    )

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
    categoria = models.ForeignKey('CategoriaServicio', on_delete=models.CASCADE, null=True, blank=True)
    descripcion = models.TextField(blank=True, null=True) 
    activo = models.BooleanField(default=True) 

    porcentaje_comision = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00, 
        help_text="Porcentaje que gana el peluquero por este servicio (0 a 100)"
    )

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
    nombre = models.CharField(max_length=200, unique=True)
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
    ESTADOS = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    )
    
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    proveedores = models.ManyToManyField('Proveedor', blank=True, related_name='marcas')

    def __str__(self):
        return self.nombre

# ===============================
# PRODUCTOS
# ===============================
class Producto(models.Model):
    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]
    
    nombre = models.CharField(max_length=255, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    
    categoria = models.ForeignKey('CategoriaProducto', on_delete=models.CASCADE, null=True, blank=True)
    proveedores = models.ManyToManyField('Proveedor', blank=True, related_name='productos')
    marca = models.ForeignKey('Marca', on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5) 
    lote_reposicion = models.IntegerField(default=1) 

    codigo = models.CharField(max_length=20, unique=True, editable=False)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVO')
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True, verbose_name="Imagen del Producto")
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.precio is not None and self.precio < 0:
            raise ValidationError({'precio': 'El precio no puede ser negativo'})
        if self.stock_actual is not None and self.stock_actual < 0:
            raise ValidationError({'stock_actual': 'El stock no puede ser negativo'})
        if self.stock_minimo is not None and self.stock_minimo < 0:
            raise ValidationError({'stock_minimo': 'El stock mínimo no puede ser negativo'})
        if self.lote_reposicion is not None and self.lote_reposicion < 1:
            raise ValidationError({'lote_reposicion': 'El lote de reposición debe ser al menos 1'})

    def generar_codigo(self):
        if self.categoria:
            abreviatura = self.categoria.nombre[:3].upper()
            productos_categoria = Producto.objects.filter(
                categoria=self.categoria,
                codigo__startswith=abreviatura + "-"
            )
            if self.pk:
                productos_categoria = productos_categoria.exclude(pk=self.pk)
            
            max_num = 0
            for producto in productos_categoria:
                try:
                    partes = producto.codigo.split('-')
                    if len(partes) == 2:
                        num = int(partes[1])
                        if num > max_num: max_num = num
                except (ValueError, IndexError):
                    continue
            self.codigo = f"{abreviatura}-{max_num + 1:03d}"

    def save(self, *args, **kwargs):
        # 1. Lógica de código y validación
        if self.categoria and not self.codigo:
            self.generar_codigo()
        
        self.clean()
        
        # 2. Guardado físico en DB
        super().save(*args, **kwargs)

        print(f"🔄 GUARDANDO: {self.nombre} | Stock: {self.stock_actual}")

        if self.estado == 'ACTIVO' and self.stock_actual <= self.stock_minimo:
            from .tasks import procesar_alertas_stock_proveedores
            procesar_alertas_stock_proveedores.delay(self.id)
            print(f"🚀 [CELERY] Tarea de stock encolada para {self.nombre}")

    def __str__(self):
        if self.marca:
            return f"{self.nombre} ({self.marca.nombre})"
        return self.nombre

    class Meta:
        db_table = "productos"
        constraints = [
            models.UniqueConstraint(
                fields=['nombre', 'marca'],
                name='unique_producto_nombre_marca',
                condition=models.Q(estado='ACTIVO') 
            )
        ]

#Solicitud  Reabastecimiento
class SolicitudReabastecimiento(models.Model):
    ESTADOS = (
        ('PENDIENTE', 'Esperando Respuestas'),
        ('CERRADA', 'Cerrada / Decisión Tomada'),
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_solicitada = models.PositiveIntegerField(default=10) # Cantidad a pedir por defecto
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')

    def __str__(self):
        return f"Reabastecer {self.producto.nombre} - {self.fecha_creacion.date()}"

class CotizacionProveedor(models.Model):
    """
    Esta es la 'tabla' que llena el proveedor desde el link.
    """
    solicitud = models.ForeignKey(SolicitudReabastecimiento, related_name='cotizaciones', on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    
    token_acceso = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    precio_ofrecido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dias_entrega = models.PositiveIntegerField(null=True, blank=True, help_text="Días hábiles para entregar")
    comentarios = models.TextField(blank=True, null=True)
    
    respondió = models.BooleanField(default=False)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)

    @property
    def puntaje_sistema(self):
        if not self.precio_ofrecido or not self.dias_entrega:
            return 0
        score_precio = 10000 / float(self.precio_ofrecido) 
        score_tiempo = 100 / float(self.dias_entrega)
        return (score_precio * 0.7) + (score_tiempo * 0.3)

class Silla(models.Model):
    nombre = models.CharField(max_length=50, unique=True, help_text="Ej: Silla 1, Puesto Ventana, Lavacabezas")
    activa = models.BooleanField(default=True, help_text="Desmarcar si la silla está rota o fuera de servicio")
    orden = models.PositiveIntegerField(unique=True, help_text="Número para ordenar visualmente (1, 2, 3...)") 
    motivo_inactividad = models.CharField(max_length=100, null=True, blank=True, help_text="Razón por la cual no se usa")

    class Meta:
        ordering = ['orden', 'nombre'] 
        verbose_name = "Silla / Puesto"
        verbose_name_plural = "Sillas / Puestos"

    def __str__(self):
        return f"{self.nombre} ({'Activa' if self.activa else 'Inactiva'})"


class Turno(models.Model):
    CANAL_CHOICES = [('WEB', 'Web'), ('PRESENCIAL', 'Presencial')]
    ESTADO_CHOICES = [
        ('RESERVADO', 'Reservado'), 
        ('COMPLETADO', 'Completado'), 
        ('CANCELADO', 'Cancelado'), 
    ]
    TIPO_PAGO_CHOICES = [('SENA_50', 'Seña 50%'), ('TOTAL', 'Pago Total'), ('PENDIENTE', 'Pendiente de Pago')]
    MEDIO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'), 
        ('MERCADO_PAGO', 'Mercado Pago'), 
        ('TRANSFERENCIA', 'Transferencia'), 
        ('PENDIENTE', 'Pendiente')
    ]
    REEMBOLSO_ESTADO_CHOICES = [
        ('NO_APLICA', 'No Aplica'), 
        ('PENDIENTE', 'Pendiente de Devolución'), 
        ('COMPLETADO', 'Devuelto al Cliente')
    ]

    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='RESERVADO')
    canal = models.CharField(max_length=15, choices=CANAL_CHOICES, default='PRESENCIAL')
    tipo_pago = models.CharField(max_length=15, choices=TIPO_PAGO_CHOICES, default='PENDIENTE')
    medio_pago = models.CharField(max_length=20, choices=MEDIO_PAGO_CHOICES, default='PENDIENTE')
    monto_seña = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    monto_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    duracion_total = models.IntegerField(default=0)
    
    # TRAZABILIDAD FINANCIERA
    reembolsado = models.BooleanField(default=False)
    reembolso_estado = models.CharField(max_length=20, choices=REEMBOLSO_ESTADO_CHOICES, default='NO_APLICA')
    
    # Integración automática (Web)
    mp_payment_id = models.CharField(max_length=50, blank=True, null=True)
    mp_refund_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Trazabilidad Manual (Transferencias presenciales / otros)
    nro_transaccion = models.CharField(max_length=100, blank=True, null=True)
    entidad_pago = models.CharField(max_length=50, blank=True, null=True, verbose_name="Billetera/Banco Origen")
    codigo_transaccion = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cód. Comprobante Manual")
    medio_pago_restante = models.CharField(max_length=20, choices=MEDIO_PAGO_CHOICES, blank=True, null=True)
    entidad_pago_restante = models.CharField(max_length=50, blank=True, null=True, verbose_name="Billetera/Banco Restante")
    codigo_transaccion_restante = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cód. Comprobante Restante")
    
    # MOTIVOS DE CANCELACIÓN
    motivo_cancelacion = models.CharField(max_length=100, blank=True, null=True)
    obs_cancelacion = models.TextField(blank=True, null=True)

    cliente = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name="turnos_cliente")
    peluquero = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name="turnos_peluquero")
    servicios = models.ManyToManyField('Servicio', db_table="turnos_servicios")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    oferta_activa = models.BooleanField(default=False)
    fecha_expiracion_oferta = models.DateTimeField(null=True, blank=True)
    token_reoferta = models.CharField(max_length=100, blank=True, null=True)
    cliente_asignado_reoferta = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name="turnos_asignados_reoferta")
    monto_comision = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    monto_original = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Monto sin descuento")
    descuento_aplicado = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Descuento aplicado")
    silla = models.ForeignKey('Silla', on_delete=models.SET_NULL, null=True, blank=True, related_name='turnos', verbose_name="Silla Asignada")
    
    def __str__(self):
        nombre_cli = self.cliente.nombre if self.cliente else "Disponible"
        return f"{self.fecha} {self.hora} - {nombre_cli}"
    
    def puede_ser_cancelado(self):
        """
        ✅ NUEVA LÓGICA: siempre se puede cancelar (si el turno está activo).
        El reembolso depende del margen de cancelación.
        """
        if self.estado in ['COMPLETADO', 'CANCELADO']:
            return False, False, "El turno ya no está activo."
        
        tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')
        ahora_utc = timezone.now()
        ahora_arg = ahora_utc.astimezone(tz_arg)
        
        fecha_turno_naive = datetime.combine(self.fecha, self.hora)
        fecha_turno_arg = tz_arg.localize(fecha_turno_naive)
        
        diferencia = fecha_turno_arg - ahora_arg
        horas_restantes = diferencia.total_seconds() / 3600
        
        from usuarios.models import ConfiguracionSistema
        config = ConfiguracionSistema.get_solo()
        margen = config.margen_horas_cancelacion or 3
        
        hay_reembolso = horas_restantes >= margen
        if hay_reembolso:
            msg = f"Reembolso habilitado (faltan {round(horas_restantes, 1)}hs)"
        else:
            msg = f"Fuera de término para reembolso (faltan {round(horas_restantes, 1)}hs)"
        
        # ✅ SIEMPRE puede cancelar si el estado lo permite
        puede_cancelar = True if self.estado in ['RESERVADO', 'DISPONIBLE'] else False
        
        return puede_cancelar, hay_reembolso, msg

    def puede_ser_modificado(self):
        if self.estado not in ['RESERVADO', 'DISPONIBLE']:
            return False, f"No se puede modificar un turno en estado {self.estado}"
        
        tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')
        ahora_utc = timezone.now()
        ahora_arg = ahora_utc.astimezone(tz_arg)
        
        fecha_turno_naive = datetime.combine(self.fecha, self.hora)
        fecha_turno_arg = tz_arg.localize(fecha_turno_naive)
        
        diferencia = fecha_turno_arg - ahora_arg
        horas_restantes = diferencia.total_seconds() / 3600
        
        if horas_restantes < 3:
            return False, f"No se puede modificar con menos de 3 horas de anticipación (faltan {round(horas_restantes, 1)}hs)"
        
        return True, "OK"
    
    def usuario_puede_modificar(self, usuario):
        if usuario.is_superuser:
            return True
        
        grupos_usuario = usuario.groups.values_list('name', flat=True)
        
        if 'Administrador' in grupos_usuario:
            return True
        
        if 'Recepcionista' in grupos_usuario:
            return True
        
        if 'Peluquero' in grupos_usuario:
            return usuario.id == self.peluquero.id
        
        return False
    
    def verificar_disponibilidad(self, fecha, hora, peluquero_id, excluir_turno_id=None):
        from .models import Turno
        
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        if isinstance(hora, str):
            hora = datetime.strptime(hora, "%H:%M").time()
        
        turnos_solapados = Turno.objects.filter(
            fecha=fecha,
            hora=hora,
            peluquero_id=peluquero_id,
            estado__in=['RESERVADO', 'DISPONIBLE']
        )
        
        if excluir_turno_id:
            turnos_solapados = turnos_solapados.exclude(id=excluir_turno_id)
        
        return not turnos_solapados.exists()

    def calcular_duracion_total(self):
        return sum(servicio.duracion for servicio in self.servicios.all())
    
    def necesita_pago_mp(self):
        return self.medio_pago == 'MERCADO_PAGO'

    def puede_reofertar(self):
        if self.estado != 'CANCELADO': return False
        import pytz
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        tz_arg = pytz.timezone('America/Argentina/Buenos_Aires')
        fecha_turno_naive = datetime.combine(self.fecha, self.hora)
        fecha_turno = tz_arg.localize(fecha_turno_naive)
        tiempo_restante = fecha_turno - timezone.localtime(timezone.now(), tz_arg)
        return tiempo_restante > timedelta(minutes=5) and not self.oferta_activa

    def obtener_interesados(self):
        from django.apps import apps
        InteresTurnoLiberado = apps.get_model('usuarios', 'InteresTurnoLiberado')
        return InteresTurnoLiberado.objects.filter(fecha_deseada=self.fecha, hora_deseada=self.hora, peluquero=self.peluquero, estado_oferta='pendiente').order_by('fecha_registro')

    def calcular_comision_peluquero(self):
        total_comision = 0
        for s in self.servicios.all():
            porcentaje = getattr(s, 'porcentaje_comision', 0)
            if porcentaje > 0:
                total_comision += float(s.precio) * (float(porcentaje) / 100)
        return round(total_comision, 2)

    def save(self, *args, **kwargs):
        crear_venta = False
        if self.pk:
            try:
                old = Turno.objects.get(pk=self.pk)
                if old.estado != 'COMPLETADO' and self.estado == 'COMPLETADO': crear_venta = True
            except: pass
        super().save(*args, **kwargs)
        if self.estado == 'COMPLETADO':
            self.monto_comision = self.calcular_comision_peluquero()
            Turno.objects.filter(pk=self.pk).update(monto_comision=self.monto_comision)
        if crear_venta: self.crear_venta_turno()

    @transaction.atomic
    def crear_venta_turno(self):
        from django.apps import apps
        MetodoPago = apps.get_model('usuarios', 'MetodoPago')
        Venta = apps.get_model('usuarios', 'Venta')
        DetalleVenta = apps.get_model('usuarios', 'DetalleVenta')
        
        total_servicios = sum(servicio.precio for servicio in self.servicios.all())
        medio_obj, _ = MetodoPago.objects.get_or_create(nombre__iexact='Efectivo', defaults={'nombre': 'Efectivo', 'tipo': 'EFECTIVO', 'activo': True})
        
        if self.medio_pago == 'MERCADO_PAGO':
             mp_obj = MetodoPago.objects.filter(tipo='MERCADOPAGO').first()
             if mp_obj:
                 medio_obj = mp_obj

        venta = Venta.objects.create(
            cliente=self.cliente, 
            usuario=self.peluquero, 
            total=total_servicios, 
            tipo='TURNO', 
            medio_pago=medio_obj,
            entidad_pago=self.entidad_pago,
            codigo_transaccion=self.codigo_transaccion or self.mp_payment_id
        )
        for s in self.servicios.all():
            DetalleVenta.objects.create(venta=venta, servicio=s, turno=self, cantidad=1, precio_unitario=s.precio, subtotal=s.precio)

    class Meta:
        db_table = "turnos"
        ordering = ['fecha', 'hora']

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
    
    turno_liberado = models.ForeignKey(
        'Turno', 
        on_delete=models.SET_NULL, # Usar SET_NULL para no borrar el Interes si borran el Turno, solo desvincular
        related_name="intereses_asociados",
        null=True, 
        blank=True
    )
    
    estado_oferta = models.CharField(max_length=20, choices=ESTADO_OFERTA_CHOICES, default='pendiente')
    token_oferta = models.CharField(max_length=100, unique=True, blank=True, null=True)
    fecha_envio_oferta = models.DateTimeField(null=True, blank=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    ip_aceptacion = models.GenericIPAddressField(null=True, blank=True)
    
    descuento_aplicado = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)
    tiempo_limite_respuesta = models.IntegerField(default=60) 	# minutos
    
    prioridad = models.IntegerField(default=0)
    orden_notificacion = models.IntegerField(default=0)
    
    class Meta:
        db_table = "intereses_turnos_liberados"
        ordering = ['fecha_registro', 'prioridad']
        unique_together = ['cliente', 'peluquero', 'fecha_deseada', 'hora_deseada', 'servicio'] 

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
# MÉTODOS DE PAGO (CORREGIDO)
# ===============================
class MetodoPago(models.Model):
    TIPO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('MERCADOPAGO', 'Mercado Pago'),    # Para integración Web/QR
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
    
    medio_pago = models.ForeignKey(
        'MetodoPago',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Método de pago utilizado para esta transacción."
    )

    entidad_pago = models.CharField(
        max_length=50, 
        null=True, 
        blank=True, 
        verbose_name="Billetera/Banco Origen"
    )
    codigo_transaccion = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="Código de Comprobante Manual"
    )
    nro_transaccion = models.CharField(max_length=100, null=True, blank=True) # Mantenemos por compatibilidad con código viejo
    mp_payment_id = models.CharField(max_length=50, null=True, blank=True)    # Mantenemos por compatibilidad con código viejo
    motivo_anulacion = models.TextField(null=True, blank=True, help_text="Razón por la cual se canceló la venta.")
    fecha_anulacion = models.DateTimeField(null=True, blank=True)

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
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Definimos los estados posibles
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),               
        ('ENVIADO', 'Enviado a Proveedor'),       
        ('COTIZADO', 'Cotizado por Proveedor'),   
        ('CONFIRMADO', 'Confirmado por Proveedor'), 
        ('ENTREGADO', 'Recibido en Local'),       
        ('CANCELADO', 'Cancelado')
    ]

    proveedor = models.ForeignKey(
        'Proveedor', # Usá string si Proveedor está definido más abajo o import circular
        on_delete=models.PROTECT,
        related_name='pedidos'
    )
    
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default='PENDIENTE'
    )

    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_esperada_recepcion = models.DateField(null=True, blank=True)
    fecha_recepcion = models.DateTimeField(null=True, blank=True)
    
    observaciones = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Auditoría
    usuario_creador = models.ForeignKey(
        'Usuario',
        on_delete=models.PROTECT,
        related_name='pedidos_creados',
        null=True,
        blank=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pedidos"
        ordering = ['-fecha_pedido']
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido #{self.id} - {self.proveedor.nombre} ({self.get_estado_display()})"

    def calcular_total(self):
        """Calcula el total usando los precios de los detalles"""
        return self.detalles.aggregate(total=models.Sum('subtotal'))['total'] or 0

    # --- LÓGICA DE ESTADOS ---

    def puede_ser_enviado(self):
        return self.estado == 'PENDIENTE'

    def puede_ser_confirmado(self):
        """El proveedor o el admin confirman precios/cantidades"""
        return self.estado in ['PENDIENTE', 'ENVIADO', 'COTIZADO']

    def puede_ser_completado(self):
        """
        Verifica si el pedido puede ser completado (recibido).
        El serializer busca este nombre exacto.
        """
        return self.estado == 'CONFIRMADO'
    
    def puede_ser_cancelado(self):
        return self.estado in ['PENDIENTE', 'ENVIADO', 'COTIZADO', 'CONFIRMADO']

    # --- MÉTODOS TRANSACCIONALES ---

    @transaction.atomic
    def confirmar_pedido(self):
        """Pasa a confirmado (listo para recibir)"""
        if not self.puede_ser_confirmado():
            raise ValueError(f"No se puede confirmar un pedido en estado {self.estado}")

        self.estado = 'CONFIRMADO'
        self.total = self.calcular_total()
        self.save()

    @transaction.atomic
    def completar_pedido(self): 
        pass

    @transaction.atomic
    def cancelar_pedido(self):
        if not self.puede_ser_cancelado():
            raise ValueError(f"No se puede cancelar un pedido en estado {self.estado}")
            
        self.estado = 'CANCELADO'
        self.save()

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

class PedidoWeb(models.Model):
    ESTADO_PENDIENTE_PAGO = 'PENDIENTE_PAGO'
    ESTADO_PAGADO = 'PAGADO'
    ESTADO_PREPARACION = 'EN_PREPARACION'
    ESTADO_LISTO_RETIRO = 'LISTO_RETIRO'
    ESTADO_EN_CAMINO = 'EN_CAMINO'
    ESTADO_ENTREGADO = 'ENTREGADO'
    ESTADO_CANCELADO = 'CANCELADO'

    ESTADOS_CHOICES = [
        (ESTADO_PENDIENTE_PAGO, 'Esperando Pago'),
        (ESTADO_PAGADO, 'Pagado - A preparar'),
        (ESTADO_PREPARACION, 'En preparación'),
        (ESTADO_LISTO_RETIRO, 'Listo para retirar en Local'),
        (ESTADO_EN_CAMINO, 'En camino (Moto/Correo)'),
        (ESTADO_ENTREGADO, 'Entregado / Finalizado'),
        (ESTADO_CANCELADO, 'Cancelado'),
    ]

    # Opciones de Entrega
    ENTREGA_RETIRO = 'RETIRO'
    ENTREGA_MOTO = 'MOTO'
    ENTREGA_CORREO = 'CORREO'

    ENTREGA_CHOICES = [
        (ENTREGA_RETIRO, 'Retiro en el Local'),
        (ENTREGA_MOTO, 'Envío Moto (San Vicente)'),
        (ENTREGA_CORREO, 'Envío Correo (Nacional)'),
    ]

    cliente = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='pedidos_web')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default=ESTADO_PENDIENTE_PAGO)
    tipo_entrega = models.CharField(max_length=20, choices=ENTREGA_CHOICES, default=ENTREGA_RETIRO)
    
    direccion_envio = models.TextField(null=True, blank=True, help_text="Dirección completa si es envío")
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    mp_payment_id = models.CharField(max_length=100, null=True, blank=True, help_text="ID de pago de MercadoPago")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Total productos + envío")
    motivo_cancelacion = models.CharField(max_length=100, blank=True, null=True)
    obs_cancelacion = models.TextField(blank=True, null=True)

    # ✅ Campo para trazabilidad de la moto
    datos_entrega_interna = models.CharField(max_length=255, null=True, blank=True, help_text="Nombre del cadete")

    def __str__(self):
        return f"Pedido Web #{self.id} - {self.cliente.nombre} {self.cliente.apellido}"

    def calcular_total(self):
        total_productos = sum(item.cantidad * item.precio_unitario for item in self.detalles.all())
        self.total = total_productos + self.costo_envio
        self.save()

class DetallePedidoWeb(models.Model):
    pedido = models.ForeignKey(PedidoWeb, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT) 
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Detalle de Pedido Web"
        verbose_name_plural = "Detalles de Pedidos Web"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario  

# ==============================================================================
# MÓDULO INTELIGENTE: REABASTECIMIENTO AUTOMÁTICO (PROVEEDORES)
# ==============================================================================

class SolicitudPresupuesto(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Esperando Respuestas'),
        ('CERRADA', 'Cerrada / Decisión Tomada'),
    ]
    # Usamos 'Producto' entre comillas para evitar errores de orden de lectura
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='solicitudes_presupuesto')
    cantidad_requerida = models.PositiveIntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    
    # El pedido que se generó a partir de la mejor cotización (opcional)
    pedido_generado = models.ForeignKey('Pedido', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        # Manejo de error por si el producto se borró
        prod_nombre = self.producto.nombre if self.producto else "Producto Eliminado"
        return f"Solicitud #{self.id} - {prod_nombre}"

class Cotizacion(models.Model):
    solicitud = models.ForeignKey(SolicitudPresupuesto, on_delete=models.CASCADE, related_name='cotizaciones')
    proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE)
    
    token = models.CharField(max_length=100, unique=True, default=secrets.token_urlsafe)
    
    # --- CAMPO NUEVO ---
    cantidad_ofertada = models.IntegerField(null=True, blank=True, help_text="Cantidad real que tiene el proveedor")
    # -------------------

    precio_ofrecido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dias_entrega = models.IntegerField(null=True, blank=True, help_text="Días hábiles")
    comentarios = models.TextField(blank=True, null=True)
    
    fecha_email_enviado = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    respondio = models.BooleanField(default=False)
    es_la_mejor = models.BooleanField(default=False)

    def __str__(self):
        return f"Cotización {self.proveedor.nombre} - {self.solicitud.id}"

    @property
    def score(self):
        if not self.precio_ofrecido:
            return float('inf')
        p = float(self.precio_ofrecido)
        d = float(self.dias_entrega or 5) 
        return (p * 0.7) + (d * 10)

# ==============================================================================
# MÓDULO DE FIDELIZACIÓN: REACTIVACIÓN DE CLIENTES
# ==============================================================================

class PromocionReactivacion(models.Model):
    ESTADOS = [
        ('ACTIVA', 'Activa (Enviada)'),
        ('USADA', 'Usada (Canjeada)'),
        ('VENCIDA', 'Vencida (No aprovechada)'),
    ]

    cliente = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='promociones_reactivacion')
    
    # Código único que viaja en el link (ej: VOLVE-A1B2)
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único para canjear")
    
    # Porcentaje de descuento (Parametrizable por si querés cambiarlo a futuro)
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateTimeField()
    
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVA')
    
    # Guardamos en qué turno se usó para trazabilidad
    turno_canje = models.ForeignKey('Turno', on_delete=models.SET_NULL, null=True, blank=True, related_name='promo_usada')
    
    # 🔥 AGREGAR ESTOS CAMPOS PARA TRAZABILIDAD:
    mp_payment_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID de transacción/pago")
    mensaje_sid = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID de mensaje Twilio")
    canal_envio = models.CharField(max_length=20, blank=True, null=True, verbose_name="Canal de envío")

    def __str__(self):
        return f"Promo {self.cliente.nombre} - {self.codigo} ({self.estado})"

    @property
    def esta_vigente(self):
        """Verifica si la promo se puede usar hoy"""
        return self.estado == 'ACTIVA' and timezone.now() <= self.fecha_vencimiento

#AUDITORIAAAAAAA

class Auditoria(models.Model):
    ACCIONES = (
        ('CREAR', 'Creación'),
        ('EDITAR', 'Edición'),
        ('ELIMINAR', 'Eliminación'),
        ('LOGIN', 'Inicio de Sesión'),
        ('LOGOUT', 'Cierre de Sesión'),
        ('ANULAR_VENTA', 'Anulación de Venta'),
        ('AJUSTE_STOCK', 'Ajuste de Stock'),
        ('APERTURA_CAJA', 'Apertura de Caja'),
        ('CIERRE_CAJA', 'Cierre de Caja'),
        ('INGRESO_MANUAL', 'Ingreso a Caja'),
        ('EGRESO_MANUAL', 'Egreso de Caja'),
    )

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    modelo_afectado = models.CharField(max_length=100) # Ej: Turno, Producto
    objeto_id = models.CharField(max_length=100, null=True, blank=True)
    accion = models.CharField(max_length=20, choices=ACCIONES)
    detalles = models.JSONField(default=dict) # Aquí guardamos el {antes: x, despues: y}
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Registro de Auditoría"

    def __str__(self):
        return f"{self.usuario} - {self.accion} {self.modelo_afectado} - {self.fecha}"

#Para recuperar la contraseña del usuario desde el login
class PasswordResetToken(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32) # Genera token seguro
        super().save(*args, **kwargs)

    @property
    def es_valido(self):
        # El token dura 1 hora (60 minutos)
        expira = self.creado_en + timedelta(hours=1)
        return timezone.now() < expira and not self.usado

#LIQUIDACION DE SUELDOS
class Liquidacion(models.Model):
    empleado = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='liquidaciones')
    fecha_pago = models.DateTimeField(auto_now_add=True)
    fecha_inicio_periodo = models.DateField()
    fecha_fin_periodo = models.DateField()
    
    monto_comisiones = models.DecimalField(max_digits=10, decimal_places=2)
    monto_sueldo_fijo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    
    observaciones = models.TextField(blank=True, null=True)

    # Relación opcional con los turnos pagados para trazabilidad exacta
    turnos_pagados = models.ManyToManyField(Turno, blank=True)

    class Meta:
        db_table = "liquidaciones"
        ordering = ['-fecha_pago']

    def __str__(self):
        return f"Pago a {self.empleado} - ${self.total_pagado} ({self.fecha_pago.date()})"

class ConfiguracionSistema(models.Model):
    razon_social = models.CharField(max_length=255, default="Los Últimos Serán Los Primeros")
    cuil_cuit = models.CharField(max_length=20, default="27-23456789-3") 
    inicio_actividad = models.DateField(null=True, blank=True)
    direccion = models.CharField(max_length=255, default="Avenida Libertador 600, San Vicente - Misiones")
    telefono = models.CharField(max_length=50, default="3755-72716")
    email = models.EmailField(default="contacto@hairsoft.com")
    logo = models.ImageField(upload_to='config/', null=True, blank=True)
    
    margen_horas_cancelacion = models.PositiveIntegerField(default=3) 
    
    # 🔥 NUEVO CAMPO: Descuento para Lista de Espera (Reoferta)
    porcentaje_descuento_reoferta = models.PositiveIntegerField(default=15, help_text="Descuento para turnos liberados (Lista de espera)")
    
    dias_inactividad_clientes = models.PositiveIntegerField(default=60, help_text="Días sin venir para considerar al cliente inactivo y enviarle promo.")
    
    # Este ya lo teníamos para Reactivaciones
    porcentaje_descuento_promo = models.PositiveIntegerField(default=15, help_text="Porcentaje de descuento para enviar a clientes inactivos")
    
    politica_senia = models.TextField(default="Política de señas: Reembolso total si cancelas con tiempo.")
    costo_envio_moto = models.DecimalField(max_digits=10, decimal_places=2, default=1500.00)
    
    class Meta:
        verbose_name = "Configuración del Sistema"

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class NotaCredito(models.Model):
    venta = models.OneToOneField(
        'Venta', 
        on_delete=models.CASCADE, 
        related_name='nota_credito',
        help_text="Venta que fue anulada."
    )
    usuario = models.ForeignKey(
        'Usuario', 
        on_delete=models.PROTECT, 
        help_text="Usuario/Admin que ejecutó la anulación."
    )
    motivo = models.TextField(help_text="Motivo por el cual se anuló la venta.")
    monto_devuelto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Nota de Crédito #{self.id} - Venta {self.venta.id}"

    class Meta:
        db_table = "notas_credito"
        ordering = ['-fecha']
        verbose_name = "Nota de Crédito"
        verbose_name_plural = "Notas de Crédito"

class HistorialStock(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='historial_movimientos')
    cantidad_anterior = models.IntegerField()
    cantidad_nueva = models.IntegerField()
    motivo = models.TextField()
    usuario = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    tipo_ajuste = models.CharField(max_length=50, default='AJUSTE_MANUAL') 

    class Meta:
        db_table = "historial_stock"
        ordering = ['-fecha']

    def diferencia(self):
        return self.cantidad_nueva - self.cantidad_anterior

# --- MÓDULO DE CAJAS ---
class Caja(models.Model):
    nombre = models.CharField(max_length=50, unique=True, help_text="Ej: Caja Principal, Caja Mostrador")
    activa = models.BooleanField(default=True, help_text="Si es False, la caja está inhabilitada")
    motivo_inactividad = models.TextField(blank=True, null=True, help_text="Razón si se deshabilita la caja")
    
    def __str__(self):
        return f"{self.nombre} - {'Activa' if self.activa else 'Inactiva'}"

class SesionCaja(models.Model):
    caja = models.ForeignKey(Caja, on_delete=models.PROTECT, related_name='sesiones')
    usuario_apertura = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='cajas_abiertas')
    usuario_cierre = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='cajas_cerradas', null=True, blank=True)
    
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    
    saldo_inicial_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # 🔥 NUEVO CAMPO: Para guardar el fondo inicial de Mercado Pago
    saldo_inicial_mp = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Saldos reales (lo que el recepcionista cuenta y declara al cerrar)
    saldo_final_efectivo_real = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    saldo_final_mp_real = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    saldo_final_transf_real = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    observaciones = models.TextField(blank=True, null=True)

    @property
    def esta_abierta(self):
        return self.fecha_cierre is None

    def __str__(self):
        estado = "Abierta" if self.esta_abierta else "Cerrada"
        return f"Sesión {self.id} | {self.caja.nombre} ({estado})"


class MovimientoCaja(models.Model):
    TIPO_CHOICES = [
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso'),
    ]
    
    METODO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('MERCADO_PAGO', 'Mercado Pago'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]

    CONCEPTO_CHOICES = [
        # Automáticos / Web
        ('TURNO_PRESENCIAL', 'Cobro de Turno Presencial'),
        ('TURNO_WEB', 'Cobro de Turno Web'),
        ('VENTA', 'Venta de Productos'),
        ('PEDIDO_WEB', 'Pedido Web'),
        # Egresos Manuales
        ('PAGO_PROVEEDOR', 'Pago a Proveedor'),
        ('LIQUIDACION_SUELDO', 'Liquidación de Sueldos'),
        ('GASTO_OPERATIVO', 'Gasto Operativo (Yerba, etc)'),
        ('RETIRO_SOCIO', 'Retiro de Socio/Dueño'),
        # Ingresos Manuales 
        ('FONDO_CAJA', 'Fondo de Caja (Sencillo)'),
        ('APORTE_SOCIO', 'Aporte del Dueño'),
        ('COBRO_DEUDA', 'Cobro de Deuda'),
        ('AJUSTE_SOBRANTE', 'Ajuste por Sobrante de Caja'),
        ('OTROS', 'Otros / Ajustes'),
    ]

    sesion_caja = models.ForeignKey(SesionCaja, on_delete=models.PROTECT, related_name='movimientos', null=True, blank=True)
    
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    metodo_pago = models.CharField(max_length=20, choices=METODO_CHOICES)
    concepto = models.CharField(max_length=30, choices=CONCEPTO_CHOICES)
    
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.CharField(max_length=255, blank=True, null=True, help_text="Detalle extra del gasto o ingreso")
    fecha = models.DateTimeField(auto_now_add=True)
    
    turno_relacionado = models.ForeignKey('Turno', on_delete=models.SET_NULL, null=True, blank=True)
    venta_relacionada = models.ForeignKey('Venta', on_delete=models.SET_NULL, null=True, blank=True)
    pedido_proveedor_relacionado = models.ForeignKey('Pedido', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        estado = "Pendiente" if not self.sesion_caja else f"Caja {self.sesion_caja.id}"
        return f"{self.tipo} | {self.get_concepto_display()} | ${self.monto} ({estado})"