from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Turno(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="turnos")
    fecha = models.DateField()
    hora = models.TimeField()
    servicio = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.usuario.nombre} - {self.fecha} {self.hora}"
