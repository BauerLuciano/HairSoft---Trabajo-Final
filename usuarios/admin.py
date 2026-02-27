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
    list_display = ('cliente', 'codigo', 'fecha_creacion', 'fecha_vencimiento', 'estado') 
    list_filter = ('estado', 'fecha_creacion') 
    search_fields = ('cliente__nombre', 'cliente__apellido', 'cliente__email', 'codigo')
    actions = [limpiar_historial_promociones]

@admin.register(Silla)
class SillaAdmin(NoLogAdmin): # Le agregué el NoLogAdmin acá también por consistencia
    list_display = ('nombre', 'orden', 'activa')
    list_editable = ('orden', 'activa')
    ordering = ('orden',)

# =========================================================
# REGISTRO AUTOMÁTICO DEL RESTO DE MODELOS
# =========================================================

# ✅ Acá agregué TODOS los modelos que faltaban
MODELOS = [
    # Usuarios y Permisos
    Usuario, Rol, Permiso, PasswordResetToken,
    
    # Catálogos (Productos, Servicios, Proveedores)
    CategoriaServicio, CategoriaProducto, Servicio, 
    Marca, Producto, Proveedor, ListaPrecioProveedor, HistorialPrecios,
    
    # Turnos y Ofertas
    Turno, InteresTurnoLiberado, ConfiguracionReoferta,
    
    # Finanzas y Ventas
    Venta, DetalleVenta, MetodoPago, NotaCredito, Liquidacion,
    
    # Pedidos Locales e Inteligentes
    Pedido, DetallePedido, SolicitudReabastecimiento, CotizacionProveedor, 
    SolicitudPresupuesto, Cotizacion,
    
    # Pedidos Web
    PedidoWeb, DetallePedidoWeb,
    
    # Auditoría y Sistema
    Auditoria, HistorialStock, ConfiguracionSistema
]

for modelo in MODELOS:
    if not admin.site.is_registered(modelo):
        admin.site.register(modelo, NoLogAdmin)