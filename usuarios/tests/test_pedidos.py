import pytest
import time # <--- Importante para esperar al hilo
from rest_framework.test import APIClient
from usuarios.factories import ProductoFactory

# ✅ Agregamos (transaction=True) para que el hilo pueda ver los datos en la DB
@pytest.mark.django_db(transaction=True)
def test_generar_solicitud_presupuesto_stock_bajo():
    from usuarios.models import SolicitudPresupuesto
    
    # 1. Creamos un producto con stock bajo (Stock 2 < Minimo 5)
    # Al crearse, tu modelo ya dispara el hilo automáticamente
    producto = ProductoFactory(
        nombre="Tinta Premium", 
        stock_actual=2, 
        stock_minimo=5, 
        lote_reposicion=10
    )
    
    print(f"\n⏳ Esperando que el hilo de HairSoft procese la alerta...")
    
    # 2. IMPORTANTE: Tu hilo tiene un time.sleep(1). 
    # Le damos 2 segundos al test para que el hilo termine de crear la solicitud.
    time.sleep(2)
    
    # 3. Verificamos que la solicitud se haya creado
    solicitud = SolicitudPresupuesto.objects.filter(producto=producto, estado='PENDIENTE').first()
    
    assert solicitud is not None
    assert solicitud.cantidad_requerida == 10
    print(f"\n✅ CP-PED-001: Solicitud generada para {producto.nombre}")