import pytest
from usuarios.factories import ProductoFactory, CategoriaProductoFactory, MarcaFactory
from usuarios.models import Proveedor, SolicitudPresupuesto, Cotizacion, ListaPrecioProveedor


@pytest.fixture
def proveedor():
    return Proveedor.objects.create(
        nombre="Proveedor Test Reposicion",
        cuit="30111222333",
        telefono="12345678",
        email="proveedor@test.com",
        estado="ACTIVO",
    )


@pytest.fixture
def producto(proveedor):
    prod = ProductoFactory(
        nombre="Shampoo Anti-Dup",
        stock_actual=2,
        stock_minimo=5,
        lote_reposicion=10,
        categoria=CategoriaProductoFactory(),
        marca=MarcaFactory(),
    )
    # Fuente única de disponibilidad: ListaPrecioProveedor activa
    ListaPrecioProveedor.objects.create(
        producto=prod,
        proveedor=proveedor,
        precio_base=1500.0,
        margen_ganancia=30.0,
        activo=True,
    )
    return prod


@pytest.mark.django_db(transaction=True)
def test_reposicion_no_genera_solicitudes_duplicadas(producto, proveedor, monkeypatch):
    # Evitamos envío de mails y pausas reales dentro de la tarea
    monkeypatch.setattr("usuarios.tasks.send_mail", lambda *a, **k: None)
    monkeypatch.setattr("usuarios.tasks.time.sleep", lambda *a, **k: None)

    from usuarios.tasks import procesar_alertas_stock_proveedores

    # 1ra ejecución: debería CREAR la solicitud + cotización
    procesar_alertas_stock_proveedores.run(producto.id)

    solicitudes = SolicitudPresupuesto.objects.filter(producto=producto)
    assert solicitudes.count() == 1, f"Se esperaba 1 solicitud, hay {solicitudes.count()}"
    solicitud = solicitudes.first()
    assert solicitud.estado == 'PENDIENTE'
    assert Cotizacion.objects.filter(solicitud=solicitud, proveedor=proveedor).count() == 1

    # 2da ejecución (mientras sigue PENDIENTE): NO debe crear nada nuevo
    procesar_alertas_stock_proveedores.run(producto.id)

    assert SolicitudPresupuesto.objects.filter(producto=producto).count() == 1, (
        "Se generó una solicitud duplicada"
    )
    assert Cotizacion.objects.filter(solicitud=solicitud, proveedor=proveedor).count() == 1, (
        "Se generó una cotización duplicada"
    )
