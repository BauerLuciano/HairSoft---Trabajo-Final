# hairsoft/models.py
from django.db import models
from datetime import timedelta

class Usuario(models.Model):
    ROLES = [
        ('ADMIN', 'Administrador'),
        ('RECEP', 'Recepcionista'),
        ('PEL', 'Peluquero'),
        ('CLI', 'Cliente'),
    ]

    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    dni = models.CharField(max_length=20, unique=True)
    contrasena = models.CharField(max_length=128)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(unique=True)
    rol = models.CharField(max_length=6, choices=ROLES)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rol})"


class Categoria(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    nombre = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.nombre



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
    servicios = models.ManyToManyField(Servicio)

    def __str__(self):
        return f"{self.fecha} {self.hora} - {self.cliente.nombre} ({self.estado})"
