# hairsoft/models.py
from django.db import models, transaction
from datetime import timedelta, datetime
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.mail import get_connection, EmailMessage
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid
import secrets, time, threading
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
    telefono = models.CharField(max_length=20)
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

    sueldo_fijo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Sueldo Fijo Mensual",
        help_text="Usar solo para empleados con fijo (ej. Recepción)"
    )

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
    ESTADOS = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    )
    
    nombre = models.CharField(max_length=100)
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
    
    nombre = models.CharField(max_length=255)
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
        if self.categoria and not self.codigo:
            self.generar_codigo()
        
        self.clean()
        super().save(*args, **kwargs)

        print(f"🔄 GUARDANDO: {self.nombre} | Stock: {self.stock_actual}")

        # DISPARADOR DE CORREOS HTML PREMIUM (EN SEGUNDO PLANO)
        # Esto evita el 'Broken Pipe' de Mercado Pago manteniendo tu lógica intacta.
        if self.estado == 'ACTIVO' and self.stock_actual <= self.stock_minimo:
            
            def enviar_alertas_background():
                print("   ⚠️ ALERTA DE STOCK. Iniciando hilo de correos...")
                try:
                    # Imports locales para el hilo
                    from .models import SolicitudPresupuesto, Cotizacion
                    from django.core.mail import send_mail
                    from django.conf import settings
                    from django.utils import timezone
                    import secrets
                    import time
                    
                    # Pequeña pausa inicial para que la transacción DB termine
                    time.sleep(1)

                    fecha_hoy = timezone.now().strftime("%d/%m/%Y")
                    
                    solicitud = SolicitudPresupuesto.objects.create(
                        producto=self,
                        cantidad_requerida=self.lote_reposicion,
                        estado='PENDIENTE'
                    )
                    
                    for proveedor in self.proveedores.all():
                        cotizacion = Cotizacion.objects.create(
                            solicitud=solicitud,
                            proveedor=proveedor,
                            token=secrets.token_urlsafe(32)
                        )
                        
                        if proveedor.email:
                            link = f"http://localhost:5173/proveedor/cotizar/{cotizacion.token}"
                            asunto = f"📦 Nueva Solicitud de Compra #{solicitud.id}"
                            
                            # --- TU HTML ORIGINAL (INTACTO) ---
                            mensaje_html = f"""
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <style>
                                    .btn-hover:hover {{ background-color: #218838 !important; }}
                                </style>
                            </head>
                            <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 40px 0;">
                                
                                <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
                                    
                                    <div style="background: linear-gradient(135deg, #007bff 0%, #6610f2 100%); padding: 40px 30px; text-align: center;">
                                        <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700; letter-spacing: 0.5px;">SOLICITUD DE COMPRA</h1>
                                        <p style="color: rgba(255,255,255,0.8); margin: 10px 0 0; font-size: 14px; font-weight: 500;">
                                            Los Ultimos Serán Los Primeros • {fecha_hoy}
                                        </p>
                                    </div>

                                    <div style="padding: 40px 30px;">
                                        <p style="font-size: 16px; color: #4a4a4a; line-height: 1.6; margin-bottom: 30px;">
                                            Hola!☺️ <strong>{proveedor.nombre}</strong>,<br>
                                            Estamos sin stock de este producto y necesitamos reponerlo con urgencia
                                        </p>
                                        
                                        <div style="background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 12px; padding: 25px; margin-bottom: 30px; position: relative;">
                                            
                                            <div style="position: absolute; top: -10px; right: 20px; background-color: #dc3545; color: white; font-size: 10px; font-weight: bold; padding: 4px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px;">
                                                Stock Bajo
                                            </div>

                                            <table style="width: 100%; border-collapse: collapse;">
                                                <tr>
                                                    <td>
                                                        <p style="margin: 0; color: #888; font-size: 12px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">PRODUCTO</p>
                                                        <p style="margin: 5px 0 15px; color: #2d3436; font-size: 18px; font-weight: 700;">{self.nombre}</p>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td>
                                                        <p style="margin: 0; color: #888; font-size: 12px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">CANTIDAD A COTIZAR</p>
                                                        <p style="margin: 5px 0 0; color: #2d3436; font-size: 22px; font-weight: 700; color: #007bff;">{solicitud.cantidad_requerida} u.</p>
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>

                                        <div style="text-align: center; margin-bottom: 30px;">
                                            <a href="{link}" 
                                            style="background-color: #28a745; color: #ffffff; padding: 18px 40px; text-decoration: none; border-radius: 50px; font-weight: 700; font-size: 16px; display: inline-block; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);">
                                                Enviar Presupuesto 
                                            </a>
                                        </div>
                                        
                                        <p style="font-size: 13px; color: #999; text-align: center; margin: 0;">
                                            ¿Problemas con el botón? <a href="{link}" style="color: #007bff; text-decoration: none;">Clic aquí</a>
                                        </p>
                                    </div>

                                    <div style="background-color: #f8f9fa; padding: 25px; text-align: center; border-top: 1px solid #e9ecef;">
                                        <p style="margin: 0; color: #adb5bd; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                                            Los Últimos Serán Los Primeros
                                        </p>
                                        <p style="margin: 8px 0 0; color: #ced4da; font-size: 11px;">
                                            Sistema Automatizado de Gestión
                                        </p>
                                    </div>
                                </div>
                                
                                <div style="text-align: center; padding-top: 20px; color: #999; font-size: 11px;">
                                    © {timezone.now().year} HairSoft - Todos los derechos reservados.
                                </div>

                            </body>
                            </html>
                            """
                            
                            mensaje_texto = f"Hola {proveedor.nombre}, necesitamos {solicitud.cantidad_requerida} de {self.nombre}. Link: {link}"

                            print(f"   📤 [HILO] Enviando HTML Premium a: {proveedor.email}...")
                            
                            try:
                                send_mail(
                                    subject=asunto,
                                    message=mensaje_texto, 
                                    from_email=settings.DEFAULT_FROM_EMAIL,
                                    recipient_list=[proveedor.email],
                                    fail_silently=False,
                                    html_message=mensaje_html 
                                )
                                print(f"   ✅ [HILO] EMAIL ENVIADO OK")
                                print("   ⏳ [HILO] Esperando 10s para el próximo (pausa Mailtrap)...")
                                time.sleep(10) # 🛑 TU PAUSA DE SEGURIDAD (AHORA EN HILO)
                            except Exception as e:
                                print(f"   ❌ [HILO] ERROR ENVIANDO: {e}")
                    
                    print(f"📦 [HILO] Proceso finalizado.")
                except Exception as ex_hilo:
                    print(f"⚠️ Error en hilo de alertas: {ex_hilo}")

            # LANZAMIENTO DEL HILO
            hilo = threading.Thread(target=enviar_alertas_background)
            hilo.start()

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
    
    # EL SECRETO: Token único para que entre sin loguearse
    token_acceso = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Datos que completa el proveedor
    precio_ofrecido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dias_entrega = models.PositiveIntegerField(null=True, blank=True, help_text="Días hábiles para entregar")
    comentarios = models.TextField(blank=True, null=True)
    
    respondió = models.BooleanField(default=False)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)

    # Lógica Inteligente: Calcular cuál es mejor
    @property
    def puntaje_sistema(self):
        if not self.precio_ofrecido or not self.dias_entrega:
            return 0
        # Ejemplo de algoritmo: Menor precio suma más, menor tiempo suma más.
        # Esto es simple, se puede complicar todo lo que quieras.
        # Asumimos peso: 70% precio, 30% tiempo. (Valores inversos porque menor es mejor)
        score_precio = 10000 / float(self.precio_ofrecido) 
        score_tiempo = 100 / float(self.dias_entrega)
        return (score_precio * 0.7) + (score_tiempo * 0.3)


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
        ('MERCADO_PAGO', 'Mercado Pago (Web) '),
        ('TRANSFERENCIA', 'Transferencia'),
        ('TARJETA', 'Tarjeta de Crédito/Débito'),
        ('PENDIENTE', 'Pendiente'),
    ]

    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='RESERVADO')
    canal = models.CharField(max_length=15, choices=CANAL_CHOICES, default='PRESENCIAL')
    tipo_pago = models.CharField(max_length=15, choices=TIPO_PAGO_CHOICES, default='PENDIENTE')
    medio_pago = models.CharField(max_length=20, choices=MEDIO_PAGO_CHOICES, default='PENDIENTE')
    monto_seña = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    monto_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    duracion_total = models.IntegerField(default=0, help_text="Duración total en minutos")
    reembolsado = models.BooleanField(default=False)
    mp_payment_id = models.CharField(max_length=50, blank=True, null=True)
    
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

    # 💰 MONTO DE COMISIÓN "CONGELADO"
    monto_comision = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.fecha} {self.hora} - {self.cliente.nombre} ({self.estado})"

    def puede_ser_modificado(self):
        ahora = timezone.now()
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

    # --- MÉTODOS DE REOFERTA ---
    def puede_reofertar(self):
        if self.estado != 'CANCELADO': return False
        fecha_turno_naive = datetime.combine(self.fecha, self.hora)
        fecha_turno = timezone.make_aware(fecha_turno_naive)
        tiempo_restante = fecha_turno - timezone.now()
        return tiempo_restante > timedelta(minutes=5) and not self.oferta_activa
    
    def obtener_interesados(self):
        print(f"🔍🔍🔍 BUSCANDO INTERESADOS PARA TURNO {self.id}:")
        from django.apps import apps
        InteresTurnoLiberado = apps.get_model('usuarios', 'InteresTurnoLiberado')
        
        interesados = InteresTurnoLiberado.objects.filter(
            fecha_deseada=self.fecha,
            hora_deseada=self.hora,
            peluquero=self.peluquero,
            estado_oferta='pendiente'
        ).order_by('fecha_registro')
        return interesados
        
    def iniciar_reoferta(self):
        from .tasks import procesar_reoferta_masiva
        if self.puede_reofertar():
            self.oferta_activa = True
            fecha_turno_naive = datetime.combine(self.fecha, self.hora)
            fecha_turno = timezone.make_aware(fecha_turno_naive)
            self.fecha_expiracion_oferta = fecha_turno - timedelta(minutes=5)
            self.token_reoferta = secrets.token_urlsafe(32)
            self.save()
            procesar_reoferta_masiva.delay(self.id)
            return True
        return False

    # --- MÉTODOS DE CÁLCULO DE COMISIÓN ---
    def calcular_comision_peluquero(self):
        """Calcula la suma de comisiones de todos los servicios del turno."""
        total_comision = 0
        for s in self.servicios.all():
            # Usamos getattr por seguridad si la migración no impactó aún
            porcentaje = getattr(s, 'porcentaje_comision', 0)
            if porcentaje > 0:
                ganancia = float(s.precio) * (float(porcentaje) / 100)
                total_comision += ganancia
        return round(total_comision, 2)

    def save(self, *args, **kwargs):
        crear_venta = False
        calcular_pago = False

        if self.pk:
            try:
                old = Turno.objects.get(pk=self.pk)
                if old.estado != 'COMPLETADO' and self.estado == 'COMPLETADO':
                    crear_venta = True
                    calcular_pago = True
            except Turno.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Calculamos pago DESPUÉS de guardar (M2M services necesitan ID)
        if calcular_pago:
            self.monto_comision = self.calcular_comision_peluquero()
            # Update directo para evitar recursión
            Turno.objects.filter(pk=self.pk).update(monto_comision=self.monto_comision)

        if crear_venta:
            self.crear_venta_turno()

    @transaction.atomic
    def crear_venta_turno(self):
        # Evitamos importaciones circulares
        from django.apps import apps
        from django.db import IntegrityError # Importante para manejar el error si ocurre
        
        MetodoPago = apps.get_model('usuarios', 'MetodoPago')
        Venta = apps.get_model('usuarios', 'Venta')
        DetalleVenta = apps.get_model('usuarios', 'DetalleVenta')

        total_servicios = sum(servicio.precio for servicio in self.servicios.all())
        
        # 1. Definir el Nombre Real y el Tipo ANTES de buscar
        # Esto soluciona el error: buscamos exactamente por lo que vamos a guardar
        mp_str = str(self.medio_pago).upper()
        
        nombre_real = 'Efectivo'
        tipo_real = 'EFECTIVO'

        if 'MERCADO' in mp_str or 'MP' in mp_str:
            nombre_real = 'Mercado Pago'
            tipo_real = 'MERCADO_PAGO'
        elif 'TARJETA' in mp_str:
            nombre_real = 'Tarjeta'
            tipo_real = 'TARJETA'
        elif 'TRANSFERENCIA' in mp_str:
            nombre_real = 'Transferencia'
            tipo_real = 'TRANSFERENCIA'
        
        # 2. Buscar o Crear BLINDADO
        try:
            # Buscamos por el nombre bonito ('Mercado Pago'), no por el código ('MERCADO_PAGO')
            medio_pago_obj, created = MetodoPago.objects.get_or_create(
                nombre__iexact=nombre_real, 
                defaults={
                    'nombre': nombre_real,
                    'tipo': tipo_real,
                    'activo': True
                }
            )
        except IntegrityError:
            # Si justo hubo una condición de carrera o falló el unique, lo traemos directo
            medio_pago_obj = MetodoPago.objects.filter(nombre__iexact=nombre_real).first()
            
            # Si aun así falla (caso extremo), usamos Efectivo por defecto para no romper el turno
            if not medio_pago_obj:
                medio_pago_obj, _ = MetodoPago.objects.get_or_create(
                    nombre='Efectivo', defaults={'tipo': 'EFECTIVO'}
                )

        # 3. Crear la Venta
        venta = Venta.objects.create(
            cliente=self.cliente,
            usuario=self.peluquero, # O el usuario logueado si se pasara, pero usamos peluquero como fallback
            total=total_servicios,
            tipo='TURNO',
            medio_pago=medio_pago_obj
        )
        
        # 4. Crear Detalles
        for servicio in self.servicios.all():
            DetalleVenta.objects.create(
                venta=venta,
                servicio=servicio,
                turno=self,
                cantidad=1,
                precio_unitario=servicio.precio,
                subtotal=servicio.precio
            )
            
        # Actualizar total final de la venta
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
    # Identificador único para el link externo del proveedor
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Definimos los estados posibles
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),               # Creado por vos, borrador
        ('ENVIADO', 'Enviado a Proveedor'),       # Se mandó el mail con el link
        ('CONFIRMADO', 'Confirmado por Proveedor'), # El proveedor dio el OK (o vos manual)
        ('ENTREGADO', 'Recibido en Local'),       # Llegó la caja (Stock + Precio impactado)
        ('CANCELADO', 'Cancelado')
    ]

    proveedor = models.ForeignKey(
        'Proveedor', # Usá string si Proveedor está definido más abajo o import circular
        on_delete=models.PROTECT,
        related_name='pedidos'
    )
    
    # Un solo campo estado, con las opciones nuevas
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
        return self.estado in ['PENDIENTE', 'ENVIADO']

    def puede_ser_completado(self):
        """
        Verifica si el pedido puede ser completado (recibido).
        El serializer busca este nombre exacto.
        """
        return self.estado == 'CONFIRMADO'
    
    def puede_ser_cancelado(self):
        return self.estado in ['PENDIENTE', 'ENVIADO', 'CONFIRMADO']

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
        # Este método se reemplaza por la lógica de recibir_pedido en la view
        # pero lo dejamos como helper interno si querés.
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

