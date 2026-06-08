import pytest
from datetime import date, time
from usuarios.factories import UsuarioFactory, ServicioFactory
from usuarios.models import Turno, Venta, DetalleVenta


@pytest.mark.django_db
def test_crear_venta_al_completar_turno():
    cliente = UsuarioFactory(rol__nombre='Cliente')
    peluquero = UsuarioFactory(rol__nombre='Peluquero')
    srv_a = ServicioFactory(precio=1000, duracion=30)
    srv_b = ServicioFactory(precio=500, duracion=30)

    turno = Turno.objects.create(
        fecha=date(2026, 6, 15),
        hora=time(14, 0),
        peluquero=peluquero,
        cliente=cliente,
        estado='RESERVADO',
        tipo_pago='TOTAL',
        monto_total=1500,
        medio_pago='EFECTIVO',
    )
    turno.servicios.set([srv_a, srv_b])

    turno.crear_venta_turno()

    venta = Venta.objects.get(tipo='TURNO')
    assert venta.cliente == cliente
    assert venta.usuario == peluquero
    assert venta.total == 1500
    assert venta.medio_pago.tipo == 'EFECTIVO'

    detalles = DetalleVenta.objects.filter(venta=venta).order_by('precio_unitario')
    assert detalles.count() == 2
    assert detalles[0].precio_unitario == 500
    assert detalles[1].precio_unitario == 1000