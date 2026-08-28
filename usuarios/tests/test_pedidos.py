import pytest
from usuarios.factories import ProductoFactory
from usuarios.models import SolicitudPresupuesto, ListaPrecioProveedor, Proveedor


@pytest.mark.django_db(transaction=True)
def test_generar_solicitud_presupuesto_stock_bajo(monkeypatch):
    from usuarios.tasks import procesar_alertas_stock_proveedores

    # Evitamos envío de mails y pausas reales dentro de la tarea
    monkeypatch.setattr("usuarios.tasks.send_mail", lambda *a, **k: None)
    monkeypatch.setattr("usuarios.tasks.time.sleep", lambda *a, **k: None)

    proveedor = Proveedor.objects.create(
        nombre="Proveedor CP-PED-001",
        cuit="30999999991",
        telefono="12345678",
        email="cp-ped-001@test.com",
        estado="ACTIVO",
    )

    # 1. Creamos un producto con stock bajo (Stock 2 < Minimo 5)
    producto = ProductoFactory(
        nombre="Tinta Premium",
        stock_actual=2,
        stock_minimo=5,
        lote_reposicion=10,
    )

    # La reposición se dispara por la tarea unificada con la fuente única de listas activas
    ListaPrecioProveedor.objects.create(
        producto=producto,
        proveedor=proveedor,
        precio_base=1000.0,
        margen_ganancia=30.0,
        activo=True,
    )

    # 2. Ejecutamos la lógica de reposición por producto
    procesar_alertas_stock_proveedores.run(producto.id)

    # 3. Verificamos que la solicitud se haya creado
    solicitud = SolicitudPresupuesto.objects.filter(producto=producto, estado='PENDIENTE').first()

    assert solicitud is not None
    assert solicitud.cantidad_requerida == 10