# Pedidos del cliente via web!
from django.db import models

class PedidoWeb(models.Model):
    # Opciones de Estado del Pedido
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

    # ✅ Campo para trazabilidad de la moto
    datos_entrega_interna = models.CharField(max_length=255, null=True, blank=True, help_text="Nombre del cadete")

    def __str__(self):
        return f"Pedido Web #{self.id} - {self.cliente.username}"

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

# para reportes!

class ConfiguracionSistema(models.Model):
    # Datos Fijos de la Empresa (CORREGIDOS)
    razon_social = models.CharField(max_length=255, default="Los Últimos Serán Los Primeros")
    cuil_cuit = models.CharField(max_length=20, default="27-23456789-3") 
    inicio_actividad = models.DateField(null=True, blank=True)
    # Dirección completa con ciudad
    direccion = models.CharField(max_length=255, default="Avenida Libertador 600, San Vicente - Misiones")
    # Teléfono real
    telefono = models.CharField(max_length=50, default="3755-72716")
    email = models.EmailField(default="contacto@hairsoft.com")

    # Parámetros del Sistema
    margen_horas_cancelacion = models.PositiveIntegerField(default=24)
    politica_senia = models.TextField(default="Política de señas: ...")

    class Meta:
        verbose_name = "Configuración del Sistema"

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj