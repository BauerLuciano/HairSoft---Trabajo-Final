# usuarios/admin.py
from django.contrib import admin
from .models import *

# Clase base para desactivar logs (esto ya lo tenías)
class NoLogAdmin(admin.ModelAdmin):
    def log_addition(self, request, object, message):
        return
    def log_change(self, request, object, message):
        return
    def log_deletion(self, request, object, object_repr):
        return

# =========================================================
# CONFIGURACIÓN ESPECIAL PARA PROMOCIONES (Con Botón de Limpieza)
# =========================================================

@admin.action(description="⚠️ BORRAR TODAS las promociones (Limpiar Pruebas)")
def limpiar_historial_promociones(modeladmin, request, queryset):
    # Borra TODO el historial, no solo lo seleccionado en el checkbox
    count = PromocionReactivacion.objects.all().count()
    if count > 0:
        PromocionReactivacion.objects.all().delete()
        modeladmin.message_user(request, f"✅ Se eliminaron {count} promociones. Historial limpio.")
    else:
        modeladmin.message_user(request, "⚠️ No hay promociones para borrar.", level='warning')

@admin.register(PromocionReactivacion)
class PromocionReactivacionAdmin(NoLogAdmin):
    # ✅ CORREGIDO: Usamos 'fecha_creacion' y sacamos 'usada' que no existe
    list_display = ('cliente', 'codigo', 'fecha_creacion', 'fecha_vencimiento', 'estado') 
    
    # ✅ CORREGIDO: Filtros con campos reales
    list_filter = ('estado', 'fecha_creacion') 
    
    search_fields = ('cliente__nombre', 'cliente__apellido', 'cliente__email', 'codigo')
    
    # Agregamos el botón de acción
    actions = [limpiar_historial_promociones]

# =========================================================
# REGISTRO AUTOMÁTICO DEL RESTO DE MODELOS
# =========================================================

MODELOS = [
    Usuario, Rol, Permiso, Servicio, Producto,
    Turno, Venta, DetalleVenta, MetodoPago, Proveedor,
    Pedido, DetallePedido, InteresTurnoLiberado
]

for modelo in MODELOS:
    if not admin.site.is_registered(modelo):
        admin.site.register(modelo, NoLogAdmin)