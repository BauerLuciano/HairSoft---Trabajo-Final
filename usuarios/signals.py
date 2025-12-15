from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from django.db.models import DateTimeField, DateField, ForeignKey, DecimalField
import logging
import time

# IMPORTAMOS TODOS LOS MODELOS QUE QUIERAS AUDITAR
from .models import (
    Turno, ConfiguracionReoferta, Producto, SolicitudPresupuesto, 
    Cotizacion, InteresTurnoLiberado, Auditoria, Usuario, Venta, Pedido, Rol,
    # ✅ NUEVOS AGREGADOS:
    Servicio, Marca, Proveedor, CategoriaProducto, CategoriaServicio, MetodoPago
)
from .middleware import get_current_request_data
from .tasks import procesar_reoferta_masiva, enviar_email_cotizacion_proveedor

logger = logging.getLogger(__name__)

# ... (MANTENÉ TUS LÓGICAS DE REOFERTA, WHATSAPP Y STOCK ACÁ ARRIBA IGUAL QUE ANTES) ...
# ... (Si las borraste, avisame) ...

# ==============================================================================
# 4. MÓDULO DE AUDITORÍA (COMPLETO)
# ==============================================================================

# 🔥 LISTA MAESTRA DE VIGILANCIA
MODELOS_A_AUDITAR = [
    Usuario, Producto, Turno, Venta, Pedido, Rol,
    Servicio, Marca, Proveedor, CategoriaProducto, CategoriaServicio, MetodoPago
]

def serializar_modelo(instance):
    """Convierte datos crudos en datos lindos para humanos."""
    data = {}
    for field in instance._meta.fields:
        nombre_campo = field.name
        if nombre_campo in ['password', 'groups', 'user_permissions', 'is_superuser', 'is_staff', 'last_login', 'date_joined']:
            continue
            
        valor = getattr(instance, nombre_campo)
        
        if valor is None:
            data[nombre_campo] = "-"
            continue

        if isinstance(field, ForeignKey):
            if hasattr(valor, 'nombre'): data[nombre_campo] = valor.nombre
            elif hasattr(valor, '__str__'): data[nombre_campo] = str(valor)
            else: data[nombre_campo] = str(valor)
            
        elif isinstance(field, DateTimeField):
            data[nombre_campo] = timezone.localtime(valor).strftime('%d/%m/%Y %H:%M')
        elif isinstance(field, DateField):
            data[nombre_campo] = valor.strftime('%d/%m/%Y')
        elif hasattr(instance, f'get_{nombre_campo}_display'):
            data[nombre_campo] = getattr(instance, f'get_{nombre_campo}_display')()
        else:
            data[nombre_campo] = str(valor)
            
    return data

@receiver(post_save)
def registrar_auditoria_cambios(sender, instance, created, **kwargs):
    if sender in MODELOS_A_AUDITAR:
        try:
            if sender == Auditoria: return

            accion = 'CREACION' if created else 'MODIFICACION'
            
            # Intentamos obtener el usuario del hilo actual
            request_data = get_current_request_data()
            usuario_db = request_data.get('user')
            
            # Validación extra: Si el middleware falló o es tarea automática, intentamos inferir
            # (Por ejemplo, si la instancia tiene un campo 'usuario_creador', podrías usarlo)
            
            if usuario_db and not usuario_db.is_authenticated:
                usuario_db = None

            datos_legibles = serializar_modelo(instance)

            # Detectamos cambios de estado (ej: Activo -> Inactivo)
            descripcion = f"{accion} de {sender.__name__}"
            if not created and 'estado' in datos_legibles:
                descripcion += f" (Estado: {datos_legibles['estado']})"

            detalles = {
                'descripcion': descripcion,
                'valor': str(instance), 
                'datos': datos_legibles
            }

            Auditoria.objects.create(
                usuario=usuario_db,
                accion=accion,
                modelo=sender.__name__,
                objeto_id=str(instance.pk),
                detalles=detalles,
                ip=request_data.get('ip'),
                navegador=request_data.get('navegador')
            )
        except Exception as e:
            print(f"❌ Error auditoría: {e}")

@receiver(post_delete)
def registrar_auditoria_borrado(sender, instance, **kwargs):
    if sender in MODELOS_A_AUDITAR:
        try:
            request_data = get_current_request_data()
            usuario_db = request_data.get('user')
            if usuario_db and not usuario_db.is_authenticated: usuario_db = None

            Auditoria.objects.create(
                usuario=usuario_db,
                accion='ELIMINACION',
                modelo=sender.__name__,
                objeto_id=str(instance.pk),
                detalles={'info': f"Registro eliminado: {str(instance)}"},
                ip=request_data.get('ip'),
                navegador=request_data.get('navegador')
            )
        except Exception as e:
            print(f"❌ Error auditoría borrado: {e}")