# usuarios/admin.py
from django.contrib import admin
from .models import *

# Clase base para desactivar logs
class NoLogAdmin(admin.ModelAdmin):
    def log_addition(self, request, object, message):
        return
    
    def log_change(self, request, object, message):
        return
    
    def log_deletion(self, request, object, object_repr):
        return

# Lista de todos los modelos a registrar
MODELOS = [
    Usuario, Rol, Permiso, Servicio, Producto, 
    Turno, Venta, DetalleVenta, MetodoPago, Proveedor,
    Pedido, DetallePedido  # ✅ AGREGADOS
]

# Registrar todos los modelos automáticamente
for modelo in MODELOS:
    admin.site.register(modelo, NoLogAdmin)