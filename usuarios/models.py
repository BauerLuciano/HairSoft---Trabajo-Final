# hairsoft/models.py
from django.db import models
from datetime import timedelta


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
# CATEGORÍAS (Definidas antes de los que las usan)
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
# USUARIOS
# ===============================
class Usuario(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    dni = models.CharField(max_length=20, unique=True)
    contrasena = models.CharField(max_length=128)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(unique=True)
    
    # 🛑 ATRIBUTOS DE CLASE OBLIGATORIOS para AUTH_USER_MODEL
    # (Solucionan REQUIRED_FIELDS y otros chequeos de Django)
    USERNAME_FIELD = 'correo' 
    REQUIRED_FIELDS = ['nombre', 'apellido', 'dni'] 
    is_admin = False # Asume el rol de admin/staff lo manejan las propiedades
    
    # Referencia a Rol 
    rol = models.ForeignKey('Rol', on_delete=models.SET_NULL, null=True) 
    estado = models.CharField(max_length=15, default='ACTIVO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # 🛑 PROPIEDADES DE COMPATIBILIDAD CON DJANGO/DRF 🛑
    # (Solucionan is_active, is_authenticated y is_anonymous)
    @property
    def is_active(self):
        return self.estado == 'ACTIVO'

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        """Necesario para pasar el chequeo de Django."""
        return False

    @property
    def is_staff(self):
        # Usado para acceso al Admin o verificación de personal
        if self.rol:
            return self.rol.nombre in ['ADMINISTRADOR', 'PELUQUERO']
        return False
    
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
    # 🛑 CORRECCIÓN: Referencia a la clase CategoriaServicio (ya definida arriba)
    categoria = models.ForeignKey(CategoriaServicio, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "servicios"

# ===============================
# PROVEEDORES
# ===============================

# AGREGAR ESTO ANTES DEL MODELO Proveedor
ESTADOS = [
    ('ACTIVO', 'Activo'),
    ('INACTIVO', 'Inactivo'),
]

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    productos_que_ofrece = models.TextField(blank=True, null=True)  # Hacer opcional
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # NUEVO: Relación muchos a muchos con categorías
    categorias = models.ManyToManyField('CategoriaProducto', blank=True)
    
    # NUEVO: Campo para productos específicos
    productos_especificos = models.TextField(blank=True, null=True)


# ===============================
# PRODUCTOS
# ===============================

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, blank=True, null=True)  # Agregar este campo
    descripcion = models.TextField(blank=True, null=True)  # Agregar este campo
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    stock_actual = models.PositiveIntegerField(default=0)  # Cambiar de 'stock' a 'stock_actual'
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE, null=True, blank=True)
    
    # 🆕 AGREGAR RELACIÓN CON PROVEEDOR
    proveedores = models.ManyToManyField(Proveedor, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "productos"


# ===============================
# TURNOS - MODELO CORREGIDO
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
    
    # Relaciones
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="turnos_cliente")
    peluquero = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="turnos_peluquero")
    servicios = models.ManyToManyField(Servicio, db_table="turnos_servicios")

    # Auditoría
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
        
        return (self.estado in ['RESERVADO', 'CONFIRMADO'] and 
                ahora < tres_horas_antes)

    def puede_ser_cancelado(self):
        from django.utils import timezone
        ahora = timezone.now()
        fecha_turno = timezone.make_aware(
            timezone.datetime.combine(self.fecha, self.hora)
        )
        tres_horas_antes = fecha_turno - timedelta(hours=3)
        
        puede_cancelar = (self.estado in ['RESERVADO', 'CONFIRMADO'] and 
                          ahora < tres_horas_antes)
        
        hay_reembolso = puede_cancelar
        
        return puede_cancelar, hay_reembolso

    def calcular_duracion_total(self):
        return sum(servicio.duracion for servicio in self.servicios.all())
    
    def necesita_pago_mp(self):
        return self.medio_pago == 'MERCADO_PAGO'

    class Meta:
        db_table = "turnos"
        ordering = ['fecha', 'hora']

