# hairsoft/models.py
from django.db import models
from datetime import timedelta


# ===============================
# USUARIOS
# ===============================
class Usuario(models.Model):
    ROLES = [
        ('ADMINISTRADOR', 'Administrador'),
        ('RECEPCIONISTA', 'Recepcionista'),
        ('PELUQUERO', 'Peluquero'),
        ('CLIENTE', 'Cliente'),
    ]

    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    dni = models.CharField(max_length=20, unique=True)
    contrasena = models.CharField(max_length=128)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=ROLES)
    estado = models.CharField(max_length=15, default='ACTIVO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rol})"

    class Meta:
        db_table = "usuarios"


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
# SERVICIOS Y PRODUCTOS
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


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "productos"


# ===============================
# TURNOS
# ===============================
class Turno(models.Model):
    ESTADOS = [
        ('PEND', 'Pendiente'),
        ('CONF', 'Confirmado'),
        ('CANC', 'Cancelado'),
    ]

    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PEND', editable=False)
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="turnos_cliente")
    peluquero = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="turnos_peluquero")
    servicios = models.ManyToManyField(Servicio, db_table="turnos_servicios")

    def __str__(self):
        return f"{self.fecha} {self.hora} - {self.cliente.nombre} ({self.estado})"

    class Meta:
        db_table = "turnos"
        ordering = ['fecha', 'hora']

# ===============================
# ROLES
# ===============================
# roles/models.py
from django.db import models

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    class Meta:
        db_table = "roles"